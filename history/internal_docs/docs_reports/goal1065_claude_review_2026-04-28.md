# Goal1065 Claude Review

Date: 2026-04-28
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Checks performed

### 1. Missing artifacts are correctly gated

PASS. When `not path.exists()`, the row is emitted with `artifact_status: "missing"` and `review_status: "needs_cloud_artifact"`. The `overall_status` resolves to `"needs_cloud_artifacts"` whenever `missing_count > 0` (and no other blocked row exists). The current run output confirms this: all 4 expected artifacts are missing and `overall_status == "needs_cloud_artifacts"`. Test `test_default_intake_waits_for_goal1062_cloud_artifacts` verifies this path explicitly.

### 2. Validation failures block the intake

PASS. `_validation_status` enforces per-app requirements before returning `"validation_passed"`:

- **facility_knn_assignment**: rejects `skip_validation: true`, requires `mode == "optix"` and `matches_oracle == true`.
- **robot_collision_screening**: requires `validated == true`, `matches_oracle == true`, `mode == "optix"`, `input_mode == "python_objects"`, and `result_mode == "pose_flags"`.

Any failing check returns `"blocked"` with a specific reason. `overall_status` becomes `"blocked"` when `blocked_count > 0`. Additionally, a manifest validation row that contains `--skip-validation` is itself blocked — correctly preventing oracle-bypassed artifacts from being counted as validation evidence. Test `test_bad_validation_blocks_intake` covers the `validated: false` case and confirms `payload["valid"] == False` and `overall_status == "blocked"`.

### 3. Timing floor failures produce the correct status

PASS. `_timing_status` requires timing rows to carry `--skip-validation` (raises `"blocked"` if absent), then extracts the RTX phase duration and compares it to `row["timing_floor_sec"]`. Both timing rows in the manifest carry `timing_floor_sec == 0.100`. A phase below that floor yields `review_status: "timing_below_floor"` and `overall_status: "timing_floor_not_met"` (distinct from `"blocked"`). Test `test_below_floor_timing_keeps_public_wording_blocked` verifies `overall_status == "timing_floor_not_met"` and `timing_below_floor_count == 1` when facility timing is 0.02 s.

### 4. `ready_for_public_wording_review` requires all four gates

PASS. The condition (script:161–168) is:

```
overall_status = "ready_for_public_wording_review"
    if missing_count == 0
    and validation_passed == 2
    and timing_passed == 2
```

All three conditions must hold simultaneously. A single missing artifact, validation failure, or timing miss prevents this status. Test `test_complete_good_artifacts_are_ready_for_public_wording_review_not_authorized` exercises the happy path.

### 5. No speedup claims authorized; no public wording changed

PASS. `public_speedup_claim_authorized` is hardcoded `False` in every row (script:108). `public_speedup_claim_authorized_count` is hardcoded `0` in the output (script:184). The `boundary` field states:

> "This intake checks copied Goal1062 artifacts only. It does not run cloud, change public wording, authorize release, or authorize public RTX speedup claims."

This boundary appears at both the top-level output and in the markdown `## Boundary` section. The script writes no files other than the two report outputs and invokes no pod, cloud, or wording-status APIs. `ready_for_public_wording_review` is a status string that gates the next review step; it does not itself authorize anything.

### 6. Manifest alignment

PASS. `build_intake` calls `build_manifest()` directly, so the 4-row structure (2 correctness_validation + 2 large_timing_repeat, one each for facility and robot) is always in sync with Goal1062. The manifest's own `valid` precondition enforces that validation rows have no `--skip-validation` and timing rows all have a floor set.

### 7. Goal1063 consistency

Goal1063's accepted audit established that only `facility_knn_assignment` and `robot_collision_screening` are pod-ready now, via exactly the 4 rows in Goal1062. Goal1065's intake operates over those same 4 rows. No new apps are introduced; the scope is consistent.

---

## Minor observations (non-blocking)

**`valid: true` / exit-code 0 on non-blocked states.** `valid = (blocked_count == 0)` and the CLI exits 0 when `valid`. This means the script exits 0 for `"needs_cloud_artifacts"` and `"timing_floor_not_met"` as well as `"blocked"`. This is an intentional design choice — the script ran successfully and produced a status report; only provably wrong artifacts (JSON errors, validation failures) are treated as fatal. `overall_status` is the authoritative signal for pipeline decisions. The test suite asserts `overall_status`, not `valid`, for non-blocked cases, and the boundary statement makes the distinction clear.

**`or`-chain in `_timing_phase_sec` (facility, script:75).** `stats.get("median_sec") or stats.get("max_sec") or stats.get("min_sec")` silently falls through if `median_sec` is 0.0. A zero timing value is physically implausible for an RTX query at the required scale, so this is not a real risk, but it is worth noting.

Neither observation is a defect given the project's current scope and scale constraints.

---

## Issues

None blocking.

---

## Verdict: ACCEPT

Goal1065 correctly handles all four required states: missing artifacts produce `needs_cloud_artifact` rows and `needs_cloud_artifacts` overall status; validation failures produce `blocked`; timing below the 100 ms floor produces `timing_floor_not_met`; and `ready_for_public_wording_review` is set only when all 4 artifacts are present, both validation rows pass oracle parity, and both timing rows clear the floor. No speedup claims are authorized and no public wording is changed at any point in this script. The boundary is stated twice in every markdown output and is consistent with Goal1062 and Goal1063 boundaries.
