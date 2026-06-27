# Claude Review: Phoenix V3 Grouped-Reduction M7 Rerun Packet

Date: 2026-06-20

Reviewer: Claude (claude-sonnet-4-6)

Packet: `docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md`
JSON: `docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json`
Script: `scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py`
Tests: `tests/v3_phoenix_grouped_reduction_m7_rerun_packet_test.py`

## Verdict

```text
approve-with-required-fixes
P0 issues: 1
P1 issues: 3
2ai_consensus_authorized: true (after P0 and P1 fixes)
```

The rerun packet is correctly structured: it flows logically from the 2-AI consensus on the feasibility packet, standardizes both scales to warmup=3, explicitly forbids backfill from old warmup=1/2 evidence, and maintains all four authorization flags as false. Seven tests pass and the wording gate passes with no violations. One P0 fix and three P1 fixes are required before Codex writes consensus and considers pod execution.

## Review Question Answers

### 1. Is this packet safe to use as a pre-pod execution packet?

Mostly yes, with one P0 gap. The packet's status is correctly `ready_for_external_review_not_executed`. The claim_boundary_gate command runs before any measurement and asserts three of the four key authorization flags via Python assertions. The failure_policy is explicit and complete. The test suite verifies that all flags are false, that warmup=3 is consistent across all planned rows, and that the script is idempotent.

The P0 gap: the claim_boundary_gate command asserts `release_authorized`, `public_speedup_claim_authorized`, and `m7_promotion_authorized_before_run` but silently omits `whole_app_speedup_claim_authorized`. The claim_boundary_gate is the pod's last mechanical safety check before measurement. Leaving one of the four core flags unchecked means that a JSON modified on the pod after local review could drift to `whole_app_speedup_claim_authorized: True` without triggering the gate.

### 2. Does it preserve all claim boundaries before execution?

Yes in the committed artifacts; with a gap in the pod-side mechanical check. All four flags are false in the JSON and in the MD header. The `summary` block mirrors all three flags. The wording gate passes with `violations: []`. The test `test_packet_is_not_execution_or_release_authorization` asserts all four flags including `whole_app_speedup_claim_authorized`.

However, the `claim_boundary_gate` command (which is what actually runs on the pod before measurement) only checks three of the four flags, as noted above under P0-1.

Boundary coverage otherwise:
- `release_authorized: false` — present in JSON, MD, summary, tested, gate-checked
- `public_speedup_claim_authorized: false` — present in JSON, MD, summary, tested, gate-checked
- `whole_app_speedup_claim_authorized: false` — present in JSON, MD, tested, NOT gate-checked (P0)
- `m7_promotion_authorized_before_run: false` — present in JSON, MD, summary, tested, gate-checked

The acceptance check "No public wording is written until an external review accepts the rerun and a Codex consensus records the exact allowed claim" is correct and consistent with the prior 2-AI consensus decision.

### 3. Does it correctly standardize the fresh rerun at warmup=3 and forbid backfill from old warmup=1/2 evidence?

Yes. This is the packet's strongest structural property. Specifically:

- Both planned rows specify `warmup: 3` in `planned_rows`.
- Both measure commands pass `--warmup 3` on the command line.
- Both output filenames contain `warmup3` in the basename, which is verified by `test_planned_rows_standardize_scales_and_warmup`.
- `failure_policy.no_merge_with_old_warmup1_or_warmup2_rows: true` is an explicit boolean flag.
- The failure policy for the 524288 scale explicitly says "do not backfill from the old 524288 warmup=2 evidence."
- `--include-iteration-walls` is present on both measure commands, ensuring per-iteration wall-time is captured alongside the median.

The warmup asymmetry disclosed in the feasibility packet (262k used warmup=1; 524k used warmup=2) is the direct motivation for this rerun, and the packet resolves it correctly by standardizing both scales to warmup=3.

One P1 gap: there is no gate that checks whether the artifact directory already contains stale warmup=1/2 evidence before the new run begins. If the pod retains prior artifacts, the `artifact_manifest` at the end would record both old and new files without flagging the contamination.

### 4. Is the prepared-query public contract draft sufficient for the next run, or does it miss any M7-critical field?

The five rules in the contract address the core failure modes identified in the feasibility review:

