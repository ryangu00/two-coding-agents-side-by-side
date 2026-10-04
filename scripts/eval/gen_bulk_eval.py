#!/usr/bin/env python3
"""Synthetic, English-only adaptation. Keep the key outside the reviewer input."""
import argparse
import json
from pathlib import Path
import random

NODES = ["node-a", "node-b", "node-c", "node-d", "node-e"]
SERVICES = ["service-a", "service-b", "service-c", "service-d", "service-e", "service-f", "service-g"]
ERRORS = [("timeout", "timed out"), ("oom", "out of memory"),
          ("conn_refused", "connection refused"), ("none", "no error"), ("5xx", "upstream 5xx")]
FORMATS = [
    "{t} [{host}] {svc} returned {code}, took {ms} ms, error: {label}",
    "At {t} the {svc} service on {host} answered HTTP {code} after {ms}ms (error={enum}).",
    "{host}/{svc} @ {t} -- status {code}; latency {sec}s; err: {enum}",
    "{t} service {svc}({host}) status {code}, latency {sec} seconds, {label}",
    "[{t}] host={host} svc={svc} code={code} took {ms} ms, failure kind {enum}",
]


def generate():
    rng = random.Random(20260925)
    lines, key = [], []
    for index in range(80):
        host, service = rng.choice(NODES), rng.choice(SERVICES)
        code = rng.choice([200, 200, 200, 400, 429, 500, 502, 504])
        milliseconds = rng.randrange(20, 90000)
        enum, label = rng.choice(ERRORS) if code >= 400 else ERRORS[3]
        timestamp = f"{rng.randrange(0, 24):02d}:{rng.randrange(0, 60):02d}"
        template = rng.choice(FORMATS)
        lines.append(template.format(t=timestamp, host=host, svc=service, code=code,
                                     ms=milliseconds, sec=f"{milliseconds / 1000:.3f}",
                                     enum=enum, label=label))
        key.append(dict(line=index + 1, time=timestamp, host=host, service=service,
                        status=code, latency_ms=milliseconds, error=enum))
    return lines, key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--answer-key", required=True)
    args = parser.parse_args()
    directory, key_path = Path(args.out_dir), Path(args.answer_key)
    if key_path.resolve() == directory.resolve() or directory.resolve() in key_path.resolve().parents:
        parser.error("Place the answer key outside the reviewer input directory")
    lines, key = generate()
    directory.mkdir(parents=True, exist_ok=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    (directory / "logs.txt").write_text("\n".join(lines) + "\n")
    key_path.write_text(json.dumps(key, indent=2) + "\n")
    (directory / "TASK.md").write_text(
        "# Extraction task\n\nExtract each input line to JSON in order.\n"
        "Return line (the row index), time, host, service, status (integer), latency_ms "
        "(integer; convert seconds to milliseconds and round), and error.\n"
        "The six extracted fields exclude the line index.\n"
        "Map timed out / out of memory / connection refused / no error / upstream 5xx "
        "to timeout / oom / conn_refused / none / 5xx.\n"
        "Write only the requested JSON output; make no network requests.\n")
    print("BULK FIXTURE OK")


if __name__ == "__main__":
    main()
