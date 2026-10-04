#!/usr/bin/env python3
"""Fan out a plan review; preserve attempts and distinguish text from execution."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

RETRY_SUFFIX = "\nVerdict on the first line; at most 1,800 characters; keep thinking short."


def request_completion(endpoint, key, body):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    request = urllib.request.Request(endpoint, json.dumps(body).encode(), headers)
    with urllib.request.urlopen(request, timeout=1500) as response:
        return json.load(response)


def review_model(model, prompt, request):
    attempts = []
    for cap in (20000, 60000):
        body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                "max_tokens": cap, "temperature": 0.4}
        started = time.monotonic()
        try:
            response = request(body)
            choice = response["choices"][0]
            text = choice["message"].get("content") or ""
            attempt = {"chars": len(text), "finish_reason": choice.get("finish_reason"),
                       "total_tokens": response.get("usage", {}).get("total_tokens"),
                       "seconds": round(time.monotonic() - started), "max_tokens": cap,
                       "served_model": response.get("model"), "text": text}
        except Exception as error:
            # Do not copy an exception that could contain a credential or request body.
            attempt = {"chars": 0, "finish_reason": "error", "total_tokens": None,
                       "seconds": round(time.monotonic() - started), "max_tokens": cap,
                       "error": type(error).__name__, "text": ""}
        attempts.append(attempt)
        if attempt["chars"] == 0 and attempt["finish_reason"] == "length":
            prompt += RETRY_SUFFIX
            continue
        break
    return {"reviewer": model, "attempts": attempts,
            "ok": bool(attempts[-1]["chars"]) and attempts[-1]["finish_reason"] == "stop"}


def count_executions(path):
    """Count structured CommandExecution completions, never narration."""
    count = 0
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        payload = record.get("payload") or {}
        if (record.get("type") == "event_msg" and payload.get("type") == "item_completed"
                and (payload.get("item") or {}).get("type") == "CommandExecution"):
            count += 1
    return count


def tool_review(command, prompt_path, output_path, log_path):
    """Command is a JSON argv array supplied by the caller, without a shell."""
    if not command or not all(isinstance(part, str) for part in command):
        raise ValueError("Tool command must be a nonempty argv array.")
    if not any(flag in command for flag in ("-s", "--sandbox")):
        raise ValueError("Tool reviewer must declare its own sandbox flag.")
    for path in (output_path, log_path):
        if Path(path).exists():
            raise ValueError("Use fresh tool output and structured log paths.")
    values = {"prompt": str(prompt_path), "output": str(output_path), "log": str(log_path)}
    argv = [part.format(**values) for part in command]
    started = time.monotonic()
    result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=1500)
    text = Path(output_path).read_text() if Path(output_path).exists() else ""
    executed = count_executions(log_path) if Path(log_path).exists() else None
    return {"reviewer": "tool-enabled", "exit_code": result.returncode, "chars": len(text),
            "seconds": round(time.monotonic() - started), "executed_commands": executed,
            "text": text, "ok": result.returncode == 0 and bool(text)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mock-fixture", help="Canned responses; makes no network requests")
    args = parser.parse_args()
    prompt = Path(args.prompt).read_text()
    models = json.loads(os.environ.get("REVIEW_MODELS", '["example-model"]'))
    if not isinstance(models, list) or not models or not all(isinstance(m, str) for m in models):
        parser.error("REVIEW_MODELS must be a nonempty JSON array of model strings")
    canned = json.loads(Path(args.mock_fixture).read_text()) if args.mock_fixture else None

    def run(model):
        if canned is not None:
            replies = iter(canned[model])
            request = lambda body: next(replies)
        else:
            endpoint = os.environ.get("REVIEW_ENDPOINT", "http://127.0.0.1:4000/v1/chat/completions")
            request = lambda body: request_completion(endpoint, os.environ.get("REVIEW_API_KEY", ""), body)
        return review_model(model, prompt, request)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(models)) as pool:
        results = list(pool.map(run, models))
    command = os.environ.get("TOOL_REVIEW_COMMAND")
    if command and not args.mock_fixture:
        results.append(tool_review(json.loads(command), args.prompt, args.out + ".tool.md",
                                   args.out + ".tool.jsonl"))
    Path(args.out).write_text(json.dumps(results, indent=2) + "\n")
    print("FANOUT OK" if all(row["ok"] for row in results) else "FANOUT INCOMPLETE")
    return 0 if all(row["ok"] for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
