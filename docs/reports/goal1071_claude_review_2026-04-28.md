# Goal1071 Claude Review

Date: 2026-04-28
Reviewer: Claude (claude-sonnet-4-6)

## Verdict

**ACCURATE** — all four claims check out against the source artifacts.

## Evidence Cross-Check

### Claim 1: Goal1068 validation passed but timing floor failed

Confirmed from `goal1070_goal1068_artifact_intake_after_pod_2026-04-28.json`:
- `validation_passed_count`: 3 (facility `matches_oracle: true`, robot `matches_oracle: true`, Barnes-Hut `matches_oracle: true`)
- `timing_floor_passed_count`: 0
- `timing_below_floor_count`: 3
- `overall_status`: `timing_floor_not_met`
- `public_speedup_claim_authorized_count`: 0

Timing medians confirmed against batch artifacts:
- Facility 800K: `optix_query_sec.median_sec` = 0.034053 s (below 0.100 s floor)
- Robot 8M: `prepared_pose_flags_warm_query_sec.median_sec` = 0.015967 s (below 0.100 s floor)
- Barnes-Hut 1M: `optix_query_sec.median_sec` = 0.004204 s (below 0.100 s floor)

### Claim 2: Facility 2.5M probe passes 100 ms floor

Confirmed from `goal1071_scale_up_probes/facility_coverage_threshold_2_5m_timing.json`:
- `parameters.copies`: 2,500,000
- `optix_query_sec.median_sec`: 0.111742 s → above floor → **passed**

### Claim 3: Robot 36M probe passes 100 ms floor

Confirmed from `goal1071_scale_up_probes/robot_prepared_pose_flags_36m_timing.json`:
- `pose_count`: 36,000,000
- `prepared_pose_flags_warm_query_sec.median_sec`: 0.102610 s → above floor → **passed**

Robot 32M near miss also confirmed: `median_sec` = 0.098737 s, just below floor.

### Claim 4: Barnes-Hut blocked by 4-node RT scene contract

Confirmed from both `barnes_hut_node_coverage_1m_timing.json` and `barnes_hut_node_coverage_validation.json`:
- `scenario.result.build_count`: 4 at both 200K and 1M body counts
- The RT scene holds only 4 one-level quadtree nodes regardless of body count; scaling bodies increases input construction and packing time but not RT traversal work, making the 100 ms floor unachievable under this contract without a redesign.

### Claim 5: No public speedup claim authorized

Confirmed — `public_speedup_claim_authorized_count: 0` in intake; all row-level `public_speedup_claim_authorized: false`; report Boundary section explicitly states no public wording change or RTX speedup claim is authorized.

## Summary

The Goal1071 report correctly states that Goal1068 validation passed (3/3) but the 100 ms timing floor failed (0/3); the facility 2.5M and robot 36M scale-up probes pass the floor; Barnes-Hut remains blocked by its structural 4-node RT contract; and no public speedup claim is authorized.
