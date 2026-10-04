#!/usr/bin/env bash
# Minimal direct variant: the caller supplies a pre-check executable and model.
set -euo pipefail
[ $# -ge 2 ] || { echo 'Usage: review-direct.sh promptfile outfile [workdir]' >&2; exit 2; }
: "${PRECHECK_CMD:?Set PRECHECK_CMD to an executable accepting the prompt path}"
: "${REVIEW_MODEL:?Set an account-verified model}"
prompt="$1"; out="$2"; wd="${3:-$PWD}"
"$PRECHECK_CMD" "$prompt" || { echo 'ABORT: pre-check refused the prompt' >&2; exit 9; }
exec "${AGENT_B_BIN:-agent-b}" exec -s read-only -C "$wd" --skip-git-repo-check \
  --ignore-user-config -c "model_provider=${REVIEW_PROVIDER:-native}" \
  -c "model=$REVIEW_MODEL" -c "model_reasoning_effort=${REVIEW_EFFORT:-high}" \
  -o "$out" "$(cat "$prompt")" < /dev/null
