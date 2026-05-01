# Goal1073 Claude Review

Date: 2026-04-28
Reviewer: Claude Sonnet 4.6 (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Scope

Review of Goal1073 as an artifact-intake gate for the four active Goal1072 cloud-batch rows.
Files reviewed:
- `scripts/goal1073_goal1072_artifact_intake.py`
- `tests/goal1073_goal1072_artifact_intake_test.py`
- `docs/reports/goal1073_goal1072_artifact_intake_2026-04-28.md`
- `scripts/goal1072_post_scale_up_rtx_pod_batch.py`
- `docs/reports/goal1072_claude_review_2026-04-28.md`
- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`

## Findings

### 1. Exactly four active artifacts intaked — PASS

`build_intake` iterates `manifest["rows"]` from `build_manifest()`, which produces exactly 4 rows:

| App | Path | Phase |
| --- | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `correctness_validation` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `large_timing_repeat` |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` |

`test_missing_artifacts_require_cloud` independently asserts `expected_artifact_count == 4`.
The generated intake report also shows `expected artifacts: 4` and `missing artifacts: 4`.

### 2. Barnes-Hut exclusion preserved as non-active — PASS

`build_intake` iterates only `manifest["rows"]`; Barnes-Hut appears only in `manifest["excluded_rows"]`
and is passed through as `payload["excluded_rows"]` without entering the intake loop.
The intake report confirms `excluded rows: 1` and the excluded-rows table shows
`barnes_hut_force_app / node_coverage_prepared` with `blocked_contract_reframe_required`.
`test_missing_artifacts_require_cloud` asserts `payload["excluded_rows"][0]["app"] == "barnes_hut_force_app"`,
and `test_cli_writes_intake_files` asserts Barnes-Hut appears in the markdown output.

### 3. Validation rows independently re-checked from artifact JSON — PASS

`_validation_status` inspects the artifact payload directly, not the manifest's `requires_validation`
flag. It first cross-checks `row["contains_skip_validation"]` (derived from the manifest command
string) to block any validation row that was incorrectly generated with `--skip-validation`.

For `facility_knn_assignment`, `_prepared_decision_validation` reads:
- `artifact["parameters"]["skip_validation"]` must not be `True`
- `artifact["scenario"]["mode"]` must equal `"optix"`
- `artifact["scenario"]["result"]["matches_oracle"]` must be exactly `True`

For `robot_collision_screening`, five independent fields are checked:
- `artifact["validated"] is True`
- `artifact["matches_oracle"] is True`
- `artifact["mode"] == "optix"`
- `artifact["input_mode"] == "python_objects"`
- `artifact["result_mode"] == "pose_flags"`

None of these delegate back to the manifest's stored assertion; each reads raw artifact content.
`test_bad_validation_artifact_blocks` confirms a `matches_oracle=False` facility artifact
sets `overall_status == "blocked"` and `blocked_count == 1`.

### 4. Timing medians and floors independently checked — PASS

`_timing_status` first cross-checks that `row["contains_skip_validation"]` is `True`; a
timing artifact that was not generated with `--skip-validation` is blocked outright.

Median extraction navigates the artifact JSON independently:
- Facility: `artifact["scenario"]["timings_sec"]["optix_query_sec"]["median_sec"]`
- Robot: `artifact["phases"]["prepared_pose_flags_warm_query_sec"]["median_sec"]`

Neither path trusts a cached summary field. The floor (`0.100` s from the manifest row) is then
compared against the extracted value. Three distinct statuses result:

| Condition | Status |
| --- | --- |
| median absent or non-numeric | `blocked` |
| median ≥ floor | `timing_floor_passed` |
| median < floor | `timing_below_floor` |

`test_missing_median_blocks_timing_artifact` confirms that an artifact with `min_sec`/`max_sec`
but no `median_sec` sets `blocked`. `test_below_floor_is_not_claim_ready` confirms
`median_sec=0.01` yields `timing_floor_not_met` and `public_speedup_claim_authorized_count == 0`.

The `overall_status` logic requires `validation_passed == 2 and timing_passed == 2` (no missing,
no below-floor) before reaching `ready_for_public_wording_review`; even that state does not
authorize a claim.

### 5. Malformed and failed artifacts blocked — PASS

- Unreadable / invalid JSON → `artifact_status: unreadable_json`, `review_status: blocked`
- Validation artifact with `matches_oracle` false, wrong mode, or `skip_validation` set → `blocked`
- Timing artifact with absent median → `blocked`
- `overall_status == "blocked"` when `blocked_count > 0`
- `valid == (blocked_count == 0)` — `main()` exits non-zero on any block

Missing artifacts are `needs_cloud_artifact` (not `blocked`), consistent with the design that
intake can run before artifacts arrive; `valid` is true when nothing is actively wrong.

### 6. Public RTX speedup claims not authorized — PASS

Every row's `base` dict hardcodes `"public_speedup_claim_authorized": False`.
`build_intake` hardcodes `"public_speedup_claim_authorized_count": 0` unconditionally.
The `boundary` field reads: "does not authorize public RTX speedup claims" — matching the
language required by the REFRESH_LOCAL constraint and consistent with Goal1072's boundary.

`ready_for_public_wording_review` is the maximum reachable `overall_status`; it denotes
readiness for a subsequent wording review step, not claim authorization itself.
All five test methods assert `public_speedup_claim_authorized_count == 0`.

### 7. Test coverage — PASS WITH MINOR GAP

Five test methods cover:
- Missing artifacts → `needs_cloud_artifacts`, `valid=True`, count=4, Barnes-Hut excluded (m1)
- Goal1071 stand-in artifacts achieving `ready_for_public_wording_review` (m2)
- Bad facility validation artifact → `blocked` (m3)
- Timing artifact with absent median → `blocked` (m4)
- Below-floor timing → `timing_floor_not_met`, not claim-ready (m5)
- CLI end-to-end: JSON and markdown files written, counts correct (m6)

Minor gap: there is no dedicated test for a failing robot-side validation artifact.
The robot path has five independent checks in `_validation_status`, all exercised by code
inspection but none by an explicit failure test. This is non-blocking given the facility
path's structural similarity and the complete structural coverage of all other states.

## Issues

**None blocking.**

1. **(Non-blocking) Robot validation failure untested.** No test asserts that, e.g.,
   `robot artifact["matches_oracle"] = False` sets `blocked`. The facility-side analog is
   tested. Recommend adding a robot validation failure case in a follow-up.

2. **(Informational) Timing floor inherited from manifest.** Goal1073 uses `row["timing_floor_sec"]`
   from the Goal1072 manifest (0.100 s) rather than re-asserting the floor value independently.
   This is acceptable given the controlled direct import, but a future standalone intake should
   pin the floor explicitly.

3. **(Informational) `valid` is "not blocked", not "all passed".** `valid=True` when artifacts
   are missing. This is intentional (consistent with Goal1070 behavior) and `overall_status`
   carries the full discriminating detail, but the field name can mislead a quick scan.

## Verdict

**ACCEPT**

Goal1073 correctly intakes exactly the four active Goal1072 artifacts, preserves Barnes-Hut as
a non-active excluded row, independently re-reads validation fields and timing medians from
artifact JSON, blocks malformed or failed artifacts at every tested failure mode, and hardcodes
`public_speedup_claim_authorized = False` in all paths. The overall-status ladder enforces that
no state short of two passing validations and two passing timing floors reaches even
`ready_for_public_wording_review`, and that state itself does not authorize a public claim.
No structural defects found; the one minor gap (no robot validation failure test) is
non-blocking.
