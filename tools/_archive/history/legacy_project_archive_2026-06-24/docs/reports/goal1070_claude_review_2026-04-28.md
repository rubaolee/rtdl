# Goal1070 Claude Review

Date: 2026-04-28

Reviewer: Claude (claude-sonnet-4-6)

## Verdict: PASS with minor concerns

Goal1070 correctly implements all five required properties. No blocking defects found.

---

## Files Reviewed

- `scripts/goal1070_goal1068_artifact_intake.py`
- `tests/goal1070_goal1068_artifact_intake_test.py`
- `docs/reports/goal1070_goal1068_artifact_intake_2026-04-28.json`
- `docs/reports/goal1070_goal1068_artifact_intake_2026-04-28.md`
- `docs/reports/goal1068_two_ai_consensus_2026-04-28.md`
- `scripts/goal1068_next_rtx_pod_efficiency_batch.py` (manifest source, for floor/row verification)

---

## Criterion-by-Criterion Assessment

### 1. Expects exactly six Goal1068 artifacts — PASS

The manifest (`build_manifest`) produces exactly six rows (3 apps × 2 phases: correctness_validation and large_timing_repeat). The intake sets `expected_artifact_count = len(rows)` from that manifest. The produced JSON confirms `"expected_artifact_count": 6` and `"missing_artifact_count": 6` in the current (no-artifacts) run. `test_default_intake_waits_for_goal1068_cloud_artifacts` asserts both counts explicitly.

### 2. Validates facility / robot / Barnes-Hut correctness rows — PASS

**Facility and Barnes-Hut** (`_prepared_decision_validation`): enforces three conditions — `skip_validation` must not be `True`, `scenario.mode` must be `"optix"`, and `scenario.result.matches_oracle` must be exactly `True`. Any failure returns `"blocked"`.

**Robot** (`_validation_status` branch for `robot_collision_screening`): enforces five conditions — `validated == True`, `matches_oracle == True`, `mode == "optix"`, `input_mode == "python_objects"`, `result_mode == "pose_flags"`. All five must be literally `True`/exact strings; missing keys return `"blocked"`.

No path exists for a validation row to return a passing status without satisfying all conditions. `test_bad_barnes_validation_blocks_intake` confirms that `matches_oracle: false` blocks the entire intake.

### 3. Timing floor enforced for all timing rows, zero median not hidden — PASS

All three timing rows in the manifest carry `timing_floor_sec=0.100` (verified in `goal1068_next_rtx_pod_efficiency_batch.py` lines 102, 153, 204). The intake enforces the floor in `_timing_status`:

```python
if isinstance(floor, (int, float)) and phase_sec < float(floor):
    return "timing_below_floor", ...
```

**Zero median is not hidden.** `_prepared_decision_timing` uses `if value is None` (identity check), not a truthiness check. If `median_sec` is `0`, the value is `0`, `0 is None` is `False`, so the zero is returned as `0.0` and triggers `timing_below_floor` since `0.0 < 0.100`. `test_barnes_below_floor_keeps_review_blocked` confirms that a below-floor median (`0.02`) is preserved as `rtx_phase_sec=0.02` and yields `timing_below_floor` status.

### 4. Never authorizes public RTX speedup claims — PASS

`public_speedup_claim_authorized: False` is hardcoded in the `base` dict for every row. `public_speedup_claim_authorized_count: 0` is hardcoded in the output dict (not derived from rows, so it cannot accidentally become nonzero). The boundary string in both JSON and Markdown explicitly states "does not authorize public RTX speedup claims". Three tests assert `payload["public_speedup_claim_authorized_count"] == 0` across all scenarios.

### 5. Adequate tests — PASS (with coverage gaps noted)

Five tests are present:

| Test | What it covers |
| --- | --- |
| `test_default_intake_waits_for_goal1068_cloud_artifacts` | Empty artifact dir → 6 missing, no authorization |
| `test_complete_good_artifacts_are_ready_for_review_not_authorized` | All 6 good → 3 validation passed, 3 timing passed, ready_for_public_wording_review, no authorization |
| `test_barnes_below_floor_keeps_review_blocked` | Barnes timing median below floor → timing_floor_not_met, correct rtx_phase_sec captured |
| `test_bad_barnes_validation_blocks_intake` | Barnes validation fails matches_oracle → blocked, valid=False |
| `test_cli_writes_json_and_markdown` | CLI end-to-end: JSON and Markdown files written |

The core paths (all pass, floor violation, validation failure, missing, CLI) are covered. The tests are sufficient to provide confidence in the critical properties.

---

## Minor Concerns (Non-Blocking)

**C1: `valid=True` when all six artifacts are missing.**
`valid` is defined as `blocked_count == 0`. When artifacts are missing, `blocked_count=0` and `valid=True`, so `main()` exits with code 0. This is internally consistent (nothing is wrong with what is present), but a caller that relies on exit code to detect readiness would not distinguish "waiting for artifacts" from "all artifacts present and passing". The `overall_status` field (`needs_cloud_artifacts`) is the correct signal; callers must check it, not just exit code.

**C2: `_prepared_decision_timing` falls back to `max_sec` when `median_sec` is absent.**
If an artifact has no `median_sec` key, the function falls back to `max_sec`, then `min_sec`. This does not hide a zero median (the `is None` guard is correct), but could silently accept an artifact that lacks a median by substituting the maximum. A strict implementation would block on a missing median. In practice the manifest requires `median_sec` from the pod runner, so this gap is unlikely to matter, but it is a defense-in-depth weakness.

**C3: No test for bad facility or robot validation.**
`test_bad_barnes_validation_blocks_intake` covers Barnes-Hut. There are no analogous tests for facility (`matches_oracle: false`, `mode != "optix"`, or `skip_validation: true`) or for robot (wrong `mode`, wrong `input_mode`, `validated: false`). The code paths are exercised for Barnes-Hut; the facility and robot paths share the same guards but lack direct test coverage for their failure modes.

**C4: No test for timing floor when `timing_floor_sec` is `None`.**
If the manifest ever produced a timing row with `timing_floor_sec=None`, `isinstance(None, (int, float))` is `False`, and the row would silently return `timing_floor_passed` with no floor enforced. This cannot happen with the current manifest (timing rows all have 0.100), but is untested.

---

## Summary

Goal1070 correctly expects six Goal1068 artifacts, validates facility/robot/Barnes-Hut correctness rows with appropriate field-level checks, enforces the 0.100 s timing floor for all timing rows using an identity-safe zero check that does not hide zero medians, hardcodes `public_speedup_claim_authorized=False` at both the row and aggregate level with an explicit boundary statement, and provides five tests covering the critical scenarios. The four minor concerns are defense-in-depth gaps rather than functional defects. **Goal1070 is accepted.**
