Review written. Here is the complete review:

---

# Claude: Phoenix V3 M55 LibRTS Authorized POD Run Intake — Recorded Review

Date: 2026-06-23  
Reviewer: Claude (external critical reviewer)  
Status: `review_complete_verdict_recorded`

**Verdict:**
```
accept_m55_valid_red_watch_rows_open_no_rerun
```

---

## Q1: Was the M55 execution within the exact M54 one-run authorization?

**Yes.**

All six mandatory pre-execution requirements from the M54 3-AI consensus were met:

| Requirement | Evidence |
|---|---|
| Real current Phoenix V3 repo root | `/root/rtdl_v3_rebuild_20260620/current` |
| Real separate V2.14 root | `/root/rtdl_v3_rebuild_20260620/v2_14` |
| Explicit Linux/POD Python for both trees | `/usr/bin/python3` |
| Target-machine dry-run executed first | Directory `_2339`, `execute: false`, `failed_checks: []` |
| `failed_check_count=0` confirmed | Dry-run summary confirms |
| Token used only after dry-run | Execution `_2340` with `execute: true` |

Execution parameters exactly match authorization: 2 scenarios, 8 samples, seed 2025, alternating order (odd samples v2_14-first, even samples current-first across all 32 schedule rows, confirmed in driver log). Status `m47_librts_stability_protocol_run_complete_not_release`, rc=0, `run_errors: {}`.

The `current_git_revision` failure (rc=128, non-git root) was correctly marked non-required and does not violate the authorization.

**Authorization token consumed. No second run authorized.**

---

## Q2: Is the copy-back complete enough for review?

**Yes.**

- 32 measured stdout JSON files (16 per scenario × 2 scenarios)
- 38 stderr/preflight text files
- `summary.json`, `README.md`, `m55_execution_driver.log`, `m55_nohup.log` all present
- 80 total files
- Gate test requirements satisfied: 32 stdout JSON, ≥32 stderr txt, ≥12 preflight files
- All 32 schedule rows have per-sample timing, speedup, metadata failure list, fixture check result, and stderr status in `summary.json`

Copy-back is complete for audit without re-running.

---

## Q3: Do the two red labels follow the M47 protocol rules?

**Yes, both `red_failure_watch_row_open` labels are correctly applied.**

**optix_cold_single_shot**: Geomean 0.984404x and median 0.979645x are above the 0.950x numeric red threshold, but the M47 protocol's stop condition fires: *"Stop and record failure instead of interpreting performance if: current OptiX payload lacks productized runner metadata."* `set_b_control_candidate_missing` is present on every sample. Additionally, pass count (6/8) and first-sample-stripped geomean (0.974022x) both fall short of green thresholds independently.

**embree_32768_stress**: Geomean 0.931885x and median 0.941006x are both below 0.950x — the numeric red rule fires independently. Min 0.801149x is below 0.900x, pass count is 4/8 against a 7/8 requirement. The metadata failure is an additional red trigger.

Neither watch row is closed. Do not interpret these labels as closure candidates.

---

## Q4: Does `set_b_control_candidate_missing` make the run a valid red result, or a setup-invalid run?

**Valid red result. The token is consumed.**

A setup-invalid run would require misconfigured paths, wrong parameters, preflight failures, or execution abort. The facts here:

- `failed_checks: []` — all pre-run setup checks passed
- `run_errors: {}` — no runtime errors across 32 measured commands
- rc=0 — harness exited cleanly
- All 32 samples produced stdout JSON output
- `fixture_contract_matches: true` on every sample of both scenarios
- All current and V2.14 stderr files empty

`set_b_control_candidate_missing` is detected during per-sample output analysis, not in the pre-run preflight phase. The M47 harness was designed to classify this as `red_failure_watch_row_open`, not `run_invalid`. The protocol anticipated this case and specified "stop and record failure" — not "discard the run."

The content of the failure is: the current tree's benchmark output does not confirm that the productized Set-B control execution path was used (expected fields `prepared_execution_session_runner_used`, `productized_execution_path`, `primitive_contract`, `prepared_query_mode` are absent). The timing values therefore cannot be asserted as measurements of the productized Set-B path. That is the failure. It is not a reason to call the run structurally invalid.

**Any future run addressing the metadata failure requires a separate authorization packet approved by external review.**

---

## Q5: Are the numerical results reported accurately without public speedup wording or watch-row closure?

**Yes. All numbers verified against `summary.json`, all values match to six significant figures.**

| Scenario | Field | Intake report | summary.json |
|---|---|---|---|
| optix | geomean | 0.984404x | 0.984403696827165 ✓ |
| optix | median | 0.979645x | 0.9796449421781168 ✓ |
| optix | min | 0.929253x | 0.9292530342749593 ✓ |
| optix | pass count | 6/8 | 6 ✓ |
| optix | fs-stripped geomean | 0.974022x | 0.9740219218705372 ✓ |
| optix | fs-stripped median | 0.978946x | 0.9789455850195483 ✓ |
| embree | geomean | 0.931885x | 0.9318846036784767 ✓ |
| embree | median | 0.941006x | 0.9410064166113763 ✓ |
| embree | min | 0.801149x | 0.8011486758982834 ✓ |
| embree | pass count | 4/8 | 4 ✓ |
| embree | fs-stripped geomean | 0.921176x | 0.9211756326909781 ✓ |
| embree | fs-stripped median | 0.930735x | 0.9307350675147374 ✓ |

Per-sample arithmetic spot-checked (e.g., embree sample 3 min: 0.7960/0.9936=0.8011 ✓). Values use raw ratio format — no "X% faster" language appears. No watch-row closure is claimed. All claim-boundary booleans are false in `summary.json`.

---

## Q6: What is the next allowed action?

**Record this verdict and leave both watch rows open. No rerun is authorized.**

Permitted immediately: record this review, preserve both watch rows as `red_failure_watch_row_open`, note `set_b_control_candidate_missing` as the documented open failure.

Not permitted from this review: no V3 release, no all-app run, no broad paid POD campaign, no second M47 run, no public speedup wording, no broad V3-over-V2 claim, no V4 work, no embedding, no C ABI, no true zero-copy claim, no watch-row closure.

Path forward if LibRTS watch-row closure is eventually desired:
1. Diagnose why `set_b_control_candidate_missing` appears (missing metadata emission or productized path genuinely not exercised).
2. Repair the defect.
3. Prepare a new M47-compliant authorization packet documenting the repair.
4. Submit for external review.
5. Execute only if a new explicit authorization token is returned.

This is not authorization for any of those steps.

---

## Verdict

```
accept_m55_valid_red_watch_rows_open_no_rerun
```

Both scenarios are accepted as valid red results with both watch rows remaining open. The M54 authorization token is consumed. Any future run requires separate authorization.
