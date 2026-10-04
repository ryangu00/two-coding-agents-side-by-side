# Open-book review with an execution record

The plan experiment compared two access conditions on the same design. It did
not compare models on a controlled independent benchmark. Its useful result is
the difference between internal consistency and first-hand source checking.

## Closed-book procedure

The first prompt supplied the plan only. It required findings with severity,
exact section, reason, and a one-line repair. Reviewers had to answer each of
the supplied attack points A through H with holds / does not hold and a reason.
They also had to name unsupported numbers, borrowed methods whose original
evidence used a different setting, and a simpler alternative when justified.

The verdict vocabulary was SHIP-AS-PLAN / FIX-FIRST / REJECT. The verdict and
three most important changes belonged first, with a 1,800-character cap.
Commands, other files, and network were forbidden. The public template preserves
this structure but requires the caller to supply fresh axes and a public plan.

Such a review could find unsupported go/no-go numbers, circular reasoning,
missing hysteresis, or an internal contradiction. It could not establish that
the plan had accurately described an external paper or hosted API.

## Open-book procedure

The second prompt appended an evidence pack: abstracts, the prior design,
measurement records, and an official API description. Reviewers compared claims
line by line, quoted the pack where it differed, and said "cannot check" where
it was silent. They also had to provide concrete implementations for two
underspecified sections and an executable evaluation procedure.

The gap declaration separated training knowledge, evidence-pack support, and
claims supported by neither. The response limit was 2,200 characters. Only the
tool-enabled reviewer could fetch from `export.arxiv.org` and
`raw.githubusercontent.com`, returning URLs and verification results.

The historical open-book call used a workspace-write sandbox with network
enabled; "do not write files" remained a prompt condition. It must not be
described as the same read-only sandbox used for the closed-book call. The
public external-command interface leaves sandbox/network settings explicit in
the caller's argv. A prompt domain list is not network enforcement.

## What changed in the findings

Both rounds returned FIX-FIRST after completed outputs were available, but their
grounds differed. The open-book round found source/plan mismatches about API
parallelism and missing constraints, and an underspecified evolution loop with
no holdout, criterion, proposal/decision separation, or self-reward protection.

The pack also exposed errors made by the plan writer: a prohibition cited to the
wrong decision record, a derived 68-week figure presented as source text, an
evaluation protocol presented as production practice, an unsupported eight-week
cooling period, and omitted parallel API behavior. These are dated observations
from that plan, not recommendations for another design.

The [complete procedure and reconciliation tables](results.md#plan-review-procedure)
retain sizes, times, output lengths, and adoption counts. The pair was run once
on 2026-09-27. It does not measure a general open-book uplift.

## Credibility before reconciliation

The tool-enabled reviewer executed 5 shell commands fetching 7 distinct URLs.
One API request covered 9 identifiers; the other requests read 6 repository
files. The identifiers resolved correctly, and the reviewer declared that it had
not read full papers. This is narrower than "the literature was verified".

Two tool-less reviewers correctly identified their evidence as the supplied
pack. Another wrote three `curl` verification claims and asserted that two
identifiers were not found. With no tool interface it could not have performed
those checks; the real fetch found both. Its unsupported verification claims
were rejected, while usable comparisons against the pack were considered.

The historical summary's "curl calls: 3" came from grepping the word in the whole
log. Matches included prompt text and narration. `count_executions()` in the
public fanout instead accepts only structured `CommandExecution` completions.
It counts executions, not distinct URLs or successful fetches. The caller must
still inspect actual argv/results to establish those stronger claims.

## Fanout and empty completions

`scripts/plan-review/fanout.py` is the English, configurable rewrite of the
historical shell-embedded clients. Each model receives the same prompt, with
completion cap 20,000 and temperature 0.4. The transport timeout is an
implementation setting, not a measured latency.

For each attempt it retains text, character count, finish reason, token total,
served-model field when present, elapsed seconds, and cap. Exactly the observed
empty/length condition triggers a rerun at 60,000 with verdict-first,
1,800-character, short-thinking wording. Both attempts remain in the output.
An empty stop, transport error, exhausted retry, or nonempty truncated answer
is not reported as a complete review.

| Setting | Source | Offline behavior |
|---|---|---|
| `REVIEW_ENDPOINT` | Environment; default loopback chat-completions URL | Unused with `--mock-fixture`. |
| `REVIEW_API_KEY` | Environment only | Optional; no credential file read. |
| `REVIEW_MODELS` | JSON array in environment | Default `example-model`, a synthetic placeholder. |
| `TOOL_REVIEW_COMMAND` | JSON argv array in environment | Optional; caller supplies sandbox flags. |
| `--prompt` / `--out` | Explicit paths | Input prompt and attempt report. |
| `--mock-fixture` | Explicit canned completion file | No HTTP request; external reviewer command is ignored in this mode. |

The optional command supports `{prompt}`, `{output}`, and `{log}` placeholders.
It receives closed stdin and is run directly, without shell evaluation. It must
write a report and a harness-format JSONL log to fresh paths. The example checks
for an explicit sandbox flag, not the sandbox's effectiveness; runtime policies
remain the caller's responsibility. Missing structured logs yield an unknown
execution count, not zero verified executions.

Tests route serialized requests through a standard-library HTTP handler backed
by byte streams. No socket is opened. The CLI's canned-completion mode is also
offline; neither path invokes a model or fetches a source.

## Avoid supplying the findings in the prompt

A later review that day supplied four attack seeds; three tool-less reviewers
restated them almost one for one. That assessment was the operator's judgement,
not a measured dependence score. The recorded response was to use seeds as
questions or axes, retain a fresh tool-enabled reviewer, and weight first-hand
tests. A credibility table remains necessary even when every verdict agrees.
