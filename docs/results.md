# Results and evidence boundaries

Historical tables are transcribed from the supplied fact record, with private names and account-specific units removed. They have not been independently re-run here. Public fixtures are synthetic and are never substitutes for these measurements.

The shared-hook incident, mirror history, and replay counts below are a compact reference to [agent-guards-that-fail-silently](https://github.com/ryangu00/agent-guards-that-fail-silently), cases 9/10 and its canary/receipts chapters. This book adds protocol mapping and runnable extractions.

## Shared hooks and rollout observations

Conditions: inventory on 2026-09-25; replay window and sample sizes are stated per row; these are historical observations, not runs of the public fixtures.

| Measurement | Value | Condition |
|---|---|---|
| Same-named hook files in the two directories | 12 | 2026-09-25 |
| Stale copies | 5 of 12, at July/August versions, oldest 79 days | 2026-07-08 to 2026-09-25 |
| Intentional agent-B differences among the differing copies | 0 | segment diff, 2026-09-25 |
| Symlinks in agent B's hook directory now | 12, plus 1 agent-B-only file | read 2026-10-03 |
| Mirror check in the daily canary | first record 2026-09-26; 10 records with it as of 2026-10-03; 0 red | canary history |
| Rollouts examined | 89 | last 5 days as of 2026-09-27 |
| Tool calls that are the model's own JavaScript exec | 95% | same 89 rollouts |
| Rollouts without any `item_completed` | 3 of 89 (the sessions started through agent B's MCP-server mode; originator differs) | same |
| Replay of 237 agent-B session states after the mapping | fire 60 (infra 56, research 3, infra+project 1), clean 177; before the mapping all 237 had empty `shapes` | published in the sibling book |
| Auditor on the last 2 days (30 rollouts) | clean 30 -> fire 13, clean 17 | published in the sibling book |
| One recent single session, our own count, 2026-10-03 (n=1) | 74 `item_completed` (25 CommandExecution, 14 FileChange, 26 Reasoning, 8 AgentMessage, 1 UserMessage) beside 30 `custom_tool_call` and 30 outputs | counts only |

The recent single session is a count-only observation (n=1); it is not an execution-rate estimate. The shipped synthetic rollout has 8 lines: metadata and a forged call map to no events; successful and failing commands retain their exit status; added and updated paths map to Write and Edit; MCP and WebSearch calls map; AgentMessage does not.

## Original mirror function

Conditions: temporary directories, original function, 2026-10-03; the public extraction catches missing targets per file and offers a stricter link option.

| Case in the agent-B directory | Result |
|---|---|
| symlink to the agent-A file | no alert |
| regular file, byte-identical to the agent-A file | no alert (limit: the replacement is only noticed at the first divergent edit) |
| regular file, different bytes | alert |
| name only in agent B's directory | ignored |
| name ending `.bak-...` | ignored |
| dangling symlink whose agent-A counterpart exists | the function raises `FileNotFoundError`; in the daily job each probe is wrapped, so the run records a red "probe crashed" entry |

## Reviewer lane incidents

Conditions: original lane and dated configuration; warning comparison used one call each; transient failures were observed over one evening only.

| Measurement | Value | Conditions |
|---|---|---|
| Consecutive failed dispatches before diagnosis | 7 | 2026-07-31 |
| Runs that "started but produced no report" | 4, all explained by the catalog replacement | same |
| Router endpoints | `/v1/messages` 200, `/v1/chat/completions` 404, `/v1/responses` 404 | router 2.0.0 |
| Metadata warnings | 1 with router catalog, 0 with own catalog | measured on one call each |
| Tokens for a bare one-sentence prompt | 23,990 | 2026-08-16, config with 5 MCP servers and 30+ plugins, no overrides |
| Saved by `--ignore-user-config` | about 24K tokens per call | our workday notes, same date |
| Top-level config on 2026-08-16 | sandbox full access, approval never, written by the vendor's desktop app | version 0.144.1 |
| Daily canary: lane red | 3 records (2026-08-19, 08-20, 08-21), each `FAIL: no reply from the model (transport)` | records that carry the check; published in the sibling book |
| Old driving channel (agent B's MCP-server mode): transient auth errors | 4 of 23 calls (17.4%) in one evening, including two calls started at the same moment (one succeeded) and one non-concurrent call | 2026-07-05; mitigation: retry twice with 3 s and 6 s back-off; one observed self-heal; not re-measured since; cause unconfirmed by the vendor; reported upstream (the two issues were merged as duplicates) |

Historical first successful review on 2026-07-31: NEEDS CHANGES; it found an observe path swallowing a record-write failure. The repair added an explicit recorded field, stderr evidence, and a test; the suite then had 124 tests. The 0.144.1 to 0.147.0 upgrade on 2026-08-16 had a green self-test before and after.

Coverage failures on 2026-09-24: a non-repository exit 2, then an 82-line diff that left most of the 7 attack surfaces outside the subject; the next full-bundle round found 2 BLOCKER and 4 MAJOR. The miss cost about 40 minutes. Three review rounds printed reasoning effort: none (rated PLAUSIBLE, not fixed in the historical wrapper). Round 2 covered 2,227 lines in at most 84 seconds (11:00:17 to 11:01:41); round 3 covered 3,639 lines in about 3 minutes. Round 3 added 3,409 lines, including 2,326 lines of earlier stderr (about 68%).

A safety-filter stop after 29 seconds was noticed 25 minutes later (observed once; trigger not characterized). A forwarding layer misread prompt text containing -m as a model flag and failed after 5 seconds. These are incident timings, not latency benchmarks.

## Original wrapper self-test

Conditions: stub agent, redirected binary and catalog paths, 2026-10-03; these results do not validate a live effort pin.

| Stub behaviour | Wrapper exit | Output |
|---|---|---|
| prints `LANE_OK` on its own line | 0 | `SELFTEST OK`, warnings 0, replied 1 |
| echoes the prompt only | 1 | `FAIL: no reply` (the prompt contains the string, but not as an exact line) |
| prints a "metadata ... not found" warning and `LANE_OK` | 1 | `FAIL: model metadata missing` |
| prints nothing | 1 | `FAIL: no reply` |

Recorded review argv contained exec --skip-git-repo-check -s read-only, --ignore-user-config, model_provider, model, and model_catalog_json. The packet began the prompt. Non-repository input and an empty diff each exited 2. The public wrapper additionally checks process status and the proposed model/effort banner contract.

## Own-task model tests

Conditions: review baseline n=1 and bulk extraction n=80 rows in one run; run dates not separately recorded; the review subject was familiar to the reviewer family.

| Test | Result | Time / token usage | Conditions |
|---|---|---|---|
| Review baseline, flagship tier, highest effort | recall of known issues counted as 2 of 3 by the record (1 full hit, 1 partial hit that missed a whole category row, 1 miss); 4 additional real MAJOR findings that nine earlier rounds had not reported (all re-verified by the orchestrator on the production code and fixed); 1 MINOR caused by a missing fixture in our evaluation snapshot | 7 minutes; input 1,561,679 tokens (cached 1,422,592), output 21,304 (reasoning 8,878) | n=1 run; the same case had been reviewed by the same model before |
| Bulk extraction, small tier, high effort | 80 of 80 rows exactly right; each of the six fields 80 of 80 | input 217,265 (cached 184,832), output 4,020 (reasoning 1,645) | n=80 rows, one run, answer key withheld |

The review recall label "2 of 3" includes a partial hit: 1 full, 1 partial that missed a whole category row, 1 miss. It must not be read as two complete recoveries. The 4 additional MAJOR findings were re-verified and fixed; the MINOR was a missing fixture in the evaluation snapshot.

The extraction used random.Random(20260925), five formats, and six extracted fields; line is an additional index. The historical mixed-language labels are replaced with English phrases in the public generator, so public fixtures are not the identical language task.

## Cost arithmetic without account-specific units

Conditions: computed from the extraction token counts and recorded list-rate weights; the flagship extraction was not run; no currency, credits, or allowance percentages are reported.

| Quantity | Small tier | Flagship (computed on the same token counts, not run) |
|---|---|---|
| Uncached input tokens | 217,265 - 184,832 = 32,433 | same |
| Rate-weighted subtotal / 1M | 32,433 x 5 + 184,832 x 0.5 + 4,020 x 30 = 375,181 per million = 0.375 | 32,433 x 250 + 184,832 x 25 + 4,020 x 1,250 = 17,754,050 per million = 17.75 |
| Ratio | | about 47 (the source record says about 17.6 and about 48x; the small difference is rounding of the same inputs) |
| Review check | | 139,087 x 250 + 1,422,592 x 25 + 21,304 x 1,250 = 96,966,550 per million = 96.97, matching the recorded rounded subtotal "about 97" |

Recorded rate weights per 1M tokens: small input 5, cached input 0.5, output 30; flagship multiples 50, 50, and 41.7. The table preserves both recomputed about 47 and the record's rounded about 48x. The baseline review and extraction ran different model tiers through different entry points; the historical wrapper default was not the baseline model.

## Plan review procedure

Conditions: one plan, paired rounds on 2026-09-27; gateway reviewers had no tools; tool-enabled reviewer access changed between rounds.

| Item | Round 1 (closed-book) | Round 2 (open-book) |
|---|---|---|
| Prompt size | 13,626 bytes (plan 12,081) | 58,401 bytes (evidence pack 46,614) |
| Tool-enabled reviewer | agent B, read-only sandbox, no network, highest effort; 0 shell executions; 40,129 tokens | agent B, workspace-write sandbox with network on, highest effort; 5 shell executions; 84,696 tokens |
| Open-weight reviewers | via gateway, no tools, completion cap 20,000 tokens | same |
| Wall time | 12:38:34 to 12:41:06 (2 min 32 s); the three gateway reviewers took 11 s, 21 s and 152 s | 12:50:45 to 12:54:17 (3 min 32 s) |
| Output | 4 of 4 non-empty (2,990, 3,028, 2,439 characters from the gateway reviewers; 4,516 bytes from agent B) | 2 of 3 gateway reviewers returned 0 characters (see pitfalls) |
| Verdicts | 4 of 4 FIX-FIRST | 4 of 4 FIX-FIRST, but now about two underspecified sections being empty shells |
| Reconciliation | 10 consensus findings (3 or more of 4) all adopted; 8 single-reviewer findings (6 adopted, 2 partly); 3 disagreements logged | 10 consensus findings; 11 single-reviewer findings adopted; 2 rejected; 6 errors by the plan's author recorded |

## What the plan rounds could find

Conditions: examples from the same pair of rounds on 2026-09-27, not an independent benchmark.

| | Closed-book consensus (examples) | Open-book consensus (examples) |
|---|---|---|
| Kind of finding | go/no-go numbers without basis; a contradiction with an earlier measurement ("68 weeks needed for the online metric" versus a 4-week loop); a gate with nothing to verify for judgement-type deliveries; egress boundary relying only on labels; a local model asked to generate where it had only classification evidence; a circular accuracy argument; no hysteresis | the plan described the borrowed methods and the hosted API differently from the evidence pack (the API takes several questions on one state in parallel, not one request per question); two hard constraints from the API's description were missing (a non-English check had to be run first; the model version had to be pinned and re-calibrated per version); the self-evolution loop was an empty shell (no holdout, no criterion, no who-proposes-who-decides, no protection against self-reward); a "deliberate" cooling period had no source; the prohibition that drove a design decision was cited to the wrong internal record |
| Needed outside material? | no | yes |

## Reviewer credibility before reconciliation

Conditions: open-book round on 2026-09-27; execution evidence exists only for the tool-enabled reviewer; its full-paper reading was not established.

| Reviewer | Real research? | Note |
|---|---|---|
| tool-enabled (agent B) | yes: 5 shell executions fetching 7 distinct URLs (one preprint-API request listing 9 identifiers, 6 raw repository files), all on the two allowed domains; all 9 identifiers resolved to the named titles; checked one repository's README for the claims; stated that it had not read the papers' full text | the only reviewer with first-hand verification |
| open-weight reviewer 1 | open-book, stated "I have no curl; identifiers and counts can only be taken from the pack" | after a re-run, 2,501 characters; most detailed claim-by-claim check |
| open-weight reviewer 2 | open-book, stated that everything came from the pack | after a re-run, 3,923 characters |
| open-weight reviewer 3 | open-book but wrote "checked with `curl -I ... -> 200`" three times (lines 51, 56, 66 of its draft) and, in its own gap declaration (lines 178-180), said it had fetched the preprint API and that two identifiers "were not found in the API" | the gateway channel has no tool; it cannot have run anything. The tool-enabled reviewer found both identifiers present. Its claims of "verified" and "not found" were not used; its claim-by-claim comparison was. Star counts for two repositories also appeared only in this draft; nothing in the pack contained them and the tool-enabled reviewer did not fetch them, so they remain unverified |

Empty-output reruns: completion cap 20,000 was exhausted with total tokens 38,366 and 37,396 (about 18.4K and 17.4K prompt tokens by subtraction). Cap 60,000 plus verdict-first/short-thinking wording produced 2,501 and 3,923 characters in 66 s and 196 s. These were single observed cases, not repeated trials.

The initial open-book dispatch had 2 of 3 gateway outputs empty. The 4 of 4 FIX-FIRST reconciliation includes the completed reruns; the empty drafts themselves supplied no verdict. The evidence pack was described as 46.6 KB and measured as 46,614 bytes.

A later same-day review supplied four attack seeds. Three tool-less reviewers restated them almost one for one (operator judgement, not a measurement); verdicts were 3 REJECT and 1 ACCEPT-WITH-CHANGES. Repository star counts present only in a tool-less draft remain unverified.

## Report audit procedure

Conditions: two reports and a subsequent method draft, 2026-09-22; hashes checked before and after the initial source audit.

| Step | Detail |
|---|---|
| Reports written | feasibility report 34.7 minutes, 30.5 KB; theory report 7.5 minutes (after one failed dispatch), 44 KB |
| Audit r1 | 10.7 minutes, 27 KB, 34 findings; both reports FIX-FIRST |
| Reconcile | 34 of 34 APPLY, none REJECT; edits as same-line replacements, net line change +2 and -2 |
| Orchestrator spot check | 4 blocker items re-checked after the fixes |
| Method draft written afterwards from the corrected reports | audited again: 8 findings (2 BLOCKER, 5 MAJOR, 1 MINOR); verdict "recipe is not consensus"; its 37-row table had 27 rows marked STANDARD, many with only one source |

Initial failed theory-report dispatch: killed at 40 minutes, produced 1 byte. A new dispatch with working notes, a 60-minute budget, and an instruction to write the skeleton within the first 10 minutes produced 44 KB in 7.5 minutes. The reports were described approximately as 30 KB and 44 KB; the procedure records 30.5 KB for the first.

Severities: 34 = 4 BLOCKER + 25 MAJOR + 5 MINOR. A working summary instead said 24 MAJOR and 6 MINOR; the review and reconciliation both support 25 and 5. All 38 arXiv identifiers resolved to the named papers. Of the 34 findings, 30 fall in the first six error-type rows below. This is semantic auditing, not citation-existence checking.

## Report findings by error type

Conditions: 34 findings, one rater, judgemental boundaries, classified from finding headings; original reviewer did not supply these categories.

| Error type | Findings | Count |
|---|---|---|
| Misreading of a cited source (source says something other than, or the opposite of, what the report says: a paper cited in reverse, a method described wrongly, a number read as another metric, a reference object swapped, a statement about code that does not match the code, a "no generation" claim contradicted by the repository) | 7, 8, 9, 14, 15, 18, 19, 20, 21, 22, 23, 26, 30 | 13 |
| Over-extension (a vendor's claim or a single case turned into a conclusion, "not found in sources checked" written as "exists nowhere", a conditional bound written as fixed, "metadata confirmed" taken as "works") | 2, 5, 11, 12, 13, 17, 24, 27, 28, 31 | 10 |
| Mixed bases (gateway versus native format, development set versus locked set, old checkpoint versus new, acceptance statistic versus deployable threshold) | 6, 16, 25 | 3 |
| Omission of a decisive source qualification | 1, 4 | 2 |
| Author's statements upgraded to measurements | 32 | 1 |
| Quotation reworded inside quotation marks | 3 | 1 |
| Technical estimate with the wrong precision (memory estimate used a different weight precision) | 10 | 1 |
| Internal inconsistency (adoption rule contradictory in two sections) | 29 | 1 |
| Formatting (unclosed code fences) | 34 | 1 |
| Informational (identifiers all resolve; semantic review still needed) | 33 | 1 |
| **Total** | | **34** |

The later method draft had 8 findings: 2 BLOCKER, 5 MAJOR, 1 MINOR. Its 37-row table labeled 27 rows STANDARD, many with only one source. The locked test set had also been used to choose alternatives; the repair moved those choices to validation and reserved a single locked-set read after freezing them.

Third document case: audits on version 1 found 23 numerical issues and 20 source/completeness issues. Version 2 had 74 edits: 28 wrong numbers, 18 unsupported claims, 16 omissions, and 12 constraint-violating plans; the categories overlap, and the diff had 104 hunks. Version 3 additions still had four inconsistency clusters and a fresh fact audit, applied in version 3.1. The date of this third case is not recorded here.

## Series A: routing evidence, catalog validation, and supervision

Conditions: nine reports/specifications dated 2026-09-25; reviewer family agent B; effort per round not recorded; counts are report tallies, not statistical estimates.

| Round | New BLOCKER / MAJOR / MINOR (confirmed) | Unconfirmed new | Previous findings: fixed / partial / unfixed | Test suites run (passed) |
|---|---|---|---|---|
| 1 | 2 / 11 / 3 (16 numbered) | 0 | n/a | 39 (gate suite); reviewer also ran 41 of its own cases (17 reproducing a defect, 24 controls) |
| 2 | 1 / 11 / 0 | 2 MINOR | 4 / 10 / 2 (of 16) | 58 + 45; reviewer's own 38 checks assert the buggy behaviour |
| 3 | 0 / 7 / 2 | 1 MAJOR | 7 / 9 / 0 (of 16) | 74 + 49 + 24 = 147 |
| 4 | 0 / 9 / 2 | 0 | 7 / 3 / 0 (of 10) | not run (file-write ban that round); collected 95 + 55 + 33 = 183; 13 non-persisting check functions |
| 5 | 0 / 6 / 0 | 1 MAJOR | 7 / 4 / 0 (of 11) | 111 + 56 + 37 = 204 |
| 6 | 0 / 5 / 0 | 0 | all 7 fixed | 113 + 56 + 40 = 209 |
| 7 | 0 / 2 / 0 | 0 | all 5 fixed | 118 + 58 + 42 = 218 |
| 8 | 0 / 3 / 0 | 0 | all 2 fixed | 120 + 58 + 44 = 222 |
| 9 | 0 / 0 / 2 | 0 | all 3 fixed | 122 + 61 + 44 = 227 |
| Total confirmed | 3 / 54 / 9 = 66 | 4 | | |

All completed historical suites passed. Round 4 collected 95 + 55 + 33 = 183; it did not run those suites. Extra reviewer cases that asserted buggy behavior passed when the defect reproduced. Round 9 reported unchanged hashes for 12 subject files.

The gate suite grew 39 to 122, validator 45 to 61, and supervision 24 to 44 (first listed in round 3). Two regressions were found by the implementer's real-path tests: locale-dependent process identity and one-sided whitespace trimming. The 21 green tests generated their own expected string rather than using the real producer.

## Series B: writable local fact-gate

Conditions: five rounds on 2026-09-27; severity vocabulary changed to BLOCKER/HIGH/MEDIUM after round 1.

| Round | New findings | Of which BLOCKER | Comment |
|---|---|---|---|
| 1 | 18 | 9 | draft versus rules |
| 2 | 12 | 3 | previous: 8 closed (some only at specification level), 6 partial, 4 open |
| 3 | 11 | 1 | with reproductions |
| 4 | 4 | 2 | plus several earlier items still open |
| 5 | 11 | 3 | reviewer switched to the flagship tier: "do not merge" |

Each round closed its principal prior defect but found another forgery route through actor-writable state. The decision stopped and re-scoped: a local writable gate catches mistakes; a forgery barrier needs an identity-separated acceptor. The narrative says "more than three" blocker rounds; the compact rule says "after three". This is a reachability review trigger, not a proven numerical threshold.

## Derived convergence comparisons

Conditions: derived from the series above and the privacy-scanner history below; unequal scopes and reviewer strength prevent a controlled comparison.

| Question | Answer from our data |
|---|---|
| Do findings fall monotonically? | Series A: confirmed findings of any severity 16, 12, 9, 11, 6, 5, 2, 3, 2 (round 4 and round 8 rose); blocker plus major only 13, 12, 7, 9, 6, 5, 2, 3, 0. Series B: 18, 12, 11, 4, 11. Series C: 6, 4, 3, 3, 4, 2, 4, 2, 1, 2 ... 2. |
| Does a green test suite mean the round will be clean? | No: tests passed in every round where they ran to completion, and rounds 2 to 8 still produced findings. |
| Can fixes cause findings? | Yes: 3 of 52 in series C; two author-found cases in series A. |
| Is zero reachable? | Series A reached zero blocker/major; series C did not in 26 rounds; series B stopped by re-scoping the target. |

## Series C: privacy-scanner scope and incomplete round detail

Conditions: history-wide repository privacy scanner; decision entry dated 2026-09-11; only the first ten and the final round were enumerated.

| Measurement | Value | Qualification |
|---|---|---|
| Findings / rounds | 52 / 26 | all reported true and fixed; never reached zero |
| False greens | 15 | content would be published while the scanner said clean |
| Regressions from fixes | 3 | included in the 52 |
| First ten rounds | 6, 4, 3, 3, 4, 2, 4, 2, 1, 2 | 31 in total |
| Last round | 2 | explicitly reported |
| Remaining subtotal | 21 across 16 remaining rounds | derived by subtraction after the first ten; see ambiguity below |
| Scope growth | 2,497 added lines; 32 commits | reported as a scope alarm |
| Test-suite growth | 124 to 197 | historical suite, not this cookbook's tests |

The fact record calls the 16 rounds "in between" while also listing the final round separately. That wording cannot identify the missing per-round allocation consistently. The 21 is retained as the subtraction subtotal after the first ten, not a second subtotal excluding the last round. No missing round counts are reconstructed.

## Series D: stopping with accepted risk

Conditions: shadow-decision-log sweeper, 2026-10-03; finding counts were not supplied.

| Observation | Value | Qualification |
|---|---|---|
| Review rounds / verdicts | 3 / all REJECT | each round was fixed; remaining items recorded as accepted risks after the third |
| Withdrawn threshold rule | back-filled records within a day | only moment-of-action records count; back-fills are displayed, not counted |

The additional de-identification series is linked only: [decision-record-deidentification-gates](https://github.com/ryangu00/decision-record-deidentification-gates). Its counts mix repairs and a changed counting rule.
