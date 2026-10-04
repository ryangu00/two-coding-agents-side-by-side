import json
import os
from pathlib import Path
import subprocess
import unittest
from support import ROOT, scratch


class ReviewerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = scratch()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(self.directory),
                        AGENT_B_BIN=str(ROOT / "fixtures/stubs/agent_b.py"),
                        REVIEW_REPO_DRIVER=str(ROOT / "fixtures/stubs/repository.py"),
                        REVIEW_MODEL="example-model", REVIEW_PROVIDER="native", REVIEW_EFFORT="high",
                        REVIEW_CATALOG=str(self.directory / "catalog.json"),
                        STUB_RECORD=str(self.directory / "argv.json"), STUB_BEHAVIOR="exact")
        for key in ("STUB_NOT_REPO", "STUB_EMPTY_DIFF", "STUB_REPO_RECORD"):
            self.env.pop(key, None)

    def run_lane(self, *args):
        return subprocess.run(["/bin/bash", str(ROOT / "scripts/reviewer-lane/review-lane.sh"), *args],
                              env=self.env, text=True, capture_output=True, cwd=ROOT)

    def review(self, *extra):
        return self.run_lane("--repo", str(self.directory), "--base", "synthetic-base", "--out",
                             str(self.directory / "last.md"), *extra)

    def test_exact_reply_passes(self):
        result = self.run_lane("--selftest")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("metadata_warnings=0 replied=1", result.stdout)
        self.assertIn("SELFTEST OK", result.stdout)

    def test_echo_warning_silence_fail(self):
        for behavior, message in (("echo", "FAIL: no reply"), ("warning", "FAIL: model metadata missing"),
                                  ("silence", "FAIL: no reply")):
            with self.subTest(behavior=behavior):
                self.env["STUB_BEHAVIOR"] = behavior
                result = self.run_lane("--selftest")
                self.assertEqual(result.returncode, 1)
                self.assertIn(message, result.stderr)

    def test_failed_process_with_exact_reply_is_not_success(self):
        self.env["STUB_BEHAVIOR"] = "failed-exact"
        self.assertEqual(self.run_lane("--selftest").returncode, 1)

    def test_effort_banner_proposal_fails_closed_in_stub(self):
        self.env["STUB_BEHAVIOR"] = "wrong-effort"
        self.assertEqual(self.run_lane("--selftest").returncode, 1)
        result = self.review()
        self.assertEqual(result.returncode, 1)
        self.assertIn("effort banner mismatch", result.stderr)

    def test_review_flags_packet_and_closed_stdin(self):
        result = self.review()
        self.assertEqual(result.returncode, 0, result.stderr)
        recorded = json.loads((self.directory / "argv.json").read_text())
        argv = recorded["argv"]
        for flag in ("exec", "--skip-git-repo-check", "--ignore-user-config", "model_provider=native",
                     "model=example-model", "model_reasoning_effort=high", "-o"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("-s") + 1], "read-only")
        self.assertTrue(any(part.startswith("model_catalog_json=") for part in argv))
        self.assertEqual(recorded["stdin"], "")
        self.assertTrue(argv[-1].startswith("# Handoff packet"))
        for text in ("example.py", "Worktree clean", "Commit subjects", "```diff"):
            self.assertIn(text, argv[-1])
        self.assertIn("SOUND", result.stdout)

    def test_schema_passthrough(self):
        result = self.review("--schema", "configs/ledger.schema.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads((self.directory / "argv.json").read_text())["argv"]
        self.assertEqual(argv[argv.index("--output-schema") + 1], "configs/ledger.schema.json")

    def test_non_repository_and_empty_diff_exit_two(self):
        for option in ("STUB_NOT_REPO", "STUB_EMPTY_DIFF"):
            self.env[option] = "yes"
            self.assertEqual(self.review().returncode, 2)
            self.env.pop(option)

    def test_bad_arguments_exit_two(self):
        self.assertEqual(self.run_lane("--unknown").returncode, 2)
        self.assertEqual(self.run_lane("--base").returncode, 2)

    def test_supplied_diff_requires_matching_packet(self):
        result = self.run_lane("--diff", "fixtures/review/subject.diff", "--out", str(self.directory / "out.md"))
        self.assertEqual(result.returncode, 2)
        result = self.run_lane("--diff", "fixtures/review/subject.diff", "--packet", "fixtures/review/packet.md",
                               "--out", str(self.directory / "out.md"))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_catalog_created_and_bad_catalog_refused(self):
        self.assertEqual(self.run_lane("--selftest").returncode, 0)
        catalog = json.loads((self.directory / "catalog.json").read_text())
        self.assertEqual(catalog["models"][0]["context_window"], 200000)
        self.assertEqual(catalog["models"][0]["effective_context_window_percent"], 95)
        (self.directory / "catalog.json").write_text("bad json")
        self.assertEqual(self.run_lane("--selftest").returncode, 2)

    def test_direct_precheck_refuses_before_agent_call(self):
        precheck = self.directory / "precheck.sh"
        precheck.write_text("#!/bin/sh\nexit 1\n")
        precheck.chmod(0o755)
        self.env["PRECHECK_CMD"] = str(precheck)
        result = subprocess.run(["/bin/bash", str(ROOT / "scripts/reviewer-lane/review-direct.sh"),
                                 str(ROOT / "fixtures/review/packet.md"), str(self.directory / "direct.md")],
                                env=self.env, capture_output=True)
        self.assertEqual(result.returncode, 9)
        self.assertFalse((self.directory / "argv.json").exists())

    def test_direct_precheck_allows_stub(self):
        precheck = self.directory / "precheck.sh"
        precheck.write_text("#!/bin/sh\nexit 0\n")
        precheck.chmod(0o755)
        self.env["PRECHECK_CMD"] = str(precheck)
        result = subprocess.run(["/bin/bash", str(ROOT / "scripts/reviewer-lane/review-direct.sh"),
                                 str(ROOT / "fixtures/review/packet.md"), str(self.directory / "direct.md")],
                                env=self.env, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue((self.directory / "direct.md").exists())
