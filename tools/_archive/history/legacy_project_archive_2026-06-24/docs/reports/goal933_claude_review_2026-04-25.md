# Goal933 Claude Review — Prepared Segment/Polygon OptiX Local Work

**Date:** 2026-04-25
**Reviewer:** Claude (claude-sonnet-4-6)
**Verdict: ACCEPT**

---

## Summary

Goal933 adds a prepare/run/destroy lifecycle for segment-polygon hit-count traversal in the OptiX backend, replacing the one-shot call pattern that was identified in Goal929 as unfit for warm-path benchmarking. The goal makes no public claims. It is correctly scoped as evidence-contract infrastructure for the next RTX cloud run.

---

## What Was Reviewed

| Layer | File(s) |
|---|---|
| C ABI declaration | `src/native/optix/rtdl_optix_prelude.h` |
| C ABI dispatch | `src/native/optix/rtdl_optix_api.cpp` lines 308–345 |
| Native workload class | `src/native/optix/rtdl_optix_workloads.cpp` lines 3552–3703 |
| Python wrapper | `src/rtdsl/optix_runtime.py` `PreparedOptixSegmentPolygonHitcount2D` |
| Python public API | `src/rtdsl/__init__.py` (export) |
| Profiler | `scripts/goal933_prepared_segment_polygon_optix_profiler.py` |
| Manifest | `scripts/goal759_rtx_cloud_benchmark_manifest.py` |
| Artifact analyzer | `scripts/goal762_rtx_cloud_artifact_report.py` |
| Tests | `tests/goal933_prepared_segment_polygon_optix_test.py` |
| Tests | `tests/goal933_prepared_segment_polygon_profiler_test.py` |

---

## C ABI — Correct

The three-function ABI (`prepare`, `run_prepared`, `destroy`) follows exactly the same pattern as the existing `PreparedRayAnyHit2D` and `PreparedFixedRadiusCountThreshold2D` families.

**Prepare** (`rtdl_optix_api.cpp:308`): null-checks on `prepared_out`, `polygons`, `vertices_xy`; UINT32_MAX guard on `polygon_count`. Consistent with peers.

**Run** (`rtdl_optix_api.cpp:329`): Delegates null checks on `rows_out`/`row_count_out` into the workloads function rather than repeating them at the dispatch layer. Functionally correct; the workloads function checks at line 3635. Other `run_prepared_*` dispatch functions in this file do the same (see `rtdl_optix_run_prepared_fixed_radius_count_threshold_2d` at line 524). Minor inconsistency vs. one-shot functions, but in-pattern.

**Destroy** (`rtdl_optix_api.cpp:342`): `delete reinterpret_cast<PreparedSegmentPolygonHitcount2D*>(prepared)` — `delete nullptr` is safe; no guard needed.

---

## Native Class `PreparedSegmentPolygonHitcount2D` — Correct

`src/native/optix/rtdl_optix_workloads.cpp:3552`

- Constructor copies polygon refs and vertices to host vectors (float), uploads to GPU, and builds the custom-AABB BVH once. AABB construction uses the original double-precision `vertices_xy`, consistent with the one-shot path.
- `vertex_xy_count % 2 != 0` guard at line 3573 catches malformed input.
- `run_prepared_segment_polygon_hitcount_2d_optix` at line 3627: empty-polygon fast-path at line 3645 returns zero counts without launching OptiX — correct. UINT32_MAX segment count guard at line 3637 in place. The reuse of the cached `g_segpoly.pipe` pipeline (compiled once via `std::call_once`) avoids re-JIT across `prepare` calls.
- float precision downcast (double→float) for segment and vertex coordinates is consistent with all other workloads in this file and is undocumented in the Python docstring, but this is an established project-wide convention.

---

## Python Wrapper — Correct

`src/rtdsl/optix_runtime.py:799`

- Follows the `PreparedOptixFixedRadiusCountThreshold2D` pattern exactly: `__init__`, `run`, `close`, `__enter__`/`__exit__`, `__del__` with exception swallow.
- `_find_optional_backend_symbol` used for all three symbols. If the prepare symbol is absent, `__init__` raises immediately with a clear error message naming the missing symbol. If the destroy symbol is absent during `close`, the method skips the call — handle leaks in that case, but `if handle.value:` prevents calling destroy on a null handle. This is defensive and correct given the deploy guarantee.
- `closed` property and double-close guard in `close()` are correct.
- `run()` on an empty polygon scene returns zero-hit tuples without touching the native library — consistent with the C-layer empty-polygon fast-path.

---

## Profiler — Correct

`scripts/goal933_prepared_segment_polygon_optix_profiler.py`

