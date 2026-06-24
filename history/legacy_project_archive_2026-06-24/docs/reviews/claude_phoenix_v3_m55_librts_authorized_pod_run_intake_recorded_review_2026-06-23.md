# Claude: Phoenix V3 M55 LibRTS Authorized POD Run Intake — Recorded Review

Date: 2026-06-23

Reviewer: Claude (external critical reviewer)

Status: `review_complete_verdict_recorded`

Verdict:

```text
accept_m55_valid_red_watch_rows_open_no_rerun
```

---

## Evidence Reviewed

- `docs/reports/phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m54_goal_completion_3ai_consensus_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/README.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/m55_execution_driver.log`
- `tests/v3_phoenix_m55_librts_authorized_pod_intake_gate_test.py`

---

## Question 1: Was the M55 execution within the exact M54 one-run authorization?

**Yes.**

The M54 3-AI consensus authorized exactly one run of
`scripts/v3_phoenix_m47_librts_stability_protocol.py` with
`--execute --authorization-token M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`,
two scenarios, eight paired samples per scenario, seed 2025, alternating
order, separate real current/V2.14 roots, explicit Linux/POD Python paths,
and full copy-back. It also required a target-machine dry-run with
`failed_check_count=0` before the execution token was used.

Verification against each mandatory pre-execution requirement:

| Requirement | Evidence |
| --- | --- |
| Real current Phoenix V3 repo root | `/root/rtdl_v3_rebuild_20260620/current` — dry-run `args.current_root` |
| Real separate V2.14 root | `/root/rtdl_v3_rebuild_20260620/v2_14` — dry-run `args.v2_root` |
| Explicit Linux/POD Python for both trees | `/usr/bin/python3` — both dry-run command lists |
| Target-machine dry-run executed first | Dry-run directory `_2339` exists, `execute: false`, `failed_checks: []` |
| `failed_check_count=0` confirmed | `summary.failed_check_count: 0` in dry-run summary |
| Authorized command run with token only after dry-run | Execution directory `_2340` with `execute: true` and token consumed |

Execution parameters match the authorization exactly:

- `scenario_count: 2` (optix_cold_single_shot, embree_32768_stress)
- `sample_count_per_scenario: 8`
- `seed: 2025`
- Alternating order confirmed in driver log: odd samples start v2_14 first,
  even samples start current first, for all 32 schedule rows
- Status: `m47_librts_stability_protocol_run_complete_not_release`
- rc=0, `run_errors: {}`

The current root is a pod-side benchmark tree, not a git root.
`current_git_revision` failed with rc=128 and was correctly marked
non-required. V2.14 git revision was captured (rc=0). This is consistent
with the intake report and does not violate the authorization.

The output directory name (`phoenix_v3_m55_librts_authorized_execution_20260623_2340`)
deviates cosmetically from the M51 runbook naming convention
(`phoenix_v3_m51_librts_authorized_run_YYYYMMDD_HHMMSS`). This has no
effect on evidence quality or protocol compliance.

**Authorization token consumed. No second run authorized by this review.**

---

## Question 2: Is the copy-back complete enough for review?

**Yes.**

Copy-back inventory per intake report:

| Item | Count / Status |
| --- | --- |
| Measured stdout JSON files | 32 (16 per scenario × 2 scenarios) |
| stderr/preflight text files | 38 |
| `summary.json` | present |
| `README.md` | present |
| `m55_execution_driver.log` | present |
| `m55_nohup.log` | present |
| Total files | 80 |

The M51 runbook requires summary.json, README.md, preflight stdout/stderr,
and one stdout JSON and stderr text per measured command. All are present.

The gate test (`v3_phoenix_m55_librts_authorized_pod_intake_gate_test.py`)
checks for exactly 32 stdout JSON files, ≥32 stderr text files, and ≥12
preflight files. The copy-back satisfies all three checks.

All 32 schedule rows in `summary.json` have individual `paired_samples`
entries with per-sample timing, speedup, metadata failure list, fixture
check result, and stderr status. Per-sample numerical values are
cross-checkable against the raw stdout JSON files.

The copy-back is complete for audit without re-running.

