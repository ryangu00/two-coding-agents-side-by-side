# Open-book plan review

## Verdict first

Begin with SHIP-AS-PLAN / FIX-FIRST / REJECT and the three most important changes.
Write in English, at most 2,200 characters.

## Claim check

Compare each description of a borrowed method or API with the evidence pack.
Quote the pack where it disagrees. Say "cannot check" where the pack is silent.
Cover the supplied attack points with holds / does not hold and a reason.
Identify numbers without basis, mismatched borrowed evidence, and a simpler alternative.
For each finding give BLOCK / MAJOR / MINOR, section, reason, and a one-line fix.

## Implementation and evaluation

Give concrete implementations for the two underspecified sections named by the caller.
Explain the state fields, decisions, calibration, and applicable constraints supported by the pack.
Specify a replay procedure, holdout, acceptance criterion, proposal and decision roles,
and protection against self-reward. Mark missing prerequisites as unknown.

## Knowledge gaps

Separate training knowledge, evidence-pack support, and judgements supported by neither.
Never turn uncertainty into a verification claim.

## Allowed domains and tools

Tool-less reviewers must not claim to have fetched anything.
The tool-enabled reviewer may fetch identifier metadata from export.arxiv.org and
repository files from raw.githubusercontent.com only. Report exact URLs and what
was actually checked. Do not write the reviewed files. Sandbox and network
permissions must be set by the caller; this prompt does not enforce either.

## Evidence pack and plan

Append the plan and the public evidence pack here. For the offline exercise,
use only the local synthetic evidence; do not fetch the domains above.
