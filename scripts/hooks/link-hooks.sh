#!/usr/bin/env bash
# Link same-named hooks; preserve originals. Supply directories as A and B.
set -euo pipefail
A="${A:-$HOME/.agentA/hooks}"
B="${B:-$HOME/.agentB/hooks}"
stamp="${STAMP:-$(date +%Y%m%d)-sync}"
[ -d "$A" ] && [ -d "$B" ] || { echo 'Both hook directories must exist.' >&2; exit 2; }
A=$(cd "$A" && pwd -P)
B=$(cd "$B" && pwd -P)
[ "$A" != "$B" ] || { echo 'Hook directories must differ.' >&2; exit 2; }
for f in "$B"/*; do
  [ -e "$f" ] || continue  # Skip an unmatched glob or a dangling link.
  n=$(basename "$f")
  case "$n" in *.bak*|__pycache__) continue;; esac
  [ -f "$A/$n" ] || continue
  [ -L "$f" ] && continue
  [ -f "$f" ] || continue
  [ ! -e "$f.bak-$stamp" ] && [ ! -L "$f.bak-$stamp" ] || {
    echo "Backup already exists: $n.bak-$stamp" >&2; exit 2;
  }
  mv "$f" "$f.bak-$stamp"
  ln -s "$A/$n" "$f"
done
# Rollback: replace <stamp> with the exact suffix before running this loop.
# for f in "$B"/*.bak-<stamp>; do mv -f "$f" "${f%.bak-<stamp>}"; done
