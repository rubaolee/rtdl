# Goal2681: v2.5 Triton Partner Adapter Front Door

Status: local implementation slice; CUDA pod validation still required.

Date: 2026-05-27

## Purpose

The earlier v2.5 slices added generic Triton continuation kernels, but most
public partner-adapter entry points still exposed only `partner="torch"` or
`partner="cupy"`. This goal adds an explicit `partner="triton"` front door for
generic adapter operations so benchmark apps can migrate away from legacy
CuPy/PyTorch continuations without calling low-level Triton helpers directly.

## Scope

The new front door covers generic continuation-shaped operations only:

- segmented count by key;
- segmented sum/min/max by key over `float64` values;
- mask compaction to selected row indices;
- column compaction and paging;
- generic metric-table reductions;
- generic columnar predicate count/sum/ids reductions.

Torch CUDA tensors are still used as the launch carrier for Triton kernels.
That carrier role is explicit and does not make PyTorch the v2.5 partner.

## Boundary

This goal does not make every old partner adapter a Triton adapter. App-math
adapters such as exact Hausdorff distance, top-k nearest point distance, DBSCAN
component labeling, and other dense domain computations remain outside the
Triton front door until they are decomposed into reviewed generic RTDL
operations.

The native engine remains app-agnostic. The new adapter routes generic
post-RT continuations through `run_triton_partner_continuation()`; it does not
move app/domain logic into Embree, OptiX, or RTDL native code.

## Implementation

`src/rtdsl/partner_adapters.py` now accepts `partner="triton"` for the generic
front doors above. The implementation routes:

- `partner_group_count_by_key()` to `segmented_count_i64`;
- `partner_group_sum_by_key()` to `segmented_sum_f64`;
- `partner_group_min_by_key()` to `segmented_min_f64`;
- `partner_group_max_by_key()` to `segmented_max_f64`;
- `partner_mask_indices()` to `compact_mask_i64`;
- columnar predicate counts through mask compaction plus segmented count;
- columnar predicate sums through `float64` masked values plus segmented sum.

`float64` is required for Triton f64 reductions. Integer counting uses
`segmented_count_i64`, not a fake integer sum through the f64 path.

`src/rtdsl/v2_5_triton_app_migration.py` now also exposes
`v2_5_triton_front_door_coverage()`. It separates operations with a generic
adapter front door from operations that currently have only a low-level Triton
dispatcher preview:

- adapter-front-door operations: `segmented_count_i64`, `segmented_sum_f64`,
  `segmented_min_f64`, `segmented_max_f64`, `compact_mask_i64`;
- dispatcher-only preview operations: `grouped_argmin_f64`,
  `bounded_collect_finalize_i64`.

This means RayDB, Spatial RayJoin, LibRTS-style AABB queries, and triangle
counting have all currently required continuation operations covered by the
generic adapter front door. Hausdorff/X-HD, RT-DBSCAN, RTNN, Barnes-Hut, robot
collision, and contact-manifold still need app wiring around dispatcher-only
operations before they can honestly claim a full `partner="triton"` app path.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
```

Expected locally on this Mac:

```text
Ran 8 tests
OK (skipped=3)
```

The skipped executable tests require Triton plus Torch CUDA on a Linux NVIDIA
pod. The non-CUDA tests verify source routing, public exports, and explicit
failure when the Triton front door is used without a CUDA carrier.

## Claim Boundary

This is app wiring for generic post-RT continuation only. It does not complete
v2.5, does not authorize public performance claims, and does not replace RTDL
RT traversal. Promotion still requires pod correctness/timing evidence and
benchmark-app integration.

## Goal2861 Refresh

Goal2861 completes the generic front-door coverage for the promoted v2.5
benchmark operation set by adding explicit partner-column adapters for grouped
argmin, grouped argmax, grouped top-k, and bounded collect/finalize. The
coverage report now shows 10 of 10 promoted benchmark apps as
adapter-front-door-ready, with zero dispatcher-only operations for that app
set. This refresh does not change the claim boundary above: it is API coverage
and executable wrapper evidence, not a public speedup or release claim.
