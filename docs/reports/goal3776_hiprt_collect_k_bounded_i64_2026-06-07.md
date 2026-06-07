# Goal3776 HIPRT COLLECT_K_BOUNDED i64 Materializer

## Purpose

Goal3776 closes the next generic HIPRT contract needed by the v2.10 AMD/HIPRT
benchmark-parity lane: bounded witness row materialization. The implementation
adds an app-name-free HIPRT C ABI:

`rtdl_hiprt_collect_k_bounded_i64`

The contract matches the existing Embree and OptiX host-native materializers:

- input rows are dense int64 candidate-id rows;
- rows are lexicographically sorted;
- duplicate rows are removed before capacity checking;
- `emitted_count` reports the exact unique row count;
- overflow fails closed before partial materialization;
- no contact, collision, manifold, or other app semantics enter the native
  engine.

## Scope

Files changed in the implementation slice:

- `src/native/hiprt/rtdl_hiprt_api.cpp`
- `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `src/rtdsl/engine_feature_matrix.py`
- `src/rtdsl/v2_10_amd_hiprt_benchmark_parity.py`
- `src/rtdsl/primitive_hierarchy.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal3753_amd_hiprt_benchmark_parity_plan_2026-06-07.md`
- `tests/goal3776_hiprt_collect_k_bounded_i64_test.py`
- `tests/goal3753_amd_hiprt_benchmark_parity_plan_test.py`
- `tests/goal3775_hiprt_ray_triangle_closest_hit_3d_test.py`

## Contact-Manifold Effect

Before Goal3776, `contact_manifold` still listed
`bounded_contact_witness_collection` as a missing generic HIPRT contract. After
Goal3776, the app can call the same bounded row collector through
`backend="hiprt"` and the generic symbol
`rtdl_hiprt_collect_k_bounded_i64`.

This advances `contact_manifold` from `needs_generic_hiprt_extension` to
`ready_for_amd_functional_pod` in the v2.10 parity matrix.

Current v2.10 AMD/HIPRT parity summary:

| Stage | Count | Apps |
| --- | ---: | --- |
| Ready for AMD functional pod | 7 | `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `robot_collision`, `contact_manifold`, `librts_spatial_index`, `rtnn` |
| Needs generic HIPRT extension | 1 | `barnes_hut` |
| Compatibility-only, not AMD perf ready | 2 | `raydb_style`, `triangle_counting` |

## Boundary

This goal does not authorize AMD performance claims, HIPRT release claims,
public speedup wording, zero-copy wording, whole-app acceleration wording,
RTDL-beats-paper wording, or app-specific native-engine logic.

The first pod validation for this goal is expected to run on NVIDIA through the
CUDA/Orochi HIPRT route. That is functional implementation evidence for the
HIPRT backend path, not AMD hardware evidence.

## Validation Plan

Portable validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3776_hiprt_collect_k_bounded_i64_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3775_hiprt_ray_triangle_closest_hit_3d_test
```

Pod validation:

1. Fetch/reset a clean checkout to the implementation commit.
2. Build HIPRT with the official HIPRT SDK.
3. Run the Goal3776, Goal3775, Goal3774, and Goal3753 focused tests.
4. Generate `docs/reports/goal3776_hiprt_collect_k_bounded_i64_a5000.json`
   recording source commit, scoped dirty status, sample parity, overflow
   fail-closed behavior, and claim-boundary flags.

