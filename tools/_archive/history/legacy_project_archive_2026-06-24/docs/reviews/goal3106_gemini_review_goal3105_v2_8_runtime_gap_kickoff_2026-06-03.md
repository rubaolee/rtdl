# Gemini Review - Goal3105 v2.8 Runtime Gap Kickoff

- **Goal:** Goal3105 (v2.7 Internal Closeout / v2.8 Runtime Gap Kickoff)
- **Reviewer:** Gemini (Antigravity)
- **Date:** 2026-06-03
- **Verdict:** `accept-with-boundary`

## Executive Summary

Goal3105 successfully closes the v2.7 internal development cycle focused on primitive discovery/orchestration metadata and initiates the v2.8 lane focused on benchmark-runtime engineering. It introduces a machine-readable gap map for ten promoted benchmark apps and identifies a shared, generic engineering target for v2.8. The design maintains rigorous claim boundaries against unauthorized releases and public claims.

## Review of Required Questions

### 1. Does Goal3105 correctly close v2.7 as an internal version without authorizing release or public claims?

**Yes.** 
- `docs/reports/goal3105_v2_7_internal_closeout_and_v2_8_runtime_gap_kickoff_2026-06-03.md` explicitly states that v2.7 is closed as an internal version and is not a release tag.
- `src/rtdsl/v2_8_benchmark_runtime_gap.py` implements `v2_7_internal_closeout_status()` which returns `release_authorized: False` and other claim boundary flags.
- `V2_7_INTERNAL_CLOSEOUT_STATUS` is set to `"closed_internal_version_not_release_authorization"`.

### 2. Does the v2.8 gap map cover the ten promoted benchmark apps?

**Yes.**
- `src/rtdsl/v2_8_benchmark_runtime_gap.py` defines `V2_8_PROMOTED_BENCHMARK_APPS` which includes exactly ten apps: `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `robot_collision`, `contact_manifold`, `raydb_style`, `barnes_hut`, `librts_spatial_index`, `rtnn`, and `triangle_counting`.
- The `V2_8_BENCHMARK_RUNTIME_GAP_ROWS` tuple provides a detailed gap mapping for each of these ten apps.

### 3. Is the first v2.8 runtime target genuinely generic and shared across multiple benchmark apps?

**Yes.**
- The target `typed_device_resident_result_streams_and_grouped_continuation` is designed as a shared runtime capability for typed output columns and grouped continuation.
- In `src/rtdsl/v2_8_benchmark_runtime_gap.py`, nine of the ten benchmark apps (all except `librts_spatial_index`) are mapped to this target family.
- `validate_v2_8_benchmark_runtime_gap_map` enforces that the target must cover at least seven apps and specifically includes key spatial, neighbor, and graph workloads.

### 4. Does the design preserve explicit partner choice and avoid hidden dispatch or hidden partner selection?

**Yes.**
- `V28BenchmarkRuntimeGapRow` has `automatic_partner_selection_allowed` set to `False` by default, and `__post_init__` prevents any row from authorizing it.
- The report and `v2_8_runtime_target_summary()` explicitly list "hidden partner auto-selection" and "hidden dispatch" as unauthorized and excluded from the first v2.8 target.

### 5. Does the design avoid app-specific native engine logic?

**Yes.**
- `V28BenchmarkRuntimeGapRow` includes an `app_specific_engine_logic_allowed` flag which is set to `False` and enforced by `__post_init__`.
- The decision report emphasizes that the goal is to improve the *generic* RTDL runtime without adding app-specific native engine logic.

### 6. Are the tests and validation strong enough for a kickoff/gap-map goal?

**Yes.**
- `tests/goal3105_v2_8_benchmark_runtime_gap_map_test.py` provides comprehensive coverage for the gap map structure, v2.7 closeout status, and claim boundaries.
- `validate_v2_8_benchmark_runtime_gap_map()` in `src/rtdsl/v2_8_benchmark_runtime_gap.py` provides a robust machine-readable validation gate.

## Claim Boundary

This review accepts Goal3105 as the kickoff for the v2.8 runtime engineering lane. It does not authorize:
- A v2.8 release or public release tag.
- Public speedup wording or whole-app speedup claims.
- "RT-core" or "true-zero-copy" wording for public use.
- Paper reproduction claims.
- Hidden partner selection or hidden auto-dispatch.
- App-specific native engine behavior or "baked-in" application logic.
- User-defined shader injection (deferred to v3.0).

## Verdict

`accept-with-boundary`
