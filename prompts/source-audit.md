# Source audit

Review the supplied reports read-only. Fetch only their cited public URLs.
For offline fixtures, read the supplied local source snapshots instead;
state that no live source was fetched. Report SHA-256 of each file before and after.

## Lens 1: traceability

For every quoted clause, paper citation, and source-code claim, fetch the URL or
arXiv identifier and mark CONFIRMED / CONTRADICTED / NOT-FOUND / FETCH-FAILED.
Quote the actual wording where it differs. Check that identifiers resolve to the
named papers, and that descriptions of code match its actual inputs and behavior.
Check the distinction between the source's text and the report's inference.

## Lens 2: overreach

List conclusions beyond their evidence, vendor claims presented as measurements,
and consensus claims not supported by two independent sources in the report.
For any interpretation of terms, label the conclusion "from text" or "from inference".
A failed fetch is not evidence that the claimed source does not exist.

## Output

Return numbered findings, each with file, section, BLOCKER / MAJOR / MINOR,
what is wrong, and the exact fix. Finish with a one-line verdict for each report:
HANDSHAKE-OK or FIX-FIRST. Include the before-and-after hashes.
