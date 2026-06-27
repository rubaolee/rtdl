# Goal3769 HIPRT Fixed-Radius Threshold Flags

Date: 2026-06-07

## Purpose

Goal3769 adds the per-query flag output that Goal3768 intentionally did not
claim. It is a generic HIPRT prepared fixed-radius threshold-flags primitive
for 3D point workloads. Given a prepared search-point set and a query batch, it
returns one boolean-style flag per query indicating whether that query reached
the caller-provided neighbor threshold.

The new native symbol is:

`rtdl_hiprt_write_prepared_fixed_radius_threshold_flags_3d`

The Python-facing methods are:

- `PreparedHiprtFixedRadiusNeighbors3D.threshold_flags(query_points, threshold=...)`
- `PreparedHiprtFixedRadiusNeighbors3D.threshold_reached_flags(query_points, threshold=...)`

## Implementation

- Added `RtdlFixedRadiusThresholdFlags3DKernel`.
- Added lazy `threshold_flags_kernel` compilation on
  `PreparedFixedRadiusNeighbors3D`.
- Added a C ABI that writes a caller-sized `uint32_t` flag buffer.
- Added Python tuple-of-bool outputs for prepared HIPRT fixed-radius handles.
- Added `fixed_radius_grouped_stream_flags_3d` to the engine feature matrix.
- Updated the v2.10 AMD/HIPRT parity matrix: `rt_dbscan` now has no missing
  generic HIPRT contracts and moves to `ready_for_amd_functional_pod`.

## Evidence

Artifact:

`docs/reports/goal3769_hiprt_fixed_radius_threshold_flags_a5000.json`

Environment:

- GPU: NVIDIA RTX A5000
- Source commit: `a7264d39`
- Scoped source dirty: `false`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- Backend route: HIPRT through CUDA/Orochi on NVIDIA hardware

Clean validation from `/root/rtdl_goal3769_clean`:

```text
make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
python3 -m unittest \
  tests.goal3769_hiprt_fixed_radius_threshold_flags_test \
  tests.goal3768_hiprt_fixed_radius_threshold_count_test \
  tests.goal566_hiprt_prepared_nn_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 18 tests passed.
- The clean source commit was `a7264d39`.
- The scoped source status was clean.

Correctness sample:

- Threshold: `3`
- Expected flags from prepared fixed-radius rows: `[true, true, true, false]`
- HIPRT prepared threshold flags: `[true, true, true, false]`
- Flag match: `true`
- Sum of flags matched scalar threshold-count: `true`

## Parity Position

After Goals3768 and 3769, the `rt_dbscan` HIPRT row in the v2.10 AMD/HIPRT
parity matrix has no missing generic contracts and is marked
`ready_for_amd_functional_pod`.

This is still not AMD hardware evidence. It does not authorize release, AMD
performance, broad RT-core, whole-app speedup, paper reproduction, or public
benchmark claims.

## Next Step

The next required step for `rt_dbscan` is AMD HIPRT functional validation. If
AMD hardware passes, performance work should focus on resident batching and the
partner/runtime component-continuation path, not app-specific DBSCAN native
logic.
