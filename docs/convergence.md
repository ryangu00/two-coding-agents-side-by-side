# The convergence ledger and the stopping decision

The series here were all reviewed by agent B, with effort per round missing from
the reports. They are histories with different subjects, scopes, and acceptance
decisions. Their finding counts cannot be treated as a common benchmark curve.

## Series A: zero blocker/major with passing tests throughout

The nine reports and specifications read for this series are dated 2026-09-25.
They cover a routing-change evidence gate, a catalog validator, and supervision
tools. The full [round table](results.md#series-a-routing-evidence-catalog-validation-and-supervision)
retains confirmed and unconfirmed findings, prior-fix verdicts, and suite results.

Confirmed findings of any severity were 16, 12, 9, 11, 6, 5, 2, 3, 2. The
blocker-plus-major sequence was 13, 12, 7, 9, 6, 5, 2, 3, 0. Both expose increases,
not monotonic decay. Every suite run to completion passed. Round 4 collected
tests but did not run the suites; its file-write prohibition prevented execution.

Some reviewer-written checks deliberately asserted the current buggy behavior.
A pass meant a successful reproduction, not a correct implementation. The
reviewer's independent cases and the ordinary regression suite measured different
things, and the ledger must retain that distinction.

Two additional regressions came from the implementer's own fixes and were found
by real-path tests. A process-identity check compared locale-dependent start-time
text, so shell and scheduler output disagreed and supervision was released.
The repair trimmed whitespace on only one side and reproduced the symptom.
The 21 green tests had constructed their expected strings rather than using the
real writer. Test a new safety check's own failure behavior and connect the real
producer to the real consumer.

The related gate and validator are published in
[llm-gateway-routing-in-production](https://github.com/ryangu00/llm-gateway-routing-in-production).
This book does not duplicate their implementation. Independent incident-shaped
cases also connect to
[local-llm-bakeoff-measurement-pitfalls](https://github.com/ryangu00/local-llm-bakeoff-measurement-pitfalls).

## Series B: a target the writer could keep forging

Across five rounds on 2026-09-27, new findings were 18, 12, 11, 4, 11 and blocker
counts were 9, 3, 1, 2, 3. Each round repaired the principal prior defect but
found a new path through state that the executing actor could write. The final
round switched to the flagship tier and said not to merge.

The decision stopped the loop and re-scoped the gate. Actor-writable local state
can catch mistakes; it cannot be the identity boundary for an adversary who can
forge that state. An identity-separated acceptor was required for that target.

The record's prose says "more than three rounds" and its compact rule says
"after three". Preserve that difference: repeated blockers trigger a reachability
discussion, not an experimentally established cutoff. Review strength changed
in the series, so the last increase cannot be isolated to code changes alone.

## Series C: scope rather than zero

The privacy-scanner history recorded 52 findings in 26 rounds, all judged true
and fixed, including 15 false greens and 3 regressions from previous fixes. It
never reached zero. Ordinary repository use remained blocking; paths requiring
special plumbing were documented as boundaries under the agreed threat model.

Only the first ten rounds and the last were enumerated. The source's wording
about 16 rounds "in between" is inconsistent with separately naming the last.
The [result note](results.md#series-c-privacy-scanner-scope-and-incomplete-round-detail)
retains the 21-finding subtraction subtotal without fabricating missing rows.

The work grew to 2,497 added lines, 32 commits, and a suite growing from 124 to
197 tests. It was reported as a scope alarm. A numerical zero requirement would
not explain what the review was still buying or where acceptance should stop.

## Series D: accepted risk is a distinct outcome

The shadow-decision-log sweeper had three REJECT rounds on 2026-10-03. Each round
was fixed; the loop then stopped by decision, with remaining items registered
as accepted risks. There are no supplied per-round finding counts to invent.

One repair withdrew a rule counting back-filled records within a day toward a
threshold. Only moment-of-action records counted; back-fills remained visible
without satisfying the threshold. The review outcome was an explicit boundary,
not a statement that every reviewer agreed the subject was clean.

The additional de-identification series is linked only in
[decision-record-deidentification-gates](https://github.com/ryangu00/decision-record-deidentification-gates),
including its warning that counts mix repairs with a changed counting rule.

## Proposed ledger, not a recovered production artifact

| Field | What the round must retain |
|---|---|
| `round` | Position in this series. |
| `subject_sha_before`, `subject_sha_after` | SHA-256 for every reviewed file; do not silently substitute a changed subject. |
| `reviewer` | Family, served model, effort, sandbox; record unknown values as unknown. |
| `prior` | Fixed, partial, or open for each earlier finding, with code-line evidence. |
| `new_confirmed`, `new_unconfirmed` | Separate counts by severity. |
| `tests` | Complete-suite passes/failures; collection and not-run remain explicit. |
| `regressions_from_fix` | Findings introduced by earlier repairs. |
| `reachability` | Ordinary use, special means, or unknown, with premises. |
| `stop_decision` | Continue, stop-and-fix, stop-and-rescope, or stop-with-accepted-risk. |

`configs/ledger.schema.json` formalizes that proposal. The example row is entirely
synthetic; its subject hashes refer to the shipped synthetic diff and its test
list is empty, so it does not fabricate a completed suite. Schema validation
checks shape, not whether the claimed tests ran or the findings are true. The
standard-library validator implements only the keywords used by the supplied
schemas and rejects unsupported keywords encountered during validation.

## Tally convention and its limits

`ledger_from_reports.py` keeps the original heading-based method. A line starting
with `#` and containing BLOCKER, MAJOR, or MINOR counts as a finding. A heading
with `unconfirmed` or `to be confirmed` is counted separately. Body prose and
summary tables do not count. The heading vocabulary is case-sensitive; uncertainty
markers are case-insensitive.

Use `--vocabulary high-medium` for BLOCKER/HIGH/MEDIUM. This does not silently map
HIGH to MAJOR or MEDIUM to MINOR. Record a changed ruler rather than comparing
unqualified totals. Use one severity-bearing heading per finding; severity words
in an unrelated heading will otherwise be counted. The script counts headings,
not unique defects, truth, fix status, or an acceptance decision.

The review-spec template preserves the historical ordering: previous report and
claims, exact files and suites, requirements, and delivery. Complete the fields
before dispatch; a template with unknown targets is not a runnable review spec.

The stopping rule is a decision about reachable defects and scope. Zero above
minor can inform it, but green tests or a declining count cannot make it for you.