---

## Question 3: Do the two red labels follow the M47 protocol rules?

**Yes, both are correctly labeled `red_failure_watch_row_open`.**

### optix_cold_single_shot

Numerical results:

| Metric | Value | Green threshold |
| --- | --- | --- |
| All-sample geomean | 0.984404x | ≥0.950x |
| All-sample median | 0.979645x | ≥0.950x |
| Min | 0.929253x | ≥0.900x |
| Pass count ≥0.950x | 6/8 | 7/8 required |
| First-sample-stripped geomean | 0.974022x | ≥0.980x |

The geomean and median are above 0.950x, and min is above 0.900x. On those
three criteria alone, the scenario would not trigger the numeric red rule.
However, the M47 protocol lists a stop condition that applies here:

> Stop and record failure instead of interpreting performance if:
> — current OptiX payload lacks productized runner metadata

`current_metadata_failures: ["set_b_control_candidate_missing"]` is present
on every sample. The harness correctly applied the stop condition and labeled
the scenario red. Additionally, the pass count (6/8) and first-sample-stripped
geomean (0.974022x) both fall short of green thresholds, so even setting the
metadata issue aside, this scenario would not reach green closure candidate.

Red label for optix_cold_single_shot is correctly applied.

### embree_32768_stress

Numerical results:

| Metric | Value | Green threshold |
| --- | --- | --- |
| All-sample geomean | 0.931885x | ≥0.950x |
| All-sample median | 0.941006x | ≥0.950x |
| Min | 0.801149x | ≥0.900x |
| Pass count ≥0.950x | 4/8 | 7/8 required |
| First-sample-stripped geomean | 0.921176x | ≥0.980x |

Geomean 0.931885x and median 0.941006x are both below 0.950x. Min 0.801149x
is below 0.900x. Pass count is 4/8 against a 7/8 requirement. The numeric
red rule is triggered independently of the metadata failure.
`set_b_control_candidate_missing` is also present on all samples, which is
an additional red trigger.

Embree_32768_stress is red on both numeric and metadata grounds.

Red label for embree_32768_stress is correctly applied.

**Summary**: Both red labels are protocol-compliant. Neither watch row is
closed. Do not interpret these labels as watch-row closure candidates.

---

## Question 4: Does `set_b_control_candidate_missing` make the run a valid red result, or a setup-invalid run that requires metadata repair and separate authorization?

**Valid red result. The authorization token is consumed.**

The distinction matters for what happened and for what comes next.

A setup-invalid run would require: misconfigured paths, wrong parameters
(wrong seed, wrong scenario count, wrong sample count), preflight check
failures, dry-run skipped, token missing, or execution abort. None of those
apply here. The facts:

- `failed_checks: []` — all pre-run setup checks passed
- `run_errors: {}` — no runtime errors during any of the 32 measured commands
- rc=0 — harness exited cleanly
- All 32 samples produced stdout JSON output
- All fixture/contract checks passed (`fixture_contract_matches: true` on
  every sample of both scenarios)
- All current and V2.14 stderr files are empty (no runtime errors in the
  benchmark itself)

`set_b_control_candidate_missing` is a per-sample metadata field, not a
setup check. It is detected during sample-level output analysis, not during
the pre-run preflight phase. The M47 harness was designed to detect and
classify this as a red failure rather than to abort the run. The harness
classification is `red_failure_watch_row_open`, not `run_invalid` or
`setup_error`. That design is intentional: the protocol anticipated that
the current tree might fail the Set-B/control candidate metadata check and
specified that the harness should record the failure and stop interpreting
performance, not discard the run.

The implication of the missing metadata is important to name clearly:
`set_b_control_candidate_missing` means the current tree's benchmark output
does not confirm that the productized Set-B control execution path was used
(expected fields: `prepared_execution_session_runner_used`,
`productized_execution_path`, `primitive_contract`, `prepared_query_mode`
absent from current output). This means the timing values collected in this
run cannot be asserted as measurements of the productized Set-B path. That
is the content of the failure, not a reason to invalidate the run as a
structural event.

