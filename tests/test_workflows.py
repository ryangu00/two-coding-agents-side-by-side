import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from support import ROOT, module, scratch

fanout = module("fanout", "scripts/plan-review/fanout.py")
ledger = module("ledger", "scripts/ledger/ledger_from_reports.py")
schema = module("schema", "scripts/ledger/validate_schema.py")
bulk = module("bulk", "scripts/eval/gen_bulk_eval.py")
http = module("http_fixture", "fixtures/stubs/http_server.py")


class FanoutTests(unittest.TestCase):
    def test_canned_cli_ignores_external_command_and_writes_attempts(self):
        with scratch() as directory:
            output = Path(directory) / "fanout.json"
            env = dict(os.environ, REVIEW_MODELS='["example-model"]',
                       TOOL_REVIEW_COMMAND='["must-not-run"]', PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/plan-review/fanout.py"),
                                     "--prompt", str(ROOT / "prompts/plan-open.md"), "--mock-fixture",
                                     str(ROOT / "fixtures/completions.json"), "--out", str(output)],
                                    env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "FANOUT OK")
            self.assertEqual(len(json.loads(output.read_text())[0]["attempts"]), 2)

    def test_http_request_empty_length_retries_and_records_metrics(self):
        replies = iter(json.loads((ROOT / "fixtures/completions.json").read_text())["example-model"])
        bodies = []

        def urlopen(request, timeout):
            body = json.loads(request.data)
            bodies.append(body)
            wire = http.respond(body, next(replies))
            self.assertTrue(wire.startswith(b"HTTP/1.0 200"))
            return io.BytesIO(wire.split(b"\r\n\r\n", 1)[1])

        with patch.object(fanout.urllib.request, "urlopen", urlopen):
            result = fanout.review_model("example-model", "Synthetic plan", lambda body:
                fanout.request_completion("http://127.0.0.1:4000/v1/chat/completions", "", body))
        self.assertTrue(result["ok"])
        self.assertEqual([body["max_tokens"] for body in bodies], [20000, 60000])
        self.assertIn("Verdict on the first line", bodies[-1]["messages"][0]["content"])
        self.assertEqual(result["attempts"][0]["chars"], 0)
        self.assertEqual(result["attempts"][0]["finish_reason"], "length")
        self.assertEqual(result["attempts"][0]["total_tokens"], 38366)
        self.assertIn("seconds", result["attempts"][-1])

    def test_empty_stop_does_not_trigger_length_retry(self):
        calls = []
        def request(body):
            calls.append(body)
            return {"choices": [{"message": {"content": ""}, "finish_reason": "stop"}]}
        result = fanout.review_model("example-model", "plan", request)
        self.assertFalse(result["ok"])
        self.assertEqual(len(calls), 1)

    def test_exhausted_retry_and_nonempty_truncation_are_incomplete(self):
        for text in ("", "FIX-FIRST"):
            result = fanout.review_model("example-model", "plan", lambda body:
                {"choices": [{"message": {"content": text}, "finish_reason": "length"}]})
            self.assertFalse(result["ok"])
            self.assertEqual(len(result["attempts"]), 2 if not text else 1)

    def test_transport_exception_is_recorded_without_its_text(self):
        def broken(body):
            raise OSError("Do not publish request content")
        result = fanout.review_model("example-model", "plan", broken)
        self.assertFalse(result["ok"])
        self.assertEqual(result["attempts"][0]["error"], "OSError")
        self.assertNotIn("Do not publish", json.dumps(result))

    def test_count_only_structured_executions(self):
        self.assertEqual(fanout.count_executions(ROOT / "fixtures/rollout.synthetic.jsonl"), 2)
        self.assertEqual(fanout.count_executions(ROOT / "fixtures/rollout.unparsed.jsonl"), 0)

    def test_external_reviewer_command_and_structured_log(self):
        with scratch() as directory:
            directory = Path(directory)
            script = directory / "review.py"
            script.write_text(
                "from pathlib import Path\nimport sys\n"
                "Path(sys.argv[2]).write_text('FIX-FIRST\\n')\n"
                "Path(sys.argv[3]).write_text(Path(sys.argv[1]).read_text())\n")
            command = [sys.executable, "-B", str(script), str(ROOT / "fixtures/rollout.synthetic.jsonl"),
                       "{output}", "{log}", "--sandbox", "read-only"]
            result = fanout.tool_review(command, "unused", directory / "review.md", directory / "events.jsonl")
            self.assertTrue(result["ok"])
            self.assertEqual(result["executed_commands"], 2)
            with self.assertRaises(ValueError):
                fanout.tool_review(command, "unused", directory / "review.md", directory / "events.jsonl")

    def test_external_command_requires_sandbox_declaration(self):
        with self.assertRaises(ValueError):
            fanout.tool_review(["example"], "prompt", "output", "log")


