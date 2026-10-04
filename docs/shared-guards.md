# Shared guards: files, events, and hook output

The mechanism has separate filesystem and evidence boundaries. Linking a guard
shares its implementation. Mapping a session log determines which observations
the guard can use. Neither establishes that the guard's policy is correct.

## Historical boundary

The copied-hook incident, mirror canary, and replay history are already described
in [agent-guards-that-fail-silently](https://github.com/ryangu00/agent-guards-that-fail-silently).
Its cases 9/10 explain the incident behind this chapter. The compact historical
inventory is retained in [results](results.md#shared-hooks-and-rollout-observations).

This public extraction contains no private guard criteria, hook inventory,
privacy patterns, or session content. The hook configuration is an illustrative
event wiring example, not the original registration order.

## Link migration and rollback

The historical procedure first compared each same-named pair segment by segment.
All differences were missing upstream fixes, with no intentional B behavior.
The copies were then moved to dated backups and replaced by links. The event
configuration continued to reference B's directory, so registration did not move.

`scripts/hooks/link-hooks.sh` implements that procedure with `A` and `B` directory
overrides. It resolves the directories before constructing links, skips backups,
already-linked files, and B-only names. It refuses a backup-name collision rather
than overwriting the retained original. An empty B directory is a successful
no-op; dangling links are skipped without stopping migration of later files.
These checks belong to the public script; the historical migration was performed
by hand.

The fixture commands in the README keep both directories inside `.work`.
Inspect the backup suffix before using the rollback pattern:

```bash
# Substitute the exact suffix; do not paste an unresolved placeholder.
for f in "$B"/*.bak-<stamp>; do mv -f "$f" "${f%.bak-<stamp>}"; done
```

Byte comparison uses `filecmp.cmp(shallow=False)`. A regular file with the same
bytes remains invisible to the original byte-only rule until a divergent edit.
The optional `--require-links` mode reports it immediately. A dangling link with
an existing A counterpart raised `FileNotFoundError` in the original probe; the
public extraction records a per-file missing-target alert and continues.

| Case with an existing A counterpart | Byte-only mode | `--require-links` mode |
|---|---|---|
| Symlink to the A file | No alert | No alert |
| Regular file with the same bytes | No alert | Alert: regular copy |
| Regular file with different bytes | Alert: different bytes | Alert: different bytes |
| Dangling symlink | Alert: missing target | Alert: missing target |

These are public-extraction behaviors; the original probe's case table is in
[results](results.md#original-mirror-function).

This is not an installer-resilience guarantee. Behavior when an agent copies or
resolves links during installation was not tested. An agent-specific behavior
can branch in the shared file on host, or use a differently named file. The
mirror deliberately ignores names without an A counterpart.

## Rollout recognition and mapping

Host detection accepts a hidden `.agentB` directory component or a first JSON
record whose `type` is `session_meta`. The public path label is generic and must
be adapted to an actual installation. A UUID-shaped session identifier cannot
identify the host: both hosts used identifiers of the same length in the notes.
The resume-pointer incident was not independently re-verified in code.

Only a record with `type: event_msg`, `payload.type: item_completed`, and a
dictionary item is mapped. An agent-B-shaped record has a payload rather than
an agent-A message. The public mapper rejects mixed envelopes.

| Item | Tool shape | Data retained |
|---|---|---|
| `CommandExecution` | `Bash` | Command, direct output, and integer exit status. |
| `FileChange` with `add` | `Write` per path | Added content as `new_string`. |
| Other file changes | `Edit` per path | Added diff lines, excluding `+++` headers. |
| `McpToolCall` | `mcp__<server>__<tool>` | Arguments. |
| `WebSearch` | `WebSearch` | Query. |
| Message and reasoning items | None | No execution evidence inferred. |

For argv lists, use the shell command at `argv[2]` only when the list is long
enough and `argv[1]` is `-lc` or `-c`; otherwise reconstruct with `shlex.join`.
For output, prefer `aggregated_output`, falling back to `stdout`. An absent or
non-integer exit code is unknown, not success. Integer nonzero exits remain
errors even if output contains a receipt-shaped success string.

The parser is deliberately not a receipt validator. It preserves command/result
association but does not assert that a printed receipt proves an external write.
It also cannot turn model-composed JavaScript output into harness evidence.

## Unsupported and damaged input

The public parser returns `parsed`, `unparsed`, `empty`, or `partial`.
Nonempty input producing no mapped events is `unparsed`, including a log made
entirely of ignored messages. Malformed lines are recorded by line number;
mapped events alongside malformed records produce `partial`. The CLI exits
nonzero for `unparsed` and `partial`. These are parsing outcomes, never clean
guard verdicts.

The historical implementation still judged the MCP-server-mode gap clean.
The daily auditor shared the new parser but kept its old function-call parser
only for rollouts with no `item_completed` records. The public example does not
ship that legacy fallback or attempt to parse JavaScript to close the gap.

## Stop and SessionStart are different channels

| Protocol | Agent A | Agent B 0.153.4 |
|---|---|---|
| Stop output | `hookSpecificOutput.additionalContext` | Strict object; no `hookSpecificOutput`. |
| Accepted Stop keys | Host-specific | `continue`, `decision`, `reason`, `stopReason`, `suppressOutput`, `systemMessage`. |
| Stop input | `transcript_path`, `session_id` | Additionally `last_assistant_message`. |
| SessionStart | `additionalContext` accepted | `additionalContext` accepted. |

`stop_output.py` shows only the output branch. It consumes both synthetic input
payloads without installing any hook. The historical message-writing hook
preferred `last_assistant_message` and fell back to the last assistant text in
the rollout; that content extraction and the private writing logic are not shipped.

`systemMessage` is visible to the human, not a non-blocking instruction to B's
model at Stop. Blocking solely to deliver a warn-only reminder was not the
recommended response. Session-start context is a distinct supported channel.

## Trust and validation limits

The quoted vendor rule was to trust the exact hook definition. The record
interprets this as configuration-definition approval rather than a script-byte
approval: updating a linked script need not re-prompt. There was no dedicated
experiment, and the binary schema extraction method was not recorded.

The offline tests exercise both output shapes, the original mirror case table,
stricter link detection, backup retention, idempotence, argv handling, forged
calls and outputs, failed receipts, and unsupported logs. They do not verify
the installed vendor's trust UI, current schemas, or a production policy.