- Phase separation is properly instrumented: `input_build_sec`, `optix_prepare_sec`, per-iteration `optix_query_sec` and `python_postprocess_sec`, single-run `validation_sec` (after all query iterations), `optix_close_sec`.
- `close()` is in a `finally` block — safe against iteration exceptions.
- `matches_oracle` is checked only when `mode == "run" and not skip_validation` — correct; dry-run intentionally skips OptiX.
- Oracle comparison uses `_digest` (hit_sum, row_count, positive_count), not order-dependent row equality — consistent with other profilers in this project.
- `strict_failures` correctly fails when `matches_oracle is not True` (i.e., both `False` and `None` trigger failure), which is the right sentinel for unchecked runs.
- `dry-run` mode records `cpu_reference_total_sec` only, with no OptiX fields — correct signal to the cloud-run reviewer that the machine cannot be trusted for timing.
- Validation runs once (not per iteration) to avoid polluting query timing. Digest of the last iteration only is compared. This is adequate for correctness gating.

---

## Manifest Update — Correct

`scripts/goal759_rtx_cloud_benchmark_manifest.py` routes the deferred `road_hazard_screening` and `segment_polygon_hitcount` cloud entries to the Goal933 profiler with `--mode run`. The artifact output paths (`goal933_road_hazard_prepared_summary_rtx.json`, `goal933_segment_polygon_hitcount_prepared_rtx.json`) are distinct from Goal929 artifacts. No existing passing gates were removed.

---

## Artifact Analyzer — Correct

`scripts/goal762_rtx_cloud_artifact_report.py` detects `schema_version == "goal933_prepared_segment_polygon_optix_contract_v1"` and extracts `optix_prepare_sec`, `optix_query_sec.median_sec`, `python_postprocess_sec.median_sec`, `optix_close_sec`, `matches_oracle`, and `priority_segment_count` from the artifact. Both segment and road-hazard scenario paths are handled.

---

## Test Coverage

| Test | What It Covers |
|---|---|
| `test_empty_prepared_polygon_scene_returns_zero_hit_counts_without_native_library` | Zero-polygon fast-path, context-manager protocol |
| `test_closed_prepared_scene_is_rejected` | Double-use-after-close guard |
| `test_native_sources_export_prepared_segment_polygon_abi` | ABI symbol presence in all three source files |
| `test_python_runtime_exports_prepared_segment_polygon_api` | Public Python module export |
| `test_dry_run_segment_profile_records_contract_without_optix` | Dry-run profiler schema, contract fields |
| `test_dry_run_road_profile_records_priority_summary` | Road-hazard scenario, priority count |
| `test_cli_writes_json` | CLI invocation and JSON output |
| `test_artifact_analyzer_accepts_goal933_schema_for_segment_and_road` | Analyzer parsing of both scenario artifact types |
| `test_rejects_invalid_scenario` | Input validation |

Coverage is adequate for a local prep goal. There is no test for the case where `mode == "run"` fails oracle (`matches_oracle == False` → `strict_pass == False`), but this is an infrastructure-only goal and the negative case is directly readable from the code.

---

## Claim Boundary Verification

The report's stated "not allowed" list is enforced in the code:

- No speedup ratio is computed anywhere in the profiler or analyzer.
- `cloud_claim_contract["non_claim"]` field is propagated into every artifact.
- `boundary` string in the profiler output explicitly prohibits speedup claims.
- `app_support_matrix.py` was not modified in a way that promotes road-hazard or segment-polygon apps.

---

## Issues

**None blocking.** Two minor observations for awareness:

1. **Consistency**: `rtdl_optix_run_prepared_segment_polygon_hitcount_2d` at the API dispatch layer does not repeat the `rows_out`/`row_count_out` null-check that one-shot functions do at the same layer. Functionally safe (the check is inside the workloads function), and consistent with other `run_prepared_*` dispatchers — but worth noting if a future API audit expects uniform placement.

2. **Float precision**: The prepared object stores and uploads vertices as `float`. This is the established project convention. The Python docstring does not mention it. Not a bug, but relevant if sub-meter coordinate accuracy matters for a future workload class built on this pattern.

---

## Test Run

```
Ran 40 tests in 0.923s
OK
```

All 40 tests pass (Goal933 suite + manifest + analyzer + readiness gate + rt-core series).

---

## Verdict

**ACCEPT.**

Goal933 is correctly scoped local prep. The three-layer change (C ABI / Python wrapper / profiler) is internally consistent, matches existing prepared-scene patterns, enforces claim boundaries explicitly, and passes all tests. Ready to batch with other local prep before the next RTX cloud run.
