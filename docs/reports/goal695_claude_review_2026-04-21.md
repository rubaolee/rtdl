# Goal 695 Claude Review: OptiX Fixed-Radius Count/Threshold Prototype

**Date:** 2026-04-21
**Reviewer:** Claude (claude-sonnet-4-6)
**Verdict:** ACCEPT

---

## Summary

Goal 695 introduces a single new primitive — `rtdl_optix_run_fixed_radius_count_threshold` / `fixed_radius_count_threshold_2d_optix` — and wires it into the outlier-detection and DBSCAN apps as an opt-in summary mode. The changes are narrow, honest about their limits, and use a genuine OptiX traversal path. No performance claims are made and the Linux/RTX parity gate is correctly preserved.

---

## Scope Honesty: PASS

The changes are strictly limited to what Goal 694 authorized:

- Fixed-radius count/threshold rows for outlier detection (`--optix-summary-mode rt_count_threshold`).
- Fixed-radius core-flag rows for DBSCAN (`--optix-summary-mode rt_core_flags`).
- No changes to Hausdorff, ANN/KNN, or Barnes-Hut code paths.
- KNN rows continue to use the existing CUDA brute-force kernel (`knn_rows_cuda` / `knn_rows_cuda_3d`), unmodified.
- The boundary strings in both apps' output dicts explicitly disclaim KNN/Hausdorff/Barnes-Hut.

The app `run_app()` functions validate `optix_summary_mode` against a strict allowlist and raise `ValueError` on unknown values; no accidental scope creep can slip through a typo.

---

## True OptiX Traversal — Not a Wrapper: PASS

The critical check. The embedded kernel (`kFixedRadiusCountRtKernelSrc`, `rtdl_optix_core.cpp:1611–1677`) is an independent OptiX program group set, not a shim over the old neighbor-row CUDA kernel:

| Program | Name | What it does |
|---|---|---|
| Raygen | `__raygen__frn_count_probe` | Fires one vertical ray per query: origin `(qx, qy, -radius)`, direction `+z`. Uses `optixTrace(params.traversable, ...)`. |
| Intersection | `__intersection__frn_count_isect` | Fetches query/target points, tests `dx²+dy² <= radius²`, calls `optixReportIntersection`. |
| Any-hit | `__anyhit__frn_count_anyhit` | Increments payload count; calls `optixTerminateRay()` when `count >= threshold`. |
| Miss | `__miss__frn_count_miss` | No-op. |

Each search point becomes a custom-primitive AABB spanning `(x ± aabb_radius, y ± aabb_radius, z ∈ [-aabb_radius, aabb_radius])`, built with `build_custom_accel` into a real OptiX BVH traversable. Launch is via `optixLaunch` with one thread per query. This is the Goal 694 2.5D construction, correctly implemented.

The old fixed-radius neighbor kernel (`run_fixed_radius_neighbors_cuda`) is untouched; `rtdl_optix_run_fixed_radius_count_threshold` calls `run_fixed_radius_count_threshold_rt` (workloads.cpp), which builds a fresh pipeline and launches through `optixLaunch`. There is no code path that falls through to the old neighbor-row accumulator.

**One minor note:** The `kRadiusPad` of `1.0e-4f` applied to AABB extents (but not to the intersection test radius `params.radius`) means AABB traversal candidates include a small guard band. This is intentional and correct — the exact test in `__intersection__frn_count_isect` uses the unpadded `params.radius`, so false candidates from the guard band are rejected there. No correctness risk; document as intended behavior.

---

## App Wiring Correctness: PASS

**Outlier detection (`rtdl_outlier_detection_app.py`):**
- `_density_rows_from_count_rows` correctly interprets `threshold_reached == 0` as "count was not truncated," meaning a low count is a true outlier. A point is `is_outlier` only when `neighbor_count < min_neighbors_including_self AND threshold_reached == 0`. This correctly avoids false-positives on non-outlier points whose counts were truncated at threshold.
- When `optix_summary_mode == "rt_count_threshold"`, `neighbor_rows` is explicitly set to `()`, so `neighbor_row_count == 0` is guaranteed. `matches_oracle` compares outlier label lists (not full row tuples) against the brute-force oracle, which is the right comparison given that threshold counts are intentionally truncated.

