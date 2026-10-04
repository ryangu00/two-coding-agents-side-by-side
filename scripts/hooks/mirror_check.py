#!/usr/bin/env python3
"""Compare shared hook bytes; optionally require links. No private guards."""
import argparse
import filecmp
import json
from pathlib import Path


def check_mirror(agent_a, agent_b, require_links=False):
    alerts = []
    filecmp.clear_cache()
    for candidate in sorted(Path(agent_b).iterdir()):
        source = Path(agent_a) / candidate.name
        if ".bak" in candidate.name or not source.is_file():
            continue
        try:
            if not filecmp.cmp(source, candidate, shallow=False):
                alerts.append({"hook": candidate.name, "error": "different bytes"})
            elif require_links and not candidate.is_symlink():
                alerts.append({"hook": candidate.name, "error": "regular copy"})
        except FileNotFoundError:
            alerts.append({"hook": candidate.name, "error": "missing target"})
    return alerts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent_a")
    parser.add_argument("agent_b")
    parser.add_argument("--require-links", action="store_true")
    args = parser.parse_args()
    alerts = check_mirror(args.agent_a, args.agent_b, args.require_links)
    print(json.dumps({"ok": not alerts, "alerts": alerts}, indent=2))
    return bool(alerts)


if __name__ == "__main__":
    raise SystemExit(main())