class LedgerTests(unittest.TestCase):
    def test_public_cli_examples(self):
        commands = [
            ("scripts/hooks/rollout_events.py", "fixtures/rollout.synthetic.jsonl"),
            ("scripts/ledger/ledger_from_reports.py", "fixtures/reports/round-a.md", "fixtures/reports/round-b.md"),
            ("scripts/ledger/ledger_from_reports.py", "--vocabulary", "high-medium", "fixtures/reports/round-c.md"),
            ("scripts/ledger/validate_schema.py", "configs/ledger.schema.json", "fixtures/ledger.example.jsonl", "--jsonl"),
            ("scripts/ledger/validate_schema.py", "configs/hooks.schema.json", "configs/hooks.example.json"),
        ]
        for command in commands:
            result = subprocess.run([sys.executable, "-B", *command], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        with scratch() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            a.mkdir(); b.mkdir()
            (a / "example").write_text("ready")
            (b / "example").symlink_to(a / "example")
            result = subprocess.run([sys.executable, "-B", "scripts/hooks/mirror_check.py", str(a), str(b),
                                     "--require-links"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])

    def test_three_report_tallies(self):
        for name, vocabulary, expected, pending in (
                ("round-a.md", "standard", {"BLOCKER": 1, "MAJOR": 1, "MINOR": 1}, 1),
                ("round-b.md", "standard", {"MAJOR": 2}, 1),
                ("round-c.md", "high-medium", {"BLOCKER": 1, "HIGH": 1, "MEDIUM": 1}, 1)):
            counts, unconfirmed = ledger.tally((ROOT / "fixtures/reports" / name).read_text(), vocabulary)
            self.assertEqual(dict(counts), expected)
            self.assertEqual(unconfirmed, pending)

    def test_schema_accepts_example_and_hashes_match(self):
        specification = json.loads((ROOT / "configs/ledger.schema.json").read_text())
        row = json.loads((ROOT / "fixtures/ledger.example.jsonl").read_text())
        schema.validate(row, specification)
        fingerprint = hashlib.sha256((ROOT / "fixtures/review/subject.diff").read_bytes()).hexdigest()
        self.assertEqual(row["subject_sha_before"]["subject.diff"], fingerprint)
        self.assertEqual(row["subject_sha_before"], row["subject_sha_after"])

    def test_schema_rejects_missing_extra_wrong_type_and_negative(self):
        specification = json.loads((ROOT / "configs/ledger.schema.json").read_text())
        row = json.loads((ROOT / "fixtures/ledger.example.jsonl").read_text())
        cases = []
        changed = copy.deepcopy(row); del changed["reviewer"]; cases.append(changed)
        changed = copy.deepcopy(row); changed["extra"] = True; cases.append(changed)
        changed = copy.deepcopy(row); changed["round"] = True; cases.append(changed)
        changed = copy.deepcopy(row); changed["new_confirmed"]["BLOCKER"] = -1; cases.append(changed)
        changed = copy.deepcopy(row); changed["stop_decision"] = "zero means done"; cases.append(changed)
        changed = copy.deepcopy(row); changed["subject_sha_after"]["subject.diff"] = "bad"; cases.append(changed)
        for changed in cases:
            with self.assertRaises(ValueError):
                schema.validate(changed, specification)

    def test_hook_configuration_shape(self):
        specification = json.loads((ROOT / "configs/hooks.schema.json").read_text())
        config = json.loads((ROOT / "configs/hooks.example.json").read_text())
        schema.validate(config, specification)
        for groups in config["hooks"].values():
            for group in groups:
                for hook in group["hooks"]:
                    self.assertIn('$HOME/.agentB/hooks/', hook["command"])
        config["hooks"]["Stop"][0]["hooks"][0]["type"] = "unsupported"
        with self.assertRaises(ValueError):
            schema.validate(config, specification)


class BulkAndPromptTests(unittest.TestCase):
    def test_seeded_output_is_identical(self):
        self.assertEqual(bulk.generate(), bulk.generate())
        lines, key = bulk.generate()
        self.assertEqual(len(lines), 80)
        self.assertEqual(len(key), 80)
        self.assertEqual(set(key[0]), {"line", "time", "host", "service", "status", "latency_ms", "error"})

    def test_unit_conversion_against_generated_lines(self):
        import re
        lines, key = bulk.generate()
        seconds_rows = 0
        for line, expected in zip(lines, key):
            match = re.search(r"latency ([0-9.]+)(?:s\b| seconds)", line)
            if match:
                seconds_rows += 1
                self.assertEqual(round(float(match.group(1)) * 1000), expected["latency_ms"])
            else:
                match = re.search(r"(\d+)\s?ms", line)
                self.assertEqual(int(match.group(1)), expected["latency_ms"])
        self.assertGreater(seconds_rows, 0)

    def test_generator_cli_and_key_separation(self):
        with scratch() as directory:
            directory = Path(directory)
            command = [sys.executable, "-B", str(ROOT / "scripts/eval/gen_bulk_eval.py"),
                       "--out-dir", str(directory / "input"), "--answer-key", str(directory / "key.json")]
            first = subprocess.run(command, capture_output=True)
            self.assertEqual(first.returncode, 0)
            original = (directory / "key.json").read_bytes()
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(original, (directory / "key.json").read_bytes())
            command[-1] = str(directory / "input/key.json")
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)

    def test_prompt_sections(self):
        required = {
            "plan-closed.md": ["Verdict first", "Attack points", "holds / does not hold", "numbers without basis", "1,800"],
            "plan-open.md": ["Claim check", "Implementation and evaluation", "Knowledge gaps", "Allowed domains", "2,200"],
            "source-audit.md": ["Lens 1", "Lens 2", "CONFIRMED", "CONTRADICTED", "NOT-FOUND", "FETCH-FAILED", "SHA-256"],
            "review-spec.template.md": ["Background and previous report", "Files and suites", "Requirements", "Delivery", "above MAJOR"],
        }
        for name, sections in required.items():
            text = (ROOT / "prompts" / name).read_text()
            for section in sections:
                self.assertIn(section, text, name)

    def test_planted_source_audit_and_unchanged_hashes(self):
        paths = sorted((ROOT / "fixtures/audit").glob("*.md"))
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        source = (ROOT / "fixtures/audit/source.md").read_text()
        quotation = (ROOT / "fixtures/audit/quotation-report.md").read_text()
        consensus = (ROOT / "fixtures/audit/consensus-report.md").read_text()
        self.assertIn("accepted the supported input", source)
        self.assertIn("rejected the supported input", quotation)
        self.assertNotIn("rejected the supported input", source)
        self.assertIn("independent consensus", consensus)
        self.assertIn("no independent consensus evidence", source)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(before, after)
