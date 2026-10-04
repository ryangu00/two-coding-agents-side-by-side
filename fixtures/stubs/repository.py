#!/usr/bin/env python3
"""Recorded repository responses; does not invoke a version-control executable."""
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
if os.environ.get("STUB_REPO_RECORD"):
    with open(os.environ["STUB_REPO_RECORD"], "a") as stream:
        stream.write(json.dumps(args) + "\n")
if os.environ.get("STUB_NOT_REPO"):
    raise SystemExit(1)
args = args[2:] if args[:1] == ["-C"] else args
if args == ["rev-parse", "--git-dir"]:
    print(".git")
elif args == ["rev-parse", "--short", "HEAD"]:
    print("synthetic-head")
elif args == ["status", "--porcelain"]:
    pass
elif args[:2] == ["diff", "--stat"]:
    print(" example.py | changed")
elif args[:1] == ["diff"]:
    if not os.environ.get("STUB_EMPTY_DIFF"):
        print((Path(__file__).parents[1] / "review/subject.diff").read_text(), end="")
elif args[:2] == ["log", "--oneline"]:
    print("synthetic-head Change example answer")
else:
    print("Unsupported fixture request", file=sys.stderr)
    raise SystemExit(2)
