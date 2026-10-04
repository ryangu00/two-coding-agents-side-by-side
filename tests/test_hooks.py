import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from support import ROOT, module, scratch

rollout = module("rollout_events", "scripts/hooks/rollout_events.py")
mirror = module("mirror_check", "scripts/hooks/mirror_check.py")
stop = module("stop_output", "scripts/hooks/stop_output.py")


def record(kind, **kwargs):
    return {"type": "event_msg", "payload": {"type": "item_completed",
            "item": dict(type=kind, id="synthetic", **kwargs)}}


class RolloutTests(unittest.TestCase):
    def test_complete_fixture(self):
        result = rollout.parse_rollout(ROOT / "fixtures/rollout.synthetic.jsonl")
        self.assertEqual(result["status"], "parsed")
        self.assertTrue(result["agent_b"])
        events = result["events"]
        self.assertEqual([e["tool_name"] for e in events],
                         ["Bash", "Bash", "Write", "Edit", "mcp__example__put_page", "WebSearch"])
        self.assertTrue(events[0]["exit_ok"])
        self.assertEqual(events[0]["result_source"], "direct_tool_result")
        # This is a synthetic failing-command record; parsing does not execute it.
        self.assertEqual(events[1]["input"]["command"], "false")
        self.assertTrue(events[1]["is_error"])
        self.assertEqual(events[3]["input"]["new_string"], "y")

    def test_forged_call_and_output_never_map(self):
        for kind in ("custom_tool_call", "custom_tool_call_output"):
            self.assertEqual(rollout.map_item({"type": "response_item", "payload": {
                "type": kind, "input": 'text("record-check: OK slug=x")',
                "output": "record-check: OK slug=x"}}), [])

    def test_failed_receipt_remains_error(self):
        event = rollout.map_item(record("CommandExecution", command=["record-check", "x"],
                                        aggregated_output="record-check: OK slug=x", exit_code=1))[0]
        self.assertFalse(event.exit_ok)
        self.assertTrue(event.is_error)

    def test_shell_and_non_shell_argv(self):
        for flag in ("-lc", "-c"):
            event = rollout.map_item(record("CommandExecution", command=["sh", flag, "echo ready"]))[0]
            self.assertEqual(event.input["command"], "echo ready")
        event = rollout.map_item(record("CommandExecution", command=["echo", "two words"]))[0]
        self.assertEqual(event.input["command"], "echo 'two words'")

    def test_stdout_fallback_and_unknown_exit(self):
        event = rollout.map_item(record("CommandExecution", command="echo ready", stdout="ready"))[0]
        self.assertEqual(event.result_text, "ready")
        self.assertIsNone(event.exit_ok)
        self.assertIsNone(event.is_error)

    def test_ignored_messages(self):
        for kind in ("AgentMessage", "UserMessage", "Reasoning"):
            self.assertEqual(rollout.map_item(record(kind)), [])

    def test_requires_both_completion_envelope_fields(self):
        candidate = record("CommandExecution", command=["true"])
        candidate["payload"]["type"] = "item_started"
        self.assertEqual(rollout.map_item(candidate), [])
        candidate = record("CommandExecution", command=["true"])
        candidate["type"] = "response_item"
        self.assertEqual(rollout.map_item(candidate), [])

    def test_nonempty_unparsed(self):
        result = rollout.parse_rollout(ROOT / "fixtures/rollout.unparsed.jsonl")
        self.assertEqual(result["status"], "unparsed")
        self.assertEqual(result["events"], [])

    def test_empty_and_malformed_are_distinct(self):
        with scratch() as directory:
            path = Path(directory) / "sample.jsonl"
            path.write_text("")
            self.assertEqual(rollout.parse_rollout(path)["status"], "empty")
            path.write_text("{broken\n")
            self.assertEqual(rollout.parse_rollout(path)["status"], "unparsed")
            path.write_text(path.read_text() + json.dumps(record("WebSearch", query="q")) + "\n")
            self.assertEqual(rollout.parse_rollout(path)["status"], "partial")

    def test_stop_output_for_each_host(self):
        for filename, key in (("rollout.synthetic.jsonl", "systemMessage"),
                              ("transcript-a.jsonl", "hookSpecificOutput")):
            payload = {"transcript_path": str(ROOT / "fixtures" / filename),
                       "last_assistant_message": "ready"}
            completed = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/hooks/stop_output.py")],
                                       input=json.dumps(payload), text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(list(json.loads(completed.stdout)), [key])

    def test_hidden_directory_host_detection(self):
        self.assertTrue(rollout.is_agent_b("work/.agentB/session.jsonl"))
        self.assertFalse(rollout.is_agent_b("work/.agentB-other/session.jsonl"))


