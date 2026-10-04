#!/usr/bin/env bash
# Caller-side, packet-plus-diff review. Defaults are synthetic placeholders.
# Effort pin and banner assertions are an UNTESTED LIVE PROPOSAL, stub-tested only.
# Catalog compatibility is version-sensitive; see docs/reviewer-lane.md.
set -euo pipefail
AGENT="${AGENT_B_BIN:-agent-b}"
MODEL="${REVIEW_MODEL:-example-model}"
PROVIDER="${REVIEW_PROVIDER:-native}"
EFFORT="${REVIEW_EFFORT:-high}"
CATALOG="${REVIEW_CATALOG:-.review-lane/catalog.json}"
REPO_DRIVER="${REVIEW_REPO_DRIVER:-git}"
die() { printf 'review-lane: %s\n' "$*" >&2; exit 2; }
command -v "$AGENT" >/dev/null 2>&1 || die 'Agent binary unavailable; set AGENT_B_BIN.'

ensure_catalog() {
  python3 - "$CATALOG" "$MODEL" <<'PY'
import json, pathlib, sys
path, model = pathlib.Path(sys.argv[1]), sys.argv[2]
if path.exists() and path.stat().st_size:
    catalog = json.loads(path.read_text())
    if not any(model in (row.get("id"), row.get("model"), row.get("slug"))
               for row in catalog["models"]):
        raise SystemExit("Catalog does not contain the requested model.")
else:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = dict(id=model, model=model, slug=model, displayName=model, display_name=model,
               description="Native-provider reviewer", base_instructions="You are a coding agent.",
               context_window=200000, max_context_window=200000,
               effective_context_window_percent=95, priority=0,
               apply_patch_tool_type="freeform", shell_type="shell_command",
               default_reasoning_summary="none", support_verbosity=True,
               input_modalities=["text"], service_tiers=[], additional_speed_tiers=[],
               experimental_supported_tools=[])
    path.write_text(json.dumps({"models": [row]}, indent=2) + "\n")
print(path.resolve())
PY
}
CATALOG=$(ensure_catalog) || die 'Invalid model catalog.'
OVERRIDES=(--ignore-user-config -c "model_provider=$PROVIDER" -c "model=$MODEL"
           -c "model_catalog_json=$CATALOG" -c "model_reasoning_effort=$EFFORT")
WORK=$(mktemp -d "${TMPDIR:-.}/review-lane.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
assert_banner() {
  grep -Fxq "model: $MODEL" "$1" || { echo 'FAIL: model banner mismatch' >&2; return 1; }
  grep -Fxq "reasoning effort: $EFFORT" "$1" || {
    echo 'FAIL: effort banner mismatch (proposal requires CLI verification)' >&2; return 1;
  }
}

if [ "${1:-}" = --selftest ]; then
  rc=0
  "$AGENT" exec --skip-git-repo-check -s read-only "${OVERRIDES[@]}" \
    'Reply with exactly: LANE_OK' < /dev/null > "$WORK/banner" 2>&1 || rc=$?
  warns=$(grep -c 'metadata for .* not found' "$WORK/banner" || true)
  ok=$(grep -cx 'LANE_OK' "$WORK/banner" || true)
  printf 'model=%s metadata_warnings=%s replied=%s\n' "$MODEL" "$warns" "$ok"
  [ "$warns" -eq 0 ] || { echo 'FAIL: model metadata missing' >&2; exit 1; }
  [ "$ok" -ge 1 ] || { echo 'FAIL: no reply' >&2; exit 1; }
  [ "$rc" -eq 0 ] || { echo 'FAIL: agent exited unsuccessfully' >&2; exit 1; }
  assert_banner "$WORK/banner" || exit 1
  echo 'SELFTEST OK'
  exit 0
fi

REPO="$PWD"; BASE=''; DIFF_FILE=''; PACKET_FILE=''; ASK=''; SCHEMA_FILE=''; OUT_FILE=''
while [ $# -gt 0 ]; do
  case "$1" in
    --repo|--base|--diff|--packet|--ask|--schema|--out)
      [ $# -ge 2 ] || die "Missing value for $1"
      case "$1" in
        --repo) REPO="$2";; --base) BASE="$2";; --diff) DIFF_FILE="$2";;
        --packet) PACKET_FILE="$2";; --ask) ASK="$2";; --schema) SCHEMA_FILE="$2";; --out) OUT_FILE="$2";;
      esac; shift 2;;
    *) die "Unknown argument: $1";;
  esac
