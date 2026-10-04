#!/usr/bin/env python3
"""Demonstrate the host-specific Stop output branch, without guard criteria."""
import argparse
import json
import sys
from rollout_events import is_agent_b


def stop_output(payload, reminder):
    if is_agent_b(payload.get("transcript_path") or ""):
        return {"systemMessage": reminder}
    return {"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": reminder}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reminder", default="Review the session record.")
    args = parser.parse_args()
    print(json.dumps(stop_output(json.load(sys.stdin), args.reminder)))


if __name__ == "__main__":
    main()
