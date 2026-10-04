# Model choice: task evidence before a default

The recorded decision separated difficult review from bulk extraction. Its
tests support a local choice for these tasks, not a ranking of available models.
The public scripts therefore use generic placeholders and require live users
to record account-specific availability themselves.

## Review baseline

The subject was the pre-fix snapshot reviewed in round 8 of the nine-round
series: routing-change evidence and catalog validation, with tests. The prompt
did not disclose the known-answer set. The direct runtime selected the flagship
tier at highest effort, and the job record's `request.model` was checked.

The spec required complete suites, actual pass counts, no reviewed-file changes,
and no database writes. Its known-answer baseline was three earlier issues.
The record called recall 2 of 3, but this was 1 full hit, 1 partial hit missing
an entire category row, and 1 miss. The model also found 4 additional real MAJOR
defects that earlier rounds had not reported; the operator re-checked and fixed
them. A MINOR concerned a missing fixture in the evaluation snapshot.

This was n=1, and the same model had seen the case before. It was not a fresh,
randomized test or evidence of complete recall. The result says that repeated
reviews of the same material can expose different issues.

## Extraction test

The original generator created 80 mixed-language operational log lines using
`random.Random(20260925)`. It drew from five text formats and required six fields:
time, host, service, status, latency in milliseconds, and an error enum. The
`line` field was a separate output index. Seconds were converted and rounded to
integer milliseconds. Five localized error labels mapped to the enum values.

The small tier at high effort ran once with its answer key withheld. All 80
rows, and all six fields on each row, were exactly correct. These are task
results, not a general accuracy estimate for operations extraction.

The public `gen_bulk_eval.py` preserves the seed, selection order, unit conversion,
format count, and enum mapping. Machine/service strings are synthetic. Because
all published files must be English, label phrases such as "out of memory"
replace the historical non-English labels. This removes the multilingual part
of the task; the public data is a reproducible adaptation, not the original test.

Use separate `--out-dir` and `--answer-key` paths. The generator rejects a key
inside the input directory, but directory separation alone does not withhold
the key from a broadly privileged reviewer. The historical access boundary is
part of the test condition; reproducing it requires an actual access restriction.

## Token counts and computed comparison

All usage and arithmetic are in [results](results.md#own-task-model-tests).
The extraction input was 217,265 tokens, of which 184,832 were cached, leaving
32,433 uncached. Output was 4,020, including 1,645 reasoning tokens.

Recorded small-tier rate weights per 1M tokens were 5 for input, 0.5 for cached
input, and 30 for output. Applying the recorded flagship weights to the same
token counts gives about 47 times the subtotal; the source's rounded account
was about 48x. This comparison did not run the flagship on extraction. Cache
share and rate assumptions are indispensable conditions, and account-specific
credit units and allowance percentages are not published.

The separate review baseline used 1,561,679 input tokens (1,422,592 cached) and
21,304 output tokens (8,878 reasoning), taking 7 minutes. It used a direct runtime
and the flagship tier. The main wrapper's historical default was an older model
that the account accepted; the two invocations must not be conflated.

## Effort and availability

The historical decision retained the flagship at highest effort for review and
selected the small tier at high effort for mechanical work. An external coding
benchmark cited in the record claimed about +5.6 points from high to highest
effort, no gain at a max tier, and about 45% higher cost there. That benchmark
was not run here, its source URL is not supplied, and the claim is not
independently verified. It is background to the decision, not new evidence.

The record also advised against changing effort during a review session because
it invalidates the prompt cache. No separate cache experiment is supplied here.
Re-evaluation triggers and a latest review date tied to retirement were recorded,
but no current retirement schedule or model availability is asserted.

A newer tier returned 400 as unsupported for the account. A forwarding layer
also changed a requested model to a nonexistent name, then retried without the
pin. Use the direct runtime and inspect the served-model evidence. One filtered
trace showed matching requested names in `response.created`, `in_progress`, and
`completed`; it was a single sample and was not stored.

The public effort pin and banner assertion remain an untested live proposal.
Passing the synthetic wrapper test verifies argument construction and rejection
behavior only. It cannot settle current model access, real reasoning effort, or
whether a different reviewer configuration converges sooner.
