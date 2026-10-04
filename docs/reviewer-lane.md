# A caller-controlled reviewer lane

The failure was not solved by repeatedly editing the second agent's settings.
A router and a desktop application both wrote to that file. The repair moved
the runtime contract into the caller's command and bounded the subject in files.

## What each invocation must establish

| Invocation element | Contract | Historical failure |
|---|---|---|
| `--ignore-user-config` | Skip caller-uncontrolled settings | Provider/catalog rewrites and context-heavy startup. |
| `-c model_provider=...` | Explicit native provider | Router lacked the required responses endpoint. |
| `-c model=...` | Explicit available model | Router-style or unsupported names. |
| `-c model_catalog_json=...` | Own valid metadata | Replacement catalog omitted native metadata. |
| `-s read-only` | Actual sandbox selection | Desktop app wrote a full-access default. |
| `< /dev/null` | Closed stdin | Background process waited for additional input. |
| `-o ...` | Last-message artifact | Grepping stdout matched an echoed prompt. |
| `--output-schema ...` | Optional structured output | Avoid relying entirely on prose parsing. |
| `-c model_reasoning_effort=...` | Proposed explicit effort | Historical user-config skipping also skipped the effort setting. |

The last row and banner assertion are **an untested live proposal**. The public
implementation is stub-tested; that is not evidence that a current CLI accepts
the value or reports the banner in the expected form.

## Public script parameters

| Environment variable | Default | Interpretation |
|---|---|---|
| `AGENT_B_BIN` | `agent-b` | Generic executable name on PATH; set a real installed binary for live use. |
| `REVIEW_MODEL` | `example-model` | Synthetic placeholder, not an available model claim. |
| `REVIEW_PROVIDER` | `native` | Placeholder; set the actual provider key. |
| `REVIEW_EFFORT` | `high` | Demonstration value; not a claim that this is the highest supported effort. |
| `REVIEW_CATALOG` | `.review-lane/catalog.json` | Created if missing or empty, validated if already present. |
| `REVIEW_REPO_DRIVER` | `git` | Real repository command by default; tests use the recorded-response stub. |
| `TMPDIR` | Current directory if unset | Temporary working files are cleaned on exit. |

The catalog retains the historical model metadata fields, including context
window 200,000 and effective percentage 95. This is a version-specific shape
checked only for the self-test across 0.147 to 0.153.4. It is not a declaration
that an arbitrary model supports that window. The exact metadata prerequisite
for another CLI/model combination is unknown here.

The public script validates existing JSON and checks that the requested model
is represented. It does not overwrite a nonempty catalog with a different model.
A malformed catalog cannot be mistaken for a clean warning count.

## Handoff packet and review subject

With `--base`, the wrapper obtains the `base...HEAD` diff and a packet containing
repository name, base, head, worktree status, changed-file statistics, and commit
subjects. With a standalone `--diff`, provide the matching `--packet`; the public
adaptation refuses to fabricate packet metadata from a guessed prior commit.

The prompt begins with the packet and appends the entire diff. It tells the
reviewer not to explore the wider repository or modify files. Findings must
include a location and failing scenario; packet claims must be checked rather
than accepted. The requested verdict vocabulary is SOUND / NEEDS CHANGES /
UNSOUND, and unsupported conclusions should say "cannot tell from the diff".

The wrapper requires `--out`. Put this output, stderr, and rebuttals outside the
subject. Requiring a path does not enforce placement: the caller must identify
the actual subject boundary. The public script does not implement an exclude
pathspec, since the historical record provides no tested exclusion policy.

The repository-response stub is solely an offline test seam. It produces
recorded answers and cannot prove repository state. No Git executable is run by
the cookbook's tests or the README's offline procedure.

## Liveness and false positives

The historical exact-line self-test cases were checked on 2026-10-03; their
[truth table](results.md#original-wrapper-self-test) distinguishes a real reply,
prompt echo, metadata warning, and silence. The daily real-call probe used a
180-second timeout. The scheduler itself is not shipped here.

The public self-test additionally requires a successful process exit and exact
`model: <value>` / `reasoning effort: <value>` lines. It deliberately fails if
the banner is missing or formatted differently. It does not prove that a server
internally served the claimed model, nor does a stub exercise authentication.

The historical false-positive diagnoses were direct: a pattern ending in OK
matched the prompt itself, and a zero-warning run with `/dev/null` as catalog
had died parsing JSON. An empty-string catalog path failed too. Neither was
evidence of a working model call.

## Shell behavior and direct variant

The review path, unlike the self-test path, expands optional schema arguments.
On bash 3.2 under `set -u`, an empty array needs:

```bash
${EXTRA[@]+"${EXTRA[@]}"}
```

The historical upgrade also exposed non-fatal commands returning failure under
`set -e`. Handle a failure as optional only when the command is actually optional;
the tests exercise review mode as well as the self-test.

`review-direct.sh` is the smaller alternative. `PRECHECK_CMD` is an executable
that receives the prompt-file path and must exit successfully before the agent
runs. It is not a shell expression and is not a supplied privacy policy. The
script uses a read-only direct `exec`, explicit model/effort, and closed stdin;
it does not implement the main wrapper's catalog, packet, self-test, or banner
checks. Its effort flag is subject to the same untested-live qualification.

## What the historical failures establish

The old MCP-server channel had 4 transient authentication failures in 23 calls
(17.4%) on 2026-07-05. Two calls began simultaneously, with one succeeding; a
non-concurrent call failed too. Retry twice with 3 s and 6 s back-off was the
mitigation, with one observed self-heal. It was not re-measured, and the cause
was not confirmed by the vendor. The wrapper uses plain `exec` instead.

An under-covering diff, default effort, prior review logs in the subject, a
forwarder parsing prompt text as flags, and a one-time safety-filter stop are
distinct failures. Their counts and timings are retained in [results](results.md#reviewer-lane-incidents).
None establishes that a vendor is generally unreliable or that prompt wording
alone can guarantee execution.
