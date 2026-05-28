# Goal2676: v2.5 Triton Partner Pivot

Status: local implementation slice, test-backed, not a release gate.

Date: 2026-05-27

## Purpose

Triton is the primary v2.5 partner. CuPy and PyTorch are not benchmark-path
partners for the v2.5 direction. The goal is to preserve the current RT-core
performance basis while making post-RT continuation work easier to write than
CuPy RawKernel or framework-specific user code.

This goal implements the first cross-layer slice of that pivot.

## Implemented Layers

| Layer | Action |
| --- | --- |
| Language contract | `plan_v2_5_partner_continuation()` now reports `preview_not_promoted` for implemented Triton/Numba preview operations, while keeping unimplemented operations descriptor-only. |
| Runtime | Added `describe_triton_partner_continuation()` and `run_triton_partner_continuation()` as generic Triton-facing entry points. Unsupported operations require an explicit reference fallback. |
| Engine boundary | Triton remains post-traversal only. It does not replace Embree/OptiX traversal and does not introduce app-specific native engine logic. |
| Primitive hierarchy | The continuation hierarchy now records a Triton-first partner continuation node instead of a NumPy/CuPy/PyTorch-style partner-array node. |
| App surface | RayDB v2.5 continuation metadata now identifies Triton as preferred partner, Numba as fallback, and CuPy/PyTorch as non-benchmark-path partners; `run_raydb_v2_5_partner_continuation_preview()` routes app-lowered group ids/values through the generic Triton dispatcher. |
| Portfolio planning | `v2_5_triton_benchmark_app_migration_plan()` records all 10 promoted benchmark apps, their current partner dependency, and the generic Triton operations needed to move each one off legacy CuPy/PyTorch continuations. |

## Torch Carrier Boundary

Torch is a tensor carrier for Triton launch in the current preview
implementation. Torch is a tensor carrier, not the v2.5 partner. The public
metadata records:

- `partner="triton"`;
- `tensor_carrier="torch_cuda_tensor_for_triton_launch"`;
- `tensor_carrier_is_partner=False`;
- `cupy_required=False`;
- `pytorch_partner_required=False`.

This makes the current implementation honest while preserving the design rule:
CuPy and PyTorch are not benchmark-path partners in v2.5.

## Current Coverage

| Operation | Triton status |
| --- | --- |
| `segmented_count_i64` | executable preview, not promoted |
| `segmented_sum_f64` | executable preview, not promoted |
| `segmented_min_f64` | executable preview, not promoted |
| `segmented_max_f64` | executable preview, not promoted |
| `compact_mask_i64` | executable preview, not promoted |
| `grouped_argmin_f64` | executable preview, not promoted |
| `bounded_collect_finalize_i64` | executable preview, not promoted |

All v2.5 continuation operations now have local Triton preview implementations
after Goals2679-2680. Python reference execution remains available for
conformance, but it does not count as Triton performance.

## Benchmark-App Migration Snapshot

The queryable migration plan covers the 10 promoted benchmark apps:

| App | v2.5 state |
| --- | --- |
| RayDB-style grouped aggregates | first executable Triton preview for count/sum/min/max |
| Spatial RayJoin | native RT hot path already avoids CuPy/PyTorch partner continuation; compact preview available if post-processing enters timing |
| LibRTS-style AABB index query | native RT hot path already avoids CuPy/PyTorch partner continuation |
| Hausdorff/X-HD | grouped argmin and segmented max now have preview coverage; app wiring and CUDA evidence still pending |
| RT-DBSCAN | compact and bounded-finalize previews available; app wiring and CUDA evidence still pending |
| RTNN | grouped argmin and bounded-finalize previews available; app wiring and CUDA evidence still pending |
| Triangle counting | count and compact preview available; needs app wiring |
| Barnes-Hut | needs frontier rows lowered to generic Triton reductions while force math stays app-owned |
| Robot collision screening | compact and bounded-finalize previews available; app wiring and CUDA evidence still pending |
| Contact-manifold witness | bounded-finalize preview available; app wiring and CUDA evidence still pending |

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2663_v2_5_triton_segmented_sum_test \
  tests.goal2665_v2_5_triton_grouped_runner_test \
  tests.goal2669_v2_5_raydb_continuation_plan_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test \
  tests.goal2678_v2_5_triton_compact_mask_preview_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2680_v2_5_triton_bounded_collect_preview_test
```

These tests validate the planner status, descriptor metadata, fallback
semantics, pod-runner routing through the generic dispatcher, primitive
hierarchy wording, RayDB v2.5 app-facing metadata, and the 10-app migration
matrix.

## Remaining Work

- Integrate Triton count/sum into at least one full RayDB RT path after RT
  traversal emits group ids and values.
- Validate the bounded collect/finalize preview on a CUDA pod and wire it into
  bounded-row benchmark apps without making row order semantic.
- Port app continuations currently implemented with CuPy RawKernel to Triton
  equivalents or demote them to legacy/conformance paths.
- Run CUDA pod validation before any performance or release claim.
