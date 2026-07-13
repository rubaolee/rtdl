# Goal5141 - Generic Cell-MBR Backend Feasibility Spike

## Verdict

`feasible_optix_backend_spike_next__requires_new_generic_native_symbol`

## Why This Goal Exists

Goals5138-5140 moved the X-HD work from an app-specific exact reference route
toward a generic RTDL system route:

```text
point columns
-> grid cell descriptors
-> radius-expanded cell-MBR candidates
-> nearest-state inline/offload/pruned frontiers
-> native ABI row table
```

Goal5140 deliberately stopped at an ABI. Goal5141 audits existing RTDL native
and Python assets to decide whether the next step can be an implementation
spike, and whether that spike would be generic or an X-HD-specific shortcut.

## Executive Conclusion

An OptiX backend is feasible, but it is **not already present**.

RTDL already has enough generic native building blocks to make the backend a
reasonable next goal:

- custom AABB GAS construction from device AABB buffers;
- generic 2-D AABB OptiX point-membership and range-intersection row output;
- 3-D fixed-radius OptiX/CUDA query kernels;
- native nearest-witness device-column handoff patterns.

Those assets are reusable patterns, not the Goal5140 backend. No current symbol
emits:

```text
frontier_kind_code, query_row_id, query_point_id, cell_id,
point_begin_offset, point_count, min_distance, max_distance
```

with Goal5140's `inline/offload/pruned` classification.

## Assets Audited

### 1. Generic 2-D AABB OptiX Index

Files:

```text
src/rtdsl/aabb_index.py
src/rtdsl/optix_runtime.py
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_workloads.cpp
```

Relevant symbols:

```text
prepare_aabb_index_2d
expanded_aabb_point_membership_rows_2d
collect_aabb_point_membership_pair_rows_2d_optix
rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows
```

Finding:

This is the strongest implementation precedent. It is app-neutral, uses OptiX
custom AABBs, emits row output, and already has fail-closed capacity semantics.
But it is 2-D point/box membership, not nearest-state frontier classification.
It can guide Goal5142, not replace it.

### 2. Custom AABB GAS Builders

Files:

```text
src/native/optix/rtdl_optix_core.cpp
```

Relevant symbols:

```text
build_custom_accel_from_device_aabbs
build_custom_accel_from_borrowed_device_aabbs
```

Finding:

These are direct building blocks. Cell MBRs can be represented as generic custom
AABBs. This supports an app-neutral cell-MBR traversal backend without copying
author X-HD code into RTDL.

### 3. 3-D Fixed-Radius RT/Grid Kernels

Files:

```text
src/native/optix/rtdl_optix_core.cpp
src/native/optix/rtdl_optix_workloads.cpp
```

Relevant symbols:

```text
__raygen__frn3d_probe
fixed_radius_neighbors_3d_grid
fixed_radius_neighbors_3d_grid_exact_rows
```

Finding:

These prove that the native layer already has 3-D query launch, fixed-radius
search, CUDA module loading, and output-row patterns. They do not operate on
cell MBRs and do not emit Goal5140 frontier rows.

### 4. 2-D Point-Group Nearest-Witness Device Columns

Files:

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_workloads.cpp
```

Relevant symbols:

```text
rtdl_optix_prepare_point_group_nearest_witness_2d
rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns
```

Finding:

This is useful as a device-column handoff and prepared-run pattern. It is not a
cell-MBR frontier backend and is limited to the point-group nearest-witness
shape.

## What Is Missing

The missing system surface is one generic native symbol family, starting with
OptiX:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier
```

It should consume generic cell MBR columns, query point columns, current
nearest-state columns, and `max_inline_points`, then emit the Goal5140 row
schema with fail-closed overflow behavior.

Embree and HIPRT should stay out of scope until the OptiX spike proves the ABI.

## Recommended Goal5142

Goal5142 should be:

```text
Generic OptiX cell-MBR frontier backend spike
```

Minimum implementation scope:

1. Add one generic OptiX native symbol that follows Goal5140's ABI.
2. Use custom AABB acceleration over caller-owned cell MBRs.
3. Emit ABI-shaped row columns with `inline/offload/pruned` kind codes.
4. Fail closed on row-capacity overflow.
5. Validate on a tiny synthetic non-X-HD fixture against
   `cell_mbr_frontiers_to_row_table_numpy_columns`.

Not authorized:

- full X-HD paper reproduction;
- author performance parity;
- X-HD-specific native primitive names;
- copying author code into RTDL core;
- Embree/HIPRT implementation before the OptiX ABI is proven.

## Risks

### R1. 3-D Backend Gap

The most mature AABB row-output path is 2-D, while X-HD graphics samples are
3-D. The spike should therefore be explicit about dimensionality and should
include a 3-D synthetic fixture if it targets the X-HD route.

### R2. Overflow Semantics

Frontier rows are capacity-sensitive. The backend must follow existing AABB row
discipline: overflow is a failure, not a partial-success result.

### R3. App Identity Creep

The backend must use only cell-MBR/frontier/nearest-state terminology. No
`xhd`, `hausdorff`, `paper`, or author-algorithm names belong in the native
contract.

### R4. Performance Overclaim

A tiny native backend smoke proves ABI correctness, not paper performance. Any
timing result must be treated as diagnostic until a separate phase-aligned
performance goal is authorized.

## Validation

This goal is a source audit and planning gate, not a code backend. Validation
performed:

```text
rg over src/rtdsl/aabb_index.py and src/rtdsl/optix_runtime.py
rg over src/native/optix/rtdl_optix_core.cpp
rg over src/native/optix/rtdl_optix_prelude.h
rg over src/native/optix/rtdl_optix_workloads.cpp
rg over Goal5140 tests/docs/manifest entries
```

Machine-readable result:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5141_generic_cell_mbr_backend_feasibility_2026-07-08.json
```

## Claim Boundary

Allowed:

- Existing generic native assets make an OptiX implementation plausible.
- A new generic native symbol is required.
- Goal5142 may implement a bounded correctness spike.

Not allowed:

- RTDL already has the Goal5140 backend.
- X-HD RT algorithm is reproduced.
- X-HD performance improved.
- Existing 2-D AABB point-membership rows are equivalent to Goal5140 frontier
  rows.
