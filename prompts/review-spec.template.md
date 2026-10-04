# Read-only code review

## Background and previous report

Supply the previous report and an itemized list of claimed fixes.
Keep this material separate from the subject diff; do not treat claims as evidence.

## Files and suites

List the exact reviewed files and complete test-suite commands.
Record subject SHA-256 before and after the review.
Do not modify the reviewed files or write to a database.
Tests may create and clean temporary files in a caller-designated scratch directory.
Use PYTHONDONTWRITEBYTECODE=1; for pytest, use -q -p no:cacheprovider.
Do not directly run tools that have production-state paths; use their isolated tests.

## Requirements

Run the complete suites first and report actual passes and failures.
For each previous finding, give fixed / partially fixed / unfixed with file:line evidence.
Grade new findings BLOCKER / MAJOR / MINOR, with file:line, trigger, consequence,
minimal reproduction, and smallest repair. Exclude style-only complaints.
Prioritize ordinary-use failures. Findings requiring a same-user malicious process
or extreme timing must state that premise and must not be graded above MAJOR.
Mark uncertainty "to be confirmed" and name the missing evidence.
Use one severity-bearing heading per finding; no severity in section headings.

## Delivery

Write the report to the caller's output path outside the reviewed subject.
Include a summary table, complete-suite results, and before-and-after hashes.
List the report and its size to confirm delivery. Do not claim an unrun test passed.