1. Cold/setup time, hot prepared-query time, and repeat-aware totals must be shown together — directly blocks the 158x hot-ratio overclaim.
2. Any speedup claim must name the repeat count or say "hot prepared-query only" — prevents ambiguous speedup assertions.
3. Single-query end-to-end speedup must be shown even when the intended workload is repeated — prevents hiding the 524k/count single-query loss (0.592x) behind multi-repeat figures.
4. Whole-database or paper-reproduction wording remains false unless a separate packet authorizes it — guards the correct boundary.
5. Warmup count, repeats, backend, groups, rows, and hardware must be identical or explicitly explained — ensures cross-run comparability.

The contract status is correctly marked `draft_required_before_public_wording`. It is sufficient to scope the rerun safely.

Missing M7-critical fields for the full promotion contract (not required for this pre-pod packet, but worth noting for the post-run intake):

- No rule about what constitutes a passing CPU reference match (tolerance, relative error threshold). The acceptance check requires it, but the contract does not define the criterion, so any post-run CPU mismatch has no defined resolution procedure.
- No rule about what happens if one mode (count or sum) passes but the other fails — is the run a partial result or must both modes succeed for the row to be valid? The two measure commands are independent and either could fail.
- No rule requiring both backends (Embree and OptiX) to produce valid rows — a single-backend result could technically pass the acceptance checks but would be incomplete for a two-backend comparison.

These gaps are acceptable for a pre-run packet but must be closed before M7 promotion wording is authorized.

### 5. What P0/P1 fixes are required?

See sections below.

## P0 Issues

**P0-1: `claim_boundary_gate` command omits the `whole_app_speedup_claim_authorized` assertion.**

The claim_boundary_gate currently asserts:

```python
assert d['release_authorized'] is False
assert d['public_speedup_claim_authorized'] is False
assert d['m7_promotion_authorized_before_run'] is False
```

It does not assert `d['whole_app_speedup_claim_authorized'] is False`. This is one of the four core authorization flags declared in the MD header, in the JSON, and in the summary. The claim_boundary_gate's stated purpose is "Fail if this packet drifts into release or public-claim authorization before measurement." A JSON modified on the pod to set `whole_app_speedup_claim_authorized: True` would pass this gate.

Fix required in `scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py` in `_commands()`, in the committed `docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json`, and in `tests/v3_phoenix_grouped_reduction_m7_rerun_packet_test.py` (`test_required_commands_include_claim_and_hardware_gates` should assert `whole_app_speedup_claim_authorized` appears in the gate command):

```python
# In the claim_boundary_gate command string, add:
"assert d['whole_app_speedup_claim_authorized'] is False; "

# In the test:
self.assertIn("whole_app_speedup_claim_authorized", commands["claim_boundary_gate"]["command"])
```

## P1 Issues

**P1-1: On assertion failure in `claim_boundary_gate`, stderr is lost and the artifact file is empty.**

The command uses `> /root/.../claim_boundary_gate.txt` which captures only stdout. When a Python assertion fails, the `AssertionError` traceback goes to stderr. The redirect captures only the `print(...)` success message; on failure, stdout is empty and stderr is discarded. A pod operator checking `claim_boundary_gate.txt` would see an empty file on gate failure, which could be misread as a passed gate if the check is "file has content" rather than "check exit code."

Fix: Redirect stderr into the artifact too so failure is visible:

```bash
... > /root/.../claim_boundary_gate.txt 2>&1
```

This preserves the exit code (non-zero on assertion failure) while also writing the full traceback to the artifact, making failures unambiguous.

**P1-2: No post-run intake command is specified in `required_commands`.**

The acceptance check states: "Post-run intake computes repeat-aware totals for repeat counts 1, 2, 5, 10, 25, 50, 100, 500, and 1000." However, there is no `required_commands` entry that performs this computation. The seven required commands are: `env_probe`, `claim_boundary_gate`, `optix_hardware_gate`, `native_build`, `m7_grouped_reduction_262144`, `m7_grouped_reduction_524288`, `artifact_manifest`. None of them computes repeat-aware totals.

This acceptance check is a required deliverable (not just a verification criterion) and cannot be satisfied by the measurement script alone, since it requires post-measurement derivation. Without a named command or script, there is no mechanical enforcement and no artifact to review.

