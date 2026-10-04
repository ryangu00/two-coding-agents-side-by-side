import ast
import json
from pathlib import Path
import re
import subprocess
import unittest
from support import ROOT


class PublicationTests(unittest.TestCase):
    def public_files(self):
        for path in ROOT.rglob("*"):
            if path.is_file() and not any(part.startswith(".") or part == "__pycache__"
                                          for part in path.relative_to(ROOT).parts):
                yield path

    def test_readme_size_and_banner(self):
        text = (ROOT / "README.md").read_text()
        self.assertTrue(text.startswith("![banner](docs/assets/banner.png)\n"))
        # Editorial size sanity check, not a completeness or quality assertion.
        self.assertGreaterEqual(len(text.splitlines()), 250)
        self.assertLessEqual(len(text.splitlines()), 450)

    def test_no_cjk_characters(self):
        forbidden = re.compile(r"[\u2e80-\u2fff\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff\U00020000-\U000323af]")
        for path in self.public_files():
            if path.suffix in {".png", ".jpg", ".jpeg", ".gif"}:
                continue
            self.assertIsNone(forbidden.search(path.read_text()), str(path.relative_to(ROOT)))

    def test_python_and_shell_syntax_without_banner_execution(self):
        for path in self.public_files():
            if path.suffix == ".py":
                ast.parse(path.read_text(), filename=path.name)
            if path.suffix == ".sh":
                result = subprocess.run(["/bin/bash", "-n", str(path)], capture_output=True)
                self.assertEqual(result.returncode, 0, path.name)

    def test_all_structured_data_parses(self):
        for path in self.public_files():
            if path.suffix == ".json":
                json.loads(path.read_text())
            elif path.suffix == ".jsonl":
                for line in path.read_text().splitlines():
                    if line.strip():
                        json.loads(line)

    def test_markdown_file_links_exist_except_deferred_banner(self):
        for path in self.public_files():
            if path.suffix != ".md":
                continue
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                if target == "docs/assets/banner.png":
                    continue
                self.assertTrue((path.parent / target.split("#")[0]).exists(), f"{path.name}: {target}")

    def test_cookbook_links_use_only_named_absolute_repositories(self):
        allowed = {"agent-guards-that-fail-silently", "decision-record-deidentification-gates",
                   "llm-gateway-routing-in-production", "local-llm-bakeoff-measurement-pitfalls"}
        for path in self.public_files():
            if path.suffix == ".md":
                for name in re.findall(r"https://github.com/ryangu00/([a-z0-9-]+)", path.read_text()):
                    self.assertIn(name, allowed)