**DBSCAN (`rtdl_dbscan_clustering_app.py`):**
- `_core_flag_rows_from_count_rows` correctly sets `is_core` when `neighbor_count >= min_points OR threshold_reached == 1`. This is logically equivalent to the full-count test because `threshold == MIN_POINTS` and a `threshold_reached` flag means the count saturated at `MIN_POINTS`.
- When `optix_summary_mode == "rt_core_flags"`, `cluster_rows` is explicitly `()`. The result makes no clustering-expansion claims; the boundary string says "core predicate prototype, not KNN/Hausdorff/Barnes-Hut."

Both apps' `boundary` fields are user-visible in JSON output and contain accurate disclaimer text.

---

## Test Coverage: PASS (with caveats)

`tests/goal695_optix_fixed_radius_summary_test.py` covers three cases:

1. **Outlier app threshold rows** — mocks `fixed_radius_count_threshold_2d_optix`, verifies `matches_oracle`, `neighbor_row_count == 0`, `native_summary_row_count == point_count`, correct outlier IDs `[7, 8]`, and boundary text.
2. **DBSCAN app core flag rows** — same structure, verifies `cluster_rows == ()`, `len(core_flag_rows) == point_count`, correct core flags, and boundary text.
3. **Native source inspection** — reads the live `.cpp` and `optix_runtime.py` files and asserts all five required symbols/phrases are present: `__raygen__frn_count_probe`, `__intersection__frn_count_isect`, `__anyhit__frn_count_anyhit`, `optixTrace(params.traversable`, `optixTerminateRay`, and `rtdl_optix_run_fixed_radius_count_threshold`.

**Caveat:** Tests 1 and 2 mock the native call, so they test Python wiring only. Test 3 is a source-text assertion, not a compiled execution. None of the tests exercise `optixLaunch` on real hardware. This is explicitly acknowledged in the summary document and is acceptable for a prototype at this stage; the Linux/RTX gate requirement below covers the gap.

---

## Linux Native Build / Performance Gate: PASS (correctly preserved)

The summary document states:
> "This goal does not change public app performance classifications yet. Outlier detection and DBSCAN remain `cuda_through_optix` until the new native function is built and measured on Linux/RTX-class hardware."

Verification in source:
- No `app_performance_classification` or equivalent field was modified in either app.
- `optix_runtime.py:fixed_radius_count_threshold_2d_optix` uses `_find_optional_backend_symbol` (not the asserting variant), so the function raises a descriptive `RuntimeError` if the library doesn't export the new symbol — it does not silently fall back to the old neighbor-row path in a way that could hide a missing build.
- The macOS build failure at `/opt/optix/include/optix.h` is documented and not worked around.

No speed claims, no benchmark numbers, no classification upgrades appear anywhere in the diff.

---

## Issues Found

None blocking. One informational item:

**I1 (informational) — `kRadiusPad` not documented in source:**  
`rtdl_optix_workloads.cpp:2976` uses `constexpr float kRadiusPad = 1.0e-4f` to widen AABBs without explaining in a comment that the exact intersection test uses the unpadded radius. This is a silent invariant. A one-line comment would prevent future confusion. Does not affect correctness.

---

## Verdict

**ACCEPT**

All three review axes pass:

1. **Scope is honestly limited** to fixed-radius outlier/DBSCAN core flags. No other workload touched.
2. **OptiX traversal source shape is genuine** — `optixTrace`, `optixReportIntersection`, `optixTerminateRay`, and a `build_custom_accel` BVH are all present and correctly composed. It is not a wrapper around the old neighbor-row kernel.
3. **Linux native build/parity is correctly required** before any performance claim or classification change. The gate is in place and was not bypassed.