The run is a valid, correctly conducted M47 experiment that produced a
documented failure outcome. The red label captures the failure accurately.

**The token is consumed. Any future run addressing the metadata failure
requires a separate authorization packet approved by external review.**

---

## Question 5: Are the numerical results reported accurately without converting them into public speedup wording or watch-row closure?

**Yes.**

Cross-check of intake report values against `summary.json`:

### optix_cold_single_shot

| Field | Intake report | summary.json | Match |
| --- | --- | --- | --- |
| geomean | 0.984404x | 0.984403696827165 | ✓ |
| median | 0.979645x | 0.9796449421781168 | ✓ |
| min | 0.929253x | 0.9292530342749593 | ✓ |
| pass count | 6/8 | pass_count_0_95: 6 | ✓ |
| first-sample-stripped geomean | 0.974022x | 0.9740219218705372 | ✓ |
| first-sample-stripped median | 0.978946x | 0.9789455850195483 | ✓ |

### embree_32768_stress

| Field | Intake report | summary.json | Match |
| --- | --- | --- | --- |
| geomean | 0.931885x | 0.9318846036784767 | ✓ |
| median | 0.941006x | 0.9410064166113763 | ✓ |
| min | 0.801149x | 0.8011486758982834 | ✓ |
| pass count | 4/8 | pass_count_0_95: 4 | ✓ |
| first-sample-stripped geomean | 0.921176x | 0.9211756326909781 | ✓ |
| first-sample-stripped median | 0.930735x | 0.9307350675147374 | ✓ |

All values match to six significant figures (rounding only). No
transcription errors found.

Spot-check of per-sample arithmetic:

- embree sample 1: v2_14_sec=0.9874 / current_sec=0.9773 = 1.0104 ✓
- embree sample 3 (min): v2_14_sec=0.7960 / current_sec=0.9936 = 0.8011 ✓
- optix sample 1: v2_14_sec=0.23468 / current_sec=0.22135 = 1.0602 ✓
- optix sample 5 (min): v2_14_sec=0.19878 / current_sec=0.21392 = 0.9293 ✓

Wording boundaries observed correctly:

- Intake report uses raw ratio values (e.g., "0.984404x"), not "V3 is X%
  faster" language
- No broad V3-over-V2 claim appears
- No watch-row closure is claimed or implied
- Intake report explicitly states "Do not call either watch row closed"
- All claim-boundary booleans are false in summary.json

---

## Question 6: What is the next allowed action?

**Record this verdict and leave both watch rows open. No rerun is authorized.**

What is permitted immediately:

1. Record this review document as the external intake verdict.
2. Preserve both watch rows as `red_failure_watch_row_open` without
   modification.
3. Note `set_b_control_candidate_missing` as the documented open failure
   in both scenarios.

What is not permitted from this review:

- No V3 release
- No all-app benchmark run
- No broad paid POD campaign
- No second M47 run (the one authorized token is consumed)
- No public speedup wording
- No broad V3-over-V2 claim
- No V4 work
- No embedding
- No C ABI
- No true zero-copy claim
- No watch-row closure

What would be required to attempt LibRTS watch-row closure in the future:

1. Diagnose why `set_b_control_candidate_missing` appears. Determine
   whether the current tree's benchmark runner is not emitting the expected
   metadata fields (`prepared_execution_session_runner_used`,
   `productized_execution_path`, `primitive_contract`, `prepared_query_mode`),
   or whether the productized path is genuinely not being exercised.
2. Repair the metadata (code fix or runner configuration fix).
3. Prepare a new M47-compliant authorization packet documenting the repair.
4. Submit that packet for external review.
5. If and only if a reviewer returns an explicit new authorization token for
   another run, execute the run.

This is not an authorization for any of the steps above. It is a statement
of what the path forward would require.

---

## Non-Authorization Record

This review does not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M47 run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure

---

## Verdict

```text
accept_m55_valid_red_watch_rows_open_no_rerun
```

Both scenarios (`optix_cold_single_shot` and `embree_32768_stress`) are
accepted as valid red results. Both watch rows remain open. The M54
authorization token is consumed. Any future run requires a separate
authorization.
