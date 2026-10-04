# Pitfalls: symptom, cause, repair, and evidence

These are dated lessons from the supplied record. An implemented public adaptation, a historical observation, and an untested proposal are labeled separately. Full counts and dates are in [results](results.md).

## Shared guards

The first failure is missing observation, not a clean session. Parse both hosts through the same event mapper, and make unsupported input visible. The public example implements unparsed input and per-file missing-target alerts; those are changes to the historical examples, not claimed historical repairs.

| Symptom | Root cause | Fix |
|---|---|---|
| Every agent-B session is "clean", ledger shapes empty | the shared judge parses only agent A's transcript shape | map `item_completed`; add a test that replays one real sample of each host through every shared hook and asserts a non-empty parse |
| Agent B's sessions still judged clean for MCP-server-mode sessions | those sessions write no `item_completed` | public extraction: report non-empty input with zero parsed events as unparsed; historical implementation did not |
| Cloud dispatches from agent B all rejected | stale egress-gate copy with an obsolete self-test canary | share the file; see [the prior incident](https://github.com/ryangu00/agent-guards-that-fail-silently) for the earlier repair |
| The memory writer wrote a session id into agent A's "resume pointer" file | agent B's session ids are also 36-character UUIDs (a different version), so "36 characters" is not a test for "agent A's id" | identify the host by transcript path, not by id shape (this item is from our notes; we did not re-verify it in code) |
| A reminder never reaches agent B's model | `systemMessage` is shown to the human only | accept; if the model must see it, use a blocking decision (not recommended for warn-only guards) or session-start `additionalContext` |
| An edited shared hook breaks the other agent | links share behaviour immediately | after any edit to a shared hook, run its self-test against both hosts' sample payloads before leaving the file |

A link shares edits immediately. A byte comparison detects divergent replacements, but cannot prove that a same-byte file is still a link unless the optional link check is enabled. A B-only filename is intentionally outside the shared-name comparison. The host-specific Stop branch must also be tested independently of guard criteria.

## Reviewer lane

These symptoms came from separate layers: provider transport, model metadata, stdin, shell behavior, and review scope. The historical wrapper was checked with a stub on 2026-10-03. The effort pin and banner assertion below remain an untested live proposal.

| Symptom | Root cause | Fix |
|---|---|---|
| "Model metadata for X not found" on every turn | catalog override replaced built-in metadata | own catalog containing the pinned model; selftest counts the warning |
| Reviews cut off mid-task | context window fell back to a small default | same |
| `0 warnings` after pointing the catalog at `/dev/null` | the process died before running | the catalog must exist and parse; selftest requires an exact-line reply |
| Selftest passes though the model said nothing | substring match found the echoed prompt | exact-line match (`grep -cx`) |
| Hang in a background run | agent waits on stdin | `< /dev/null` |
| Wrapper aborts under `set -u` on macOS | bash 3.2 empty array | `${arr[@]+"${arr[@]}"}` |
| Review passes on a diff of 82 lines | the review subject was not the change set | build a base that puts the whole subject in the diff; report diff size in the packet |
| Reviewer verdict looks shallow | effort fell to default when user config was skipped | untested live proposal: pin the effort, print and assert the banner |

In the first real use on 2026-07-31, the bounded review found an observe path swallowing a record-write failure. That result supports checking failure visibility, not treating an apparently successful invocation as a verdict. The public tests also reject a nonzero agent exit even when an exact reply is present.

## Model and effort choice

The own-task tests were a single review baseline and a single extraction run. They cannot establish a universal model ranking or a stable cost advantage outside their token mix.

| Symptom | Root cause | Fix |
|---|---|---|
| Wrong model served or a model silently substituted | forwarders rewrite flags; vendors may route differently | check the served model from the job record or the CLI banner; in one sample the server's `response.created`, `in_progress` and `completed` events all carried the requested model (single sample, filtered trace, not stored) |
| Savings claims that do not survive recomputation | credits depend on list rates and cache share | recompute from token counts, as above |
| "Review the repo" without a diff | no bounded subject | Chapter 2 |

A forwarding layer once interpreted -m in task text as a model selector and failed after 5 seconds. Another changed the model name, received 400, and retried without the requested pin. The recorded repair was a direct runtime invocation with explicit settings and a checked job record. Long tasks were put in a spec file rather than passed through a flag-rewriting intermediary.

## Open-book plans

The plan experiment was one pair of rounds on 2026-09-27. Empty outputs were observed once per affected reviewer, and the fabricated verification came from one tool-less draft; repetition was not performed.

| Symptom | Root cause | Fix |
|---|---|---|
| Two reasoning models returned empty text with `finish_reason=length` | the completion cap (20,000) was consumed by reasoning; the reported total of 38,366 and 37,396 tokens minus the cap leaves about 18.4K and 17.4K prompt tokens | detect `chars == 0 and finish == length`, re-run with a larger cap (60,000), put "verdict on the first line, at most 1,800 characters, keep thinking short" in the prompt. The re-runs produced 2,501 and 3,923 characters in 66 s and 196 s |
| A reviewer's findings echo the orchestrator's seeds | the prompt contained conclusions | seeds as axes only; at least one fresh, tool-enabled reviewer |
| "Verified" in a review with no tool | no execution path exists | credibility table first; discard unverifiable verification claims |
| Reconciliation adopts everything | consensus mistaken for correctness | reject a finding when a tool-enabled reviewer has checked the opposite (two such rejections in round 2) |

A verdict-first prompt did not itself enforce length or truthful access claims. The rerun outputs exceeded the requested character bound. Preserve actual character counts and finish reasons; first-hand execution records determine whether a fetch occurred. A credibility table must precede reconciliation even when reviewers agree.

## Source audits

These rules describe the audit method. The reports and vendor-specific terms or conclusions are not published. The 34-finding error-type table is a one-rater interpretation, not a model accuracy benchmark.

| Symptom | Root cause | Fix |
|---|---|---|
| Report says "consensus" | one practitioner's public practice or internal reports citing each other | require two independent sources; count internal notes as one |
| "Verbatim" quotes differ from the page | a model paraphrased inside quotation marks | the audit compares quoted text with the fetched text |
| Example command silently does nothing | the cited code reads a nested key | run the exact example against the cited code at a fixed revision; check how many records matched |
| A bound stated as a fixed floor | the original is conditional | restate with its condition |
| Interpretive verdicts | inference from a neighbouring clause | label each interpretation "from text" or "from inference" |

The audit found source misreadings with real identifiers. Correcting the citations list would not repair the conclusions. The later method draft also selected alternatives on its locked test set; the repair moved selection to validation and reserved the locked-set read until choices were frozen.

## Convergence and scope

The series use unequal subjects and review strength. Series B changed severity vocabulary after its first round; effort per round is missing from the historical reports. The blocker-round threshold is an operational trigger, not a measured cutoff.

| Symptom | Root cause | Fix |
|---|---|---|
| Round count keeps growing on one target | each fix opens a new path through writable state | reachability triage; after three BLOCKER rounds on one target, re-scope |
| Reviewer sees its own earlier verdict | review outputs inside the reviewed tree | outputs outside the subject; record hashes |
| Tests pass, reviewer still finds the defect | tests generate their own expected values | real producer to real consumer tests; reviewer-written cases kept as regression tests |
| Back-filled data counted toward a gate | after-the-fact records | only moment-of-action records count; back-fills are displayed, not counted |
| Reviews of unequal strength compared | effort and subject not recorded | ledger fields `reviewer` and `subject_sha_*` |

The record alternates between after three and more than three blocker rounds. Keep the underlying decision explicit: can ordinary use still reach the defect, and can the proposed boundary ever exclude the actor who controls its state? An accepted-risk stop is distinct from a clean round. Do not manufacture elided privacy-scanner round counts to draw a smoother curve.

## Review artifacts can invalidate the subject

On 2026-09-24, a non-repository start failed, then an 82-line diff omitted most of the intended bundle. Building a base that included the whole bundle changed the actual review subject; it was not simply another opinion on the same input. Later, prior stderr and conclusions entered the next diff and exposed the reviewer to its earlier verdict and rebuttals. Keep outputs outside the subject and record hashes and diff size.

## Prompt-only access boundaries

One source review ran in a workspace-write sandbox despite a read-only prompt. The unchanged before/after hashes established that its subject files were not modified. They do not prove that the sandbox prevented writes. The main public wrapper passes -s read-only; the optional external plan reviewer requires caller-supplied runtime flags.

## One-time safety-filter stop

A prompt requesting constructed bypasses and proofs of concept was stopped after 29 seconds, noticed 25 minutes later when the session log stopped changing. Rewording it as a read-only review of omitted validation with reproducible cases ran. This happened once; other runs used similar adversarial language, so the trigger is not characterized and the wording is not a reliable workaround.

## Public-example boundaries

- A synthetic reply validates wrapper logic, not vendor authentication or model availability.
- A parsed event is not a verified write receipt. Command output and exit status remain data for a separate policy.
- JSON Schema validation proves shape, not that tests ran, hashes were honestly collected, or a risk was accepted.
- A sibling answer-key directory is not an access-control boundary. The extraction reviewer must actually be unable to read the key.
- The English-only generator removes the original multilingual labels; the historical extraction result does not measure this adaptation.
- No daily scheduler, private guard policy, original report, or live model environment is installed by this book.
