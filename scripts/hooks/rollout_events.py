#!/usr/bin/env python3
"""Map harness completion records. Parsing is not a receipt or policy verdict."""
import argparse
import json
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Event:
    tool_name: str
    input: dict
    tool_use_id: str = ""
    result_text: str = ""
    result_source: str = "none"
    exit_ok: Optional[bool] = None
    is_error: Optional[bool] = None


def is_agent_b(path):
    if ".agentB" in Path(path).parts:
        return True
    try:
        with open(path, encoding="utf-8") as stream:
            first = json.loads(stream.readline())
        return isinstance(first, dict) and first.get("type") == "session_meta"
    except (OSError, ValueError):
        return False


def added_text(change):
    if change.get("type") == "add":
        return str(change.get("content") or "")
    return "\n".join(line[1:] for line in str(change.get("unified_diff") or "").splitlines()
                     if line.startswith("+") and not line.startswith("+++"))


def map_item(record):
    if not isinstance(record, dict) or "message" in record:
        return []
    payload = record.get("payload")
    if record.get("type") != "event_msg" or not isinstance(payload, dict):
        return []
    if payload.get("type") != "item_completed":
        return []
    item = payload.get("item")
    if not isinstance(item, dict):
        return []
    kind, identifier = item.get("type"), str(item.get("id") or "")
    if kind == "CommandExecution":
        argv = item.get("command")
        if isinstance(argv, list):
            command = (str(argv[2]) if len(argv) >= 3 and argv[1] in ("-lc", "-c")
                       else shlex.join(map(str, argv)))
        else:
            command = str(argv or "")
        code = item.get("exit_code")
        failed = code != 0 if type(code) is int else None
        return [Event("Bash", {"command": command}, identifier,
                      str(item.get("aggregated_output") or item.get("stdout") or ""),
                      "direct_tool_result", None if failed is None else not failed, failed)]
    if kind == "FileChange":
        return [Event("Write" if change.get("type") == "add" else "Edit",
                      {"file_path": path, "new_string": added_text(change)}, f"{identifier}:{index}")
                for index, (path, change) in enumerate((item.get("changes") or {}).items())
                if isinstance(change, dict)]
    if kind == "McpToolCall":
        return [Event(f"mcp__{item.get('server')}__{item.get('tool')}",
                      item.get("arguments") or {}, identifier)]
    if kind == "WebSearch":
        return [Event("WebSearch", {"query": item.get("query")}, identifier)]
    return []


def parse_rollout(path):
    events, errors, nonempty = [], [], False
    with open(path, encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            nonempty = True
            try:
                events.extend(map_item(json.loads(line)))
            except (ValueError, TypeError, AttributeError) as error:
                errors.append({"line": number, "error": type(error).__name__})
    status = "unparsed" if nonempty and not events else "parsed" if events else "empty"
    if errors and events:
        status = "partial"
    return {"status": status, "agent_b": is_agent_b(path),
            "events": [asdict(event) for event in events], "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rollout")
    args = parser.parse_args()
    result = parse_rollout(args.rollout)
    print(json.dumps(result, indent=2))
    return 1 if result["status"] in ("unparsed", "partial") else 0


if __name__ == "__main__":
    raise SystemExit(main())
