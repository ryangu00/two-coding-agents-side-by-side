# Source audits: real citations can support false claims

All 38 arXiv identifiers in the two historical reports resolved to the named
papers. The audit still found 34 issues. The problem was chiefly interpretation,
scope, basis, and omitted qualifications, not fabricated identifiers.

This chapter publishes the audit method and classification statistics only.
The original reports, audits, and vendor-specific terms or conclusions are not
included. The tiny public reports are planted exercises, not excerpts.

## Prepare the audit subject

Identify the exact report files and hash each before review. Restrict the task
to their cited public sources and require a status for every claim. The actual
2026-09-22 review had workspace-write and network enabled; its prompt prohibited
file changes. Identical before/after SHA-256 values established that the reports
were unchanged during that review. The prompt alone was not an access control.

Some public pages could not be fetched. Their claims stayed unverified. An
unlocatable repository was not counted as independent support. A failure to
find something in the checked sources was not treated as a universal negative.

## Lens 1: traceability

For every quotation, paper claim, and source-code statement, follow the actual
reference. Check that the identifier names the cited work and that the text or
code says what the report claims. Where it differs, quote the source and give
the exact repair, rather than merely saying "citation seems weak".

| Status | What it records | What it does not establish |
|---|---|---|
| CONFIRMED | Checked source supports the particular claim | Every wider inference from that source. |
| CONTRADICTED | Checked source differs from the claim | That all other claims in the report fail. |
| NOT-FOUND | The checked reference could not be located | That no such source exists anywhere. |
| FETCH-FAILED | Retrieval did not succeed | Whether the source would support the claim. |

A quoted sentence must match the source. A description of training code needs
the actual input shape and implementation. One historical command example used
the wrong outer input shape and would be treated as empty. The recorded repair
was to check the exact example against code at a fixed revision and count the
records actually consumed. The private command and report are not published.

## Lens 2: overreach

Separate a source's statement from a measured result, a single demonstrated
case from a general conclusion, and a development-set result from a locked-set
evaluation. A model can cite the correct paper while swapping the metric or the
object the result applies to. A conditional bound must retain its condition.

The historical review also found a memory estimate using the wrong weight
precision, a guarantee about prediction-set coverage presented as an accepted-set
error guarantee, and an inconsistent adoption rule. These are different errors;
grouping them all as "hallucinations" would hide the repair needed.

Require independent support before using the word consensus. Repeated internal
notes citing each other do not supply independent sources. In the later method
draft, a 37-row table labeled 27 rows STANDARD, many with a single source, while
the draft itself demanded two sources. The resulting verdict was "recipe is not
consensus".

## Reconcile and audit revisions

The initial audit took 10.7 minutes and produced a 27 KB report with 34 findings.
Both subjects were FIX-FIRST. The edit pass marked 34 of 34 APPLY and none
REJECT, with targeted replacements and net line changes +2 and -2. The operator
then spot-checked 4 blocker items. That adoption rate is an observation, not a
rule to accept every reviewer suggestion.

The review and reconciliation count 4 BLOCKER, 25 MAJOR, and 5 MINOR. A working
summary said 24 MAJOR and 6 MINOR; the table uses the agreeing primary tallies.
The [error-type table](results.md#report-findings-by-error-type) is a later,
one-rater classification from headings, with judgemental category boundaries.

A method draft produced from the repaired reports received another audit:
8 findings, including 2 BLOCKER. Besides unsupported consensus, it had used a
locked test set to choose alternatives. The repair put selection on validation
and reserved the locked set for a single read after choices were frozen.

Another long document received separate numerical and source/completeness
audits, then new consistency and fact audits for later additions. Its version
history and edit counts appear in results, with no date invented. Correcting an
earlier version did not make new sections inherit correctness.

## Offline exercise

Use `prompts/source-audit.md` with `fixtures/audit/quotation-report.md` and
`fixtures/audit/consensus-report.md`. Their cited `source.md` is a synthetic local
snapshot. It states that the sample accepted the supported input and does not
supply independent consensus evidence.

The first report reverses the source's wording. The other generalizes a single
example to every input and calls that independent consensus. Compare the reports
with the snapshot, assign traceability and overreach findings, then inspect
`fixtures/audit/expected.md`.

The test suite checks the planted differences and unchanged file hashes. It does
not pretend to run a source-aware model or perform a legal review. For a live
audit, source retrieval and claim-by-claim judgement remain additional work.

The rule is to audit meaning and scope, retain missing evidence, reconcile each
repair explicitly, and repeat the audit when a revision adds new content.