Fix: Either add a `post_run_intake` entry to `required_commands` that names the intake script (e.g., referencing the repeat-aware amortization logic from the feasibility work), or clearly document that the intake is a separate step with a defined script name, so Codex knows exactly what to run and where the output goes.

**P1-3: `env_probe` source manifest omits `scripts/v3_gpu_python_env_gate.py` from the sha256sum.**

The `env_probe` command hashes:

```bash
sha256sum VERSION scripts/v3_0_m28_raydb_prepared_grouped_refresh.py scripts/v3_optix_hardware_gate.py
```

But `scripts/v3_gpu_python_env_gate.py` is also called in the same command (`--json-out gpu_env_gate.json`). The environment gate script is part of the measured execution and should have its identity recorded in the source manifest. If that script were modified between local review and pod execution, there would be no artifact-level evidence of the change.

Fix: Add `scripts/v3_gpu_python_env_gate.py` to the sha256sum invocation:

```bash
sha256sum VERSION scripts/v3_0_m28_raydb_prepared_grouped_refresh.py scripts/v3_optix_hardware_gate.py scripts/v3_gpu_python_env_gate.py > .../source_manifest.sha256
```

Update the script and the committed JSON accordingly.

## Test Coverage Assessment

The seven tests cover the critical correctness and boundary cases well:

- `test_packet_is_not_execution_or_release_authorization` — checks all four flags and the summary fields
- `test_planned_rows_standardize_scales_and_warmup` — verifies both scales, groups, modes, backends, warmup=3, and warmup3 in output filename
- `test_required_commands_include_claim_and_hardware_gates` — verifies all seven command IDs, `--require-rt-hardware`, `--warmup 3`, `--include-iteration-walls`, and `generic_capability` on measure commands
- `test_public_contract_requires_hot_cold_repeat_context` — asserts all four key contract phrases
- `test_failure_policy_forbids_backfill_from_old_warmups` — checks all five failure_policy fields
- `test_script_rebuilds_packet` — idempotency: rebuilt summary and required_commands match committed JSON
- `test_report_keeps_boundary_visible` — verifies all seven boundary phrases in the MD

After the P0-1 fix, `test_required_commands_include_claim_and_hardware_gates` should also assert that `whole_app_speedup_claim_authorized` appears in the claim_boundary_gate command string.

One additional test gap worth noting: there is no test that asserts the two planned row IDs appear in the artifact directory path (i.e., that the output filenames in `planned_rows` match the output filenames in the corresponding `required_commands`). The two are currently consistent, but they are defined separately (once in `planned_rows`, once in `_measure_command()`), and a future refactor could introduce a mismatch without a test catching it.

## Wording Gate

The release wording gate (`v3_release_wording_gate.py --pretty`) passes with `violations: []`. The packet correctly adds its required strings:

- `phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md` — present in `DEFAULT_FILES`
- `ready_for_external_review_not_executed` — present in the committed MD and required by `REQUIRED_STRINGS`
- `m7_promotion_authorized_before_run: false` — present in the MD header block
- `fresh M7-designated grouped_reduction rerun` — present in the MD purpose section

The wording gate correctly guards these boundary phrases.

## Lineage Integrity

The rerun packet is the correct next step after the feasibility consensus. The 2-AI consensus explicitly stated: "The next valid promotion step is not more wording; it is a fresh M7-designated rerun and public prepared query contract that makes setup, warmup, repeat count, and amortization rules first-class." This packet implements exactly that scope — a fresh rerun contract with warmup=3 standardized across both scales — without attempting to promote grouped_reduction or write public wording.

The five P1 fixes from the feasibility review (warmup asymmetry disclosure, case-specific blockers, payload-derived MD flags, Embree cold cost, 262k/count pinning test) were all applied and are visible in the prior consensus record. This rerun packet does not regress any of those fixes.

## Bottom Line

The rerun packet is structurally sound and correctly inherits from the feasibility work. The claim isolation, warmup standardization, and backfill prohibition are all present and tested. The P0 fix (adding `whole_app_speedup_claim_authorized` to the claim_boundary_gate) is a one-line change in the script and a corresponding one-line addition in the test. Fix all four issues (P0-1, P1-1, P1-2, P1-3), regenerate the JSON and MD from the script, confirm the 7 tests still pass and the wording gate still passes, and consensus is authorized.