done
"$REPO_DRIVER" -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || die 'Not a repository.'
[ -n "$BASE" ] || [ -n "$DIFF_FILE" ] || die 'Need --base or --diff.'
[ -n "$PACKET_FILE" ] || [ -n "$BASE" ] || die 'Supply --packet with a standalone --diff.'
[ -n "$OUT_FILE" ] || die 'Supply --out outside the reviewed subject.'
if [ -z "$DIFF_FILE" ]; then
  DIFF_FILE="$WORK/review.diff"
  "$REPO_DRIVER" -C "$REPO" diff "$BASE"...HEAD > "$DIFF_FILE"
fi
[ -s "$DIFF_FILE" ] || die 'Diff is empty.'
diff_lines=$(wc -l < "$DIFF_FILE" | tr -d ' ')
if [ -z "$PACKET_FILE" ]; then
  PACKET_FILE="$WORK/handoff.md"
  {
    printf '# Handoff packet\n\n- Repo: %s\n- Base: %s\n' "$(basename "$REPO")" "$BASE"
    printf '%s\n' "- Head: $("$REPO_DRIVER" -C "$REPO" rev-parse --short HEAD)"
    if [ -z "$("$REPO_DRIVER" -C "$REPO" status --porcelain)" ]; then
      echo '- Worktree clean: yes'
    else
      echo '- Worktree clean: NO; the committed range alone is reviewed'
    fi
    printf '\n## Changed files\n'
    "$REPO_DRIVER" -C "$REPO" diff --stat "$BASE"...HEAD
    printf '\n## Commit subjects in range\n'
    "$REPO_DRIVER" -C "$REPO" log --oneline "$BASE"..HEAD
  } > "$PACKET_FILE"
fi
{
  cat "$PACKET_FILE"
  printf '\n# Read-only review\n'
  echo 'Assume the change is wrong until the diff proves otherwise.'
  echo 'Do not explore the wider repository. Do not modify files.'
  if [ -n "$ASK" ]; then printf 'Focus: %s\n' "$ASK"; fi
  echo 'Answer in under 500 words: findings most severe first as file:line, defect, failing scenario;'
  echo 'whether each packet claim is supported; verdict SOUND / NEEDS CHANGES / UNSOUND.'
  echo 'Say "cannot tell from the diff" rather than guessing.'
  printf '\n```diff\n'
  cat "$DIFF_FILE"
  printf '\n```\n'
} > "$WORK/prompt.md"
printf 'review-lane: model=%s effort=%s diff_lines=%s\n' "$MODEL" "$EFFORT" "$diff_lines" >&2
EXTRA=()
[ -z "$SCHEMA_FILE" ] || EXTRA+=(--output-schema "$SCHEMA_FILE")
rc=0
"$AGENT" exec --skip-git-repo-check -s read-only -C "$REPO" "${OVERRIDES[@]}" \
  ${EXTRA[@]+"${EXTRA[@]}"} -o "$OUT_FILE" "$(cat "$WORK/prompt.md")" \
  < /dev/null > "$WORK/banner" 2>&1 || rc=$?
cat "$WORK/banner" >&2
[ "$rc" -eq 0 ] || exit "$rc"
assert_banner "$WORK/banner" || exit 1
[ -s "$OUT_FILE" ] || { echo 'FAIL: no last message' >&2; exit 1; }
cat "$OUT_FILE"
