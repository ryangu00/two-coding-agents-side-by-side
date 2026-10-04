#!/usr/bin/env python3
"""Offline agent stub; assertions against this program are not live acceptance."""
import json
import os
from pathlib import Path
import sys

argv = sys.argv[1:]
settings = {}
for index, arg in enumerate(argv[:-1]):
    if arg == "-c":
        name, value = argv[index + 1].split("=", 1)
        settings[name] = value
if os.environ.get("STUB_RECORD"):
    Path(os.environ["STUB_RECORD"]).write_text(json.dumps({"argv": argv, "stdin": sys.stdin.read()}))
behavior = os.environ.get("STUB_BEHAVIOR", "exact")
print("model: " + settings.get("model", "example-model"), file=sys.stderr)
effort = "none" if behavior == "wrong-effort" else settings.get("model_reasoning_effort", "high")
print("reasoning effort: " + effort, file=sys.stderr)
if behavior == "warning":
    print("Model metadata for example-model not found", file=sys.stderr)
if "-o" in argv:
    Path(argv[argv.index("-o") + 1]).write_text("SOUND\nSynthetic review only.\n")
elif behavior == "echo":
    print("Reply with exactly: LANE_OK")
elif behavior != "silence":
    print("LANE_OK")
raise SystemExit(1 if behavior == "failed-exact" else 0)