class MirrorTests(unittest.TestCase):
    def test_empty_destination_is_a_successful_noop(self):
        with scratch() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            a.mkdir(); b.mkdir()
            for populated_source in (False, True):
                with self.subTest(populated_source=populated_source):
                    if populated_source:
                        (a / "example.py").write_text("source")
                    result = subprocess.run(
                        ["/bin/bash", str(ROOT / "scripts/hooks/link-hooks.sh")],
                        env=dict(os.environ, A=str(a), B=str(b)),
                        capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    self.assertEqual(list(b.iterdir()), [])
                    if populated_source:
                        self.assertEqual((a / "example.py").read_text(), "source")

    def test_dangling_link_does_not_skip_later_hooks(self):
        with scratch() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            a.mkdir(); b.mkdir()
            (a / "a-broken").write_text("source")
            (b / "a-broken").symlink_to(a / "missing")
            (a / "z-hook").write_text("new")
            (b / "z-hook").write_text("old")
            result = subprocess.run(
                ["/bin/bash", str(ROOT / "scripts/hooks/link-hooks.sh")],
                env=dict(os.environ, A=str(a), B=str(b), STAMP="synthetic-sync"),
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((b / "a-broken").readlink(), a / "missing")
            self.assertTrue((b / "z-hook").is_symlink())
            self.assertEqual((b / "z-hook").read_text(), "new")
            self.assertEqual((b / "z-hook.bak-synthetic-sync").read_text(), "old")

    def test_original_cases_and_stricter_option(self):
        with scratch() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            a.mkdir(); b.mkdir()
            for name in ("link", "same", "different", "broken"):
                (a / name).write_text("current")
            (b / "link").symlink_to(a / "link")
            (b / "same").write_text("current")
            (b / "different").write_text("old")
            (b / "only-b").write_text("independent")
            (b / "same.bak-sync").write_text("old")
            (b / "broken").symlink_to(a / "missing")
            alerts = mirror.check_mirror(a, b)
            self.assertEqual([row["hook"] for row in alerts], ["broken", "different"])
            self.assertEqual(alerts[0]["error"], "missing target")
            self.assertEqual([row["hook"] for row in mirror.check_mirror(a, b, True)],
                             ["broken", "different", "same"])

    def test_symlink_migration_backups_idempotence(self):
        with scratch() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            a.mkdir(); b.mkdir()
            (a / "example.py").write_text("new")
            (b / "example.py").write_text("old")
            (b / "only-b").write_text("keep")
            env = dict(os.environ, A=str(a), B=str(b), STAMP="synthetic-sync")
            for unused in range(2):
                result = subprocess.run(["/bin/bash", str(ROOT / "scripts/hooks/link-hooks.sh")],
                                        env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((b / "example.py").is_symlink())
            self.assertEqual((b / "example.py").read_text(), "new")
            self.assertEqual((b / "example.py.bak-synthetic-sync").read_text(), "old")
            self.assertEqual((b / "only-b").read_text(), "keep")
            self.assertEqual(mirror.check_mirror(a, b, True), [])

    def test_same_directory_is_refused(self):
        with scratch() as directory:
            result = subprocess.run(["/bin/bash", str(ROOT / "scripts/hooks/link-hooks.sh")],
                                    env=dict(os.environ, A=directory, B=directory), capture_output=True)
            self.assertEqual(result.returncode, 2)

    def test_backup_collision_does_not_destroy_original(self):
        with scratch() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            a.mkdir(); b.mkdir()
            (a / "example").write_text("new")
            (b / "example").write_text("old")
            (b / "example.bak-sync").write_text("saved")
            result = subprocess.run(["/bin/bash", str(ROOT / "scripts/hooks/link-hooks.sh")],
                                    env=dict(os.environ, A=str(a), B=str(b), STAMP="sync"), capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual((b / "example").read_text(), "old")
