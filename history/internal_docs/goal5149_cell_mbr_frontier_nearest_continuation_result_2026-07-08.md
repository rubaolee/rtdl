# Goal5149 - Cell-MBR Frontier Nearest Continuation Result

## Verdict

`completed_generic_cell_mbr_frontier_nearest_continuation`

## What Changed

Goal5149 adds a generic continuation helper:

```text
nearest_witness_from_cell_mbr_frontier_numpy_columns
```

The helper consumes:

- source/query point columns,
- target point columns,
- generic grid cell columns,
- a Goal5140/5148-style cell-MBR frontier row table.

It returns nearest-witness columns:

```text
source_ids
nearest_item_ids
nearest_distances
```

The helper is intentionally app-neutral. It has no X-HD, Hausdorff, paper, or
author identity in its public contract. It is the continuation needed after a
cell-MBR frontier producer: scan the point spans referenced by inline/offload
frontier rows, skip pruned rows, and produce nearest witness state per query.

## Why This Matters

Goal5148 moved cell-MBR distance filtering and frontier kind classification into
a native OptiX 3-D row producer. That row producer alone is not an X-HD route:
it only says which cell rows remain candidates. Goal5149 adds the generic
downstream continuation that turns those frontier rows into nearest witnesses.

This is still not an author X-HD fused RT-core implementation. It is a generic
partner continuation over a generic row table.

## Verification

Local tests:

```text
py -m unittest tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5145_dimension_generic_cell_mbr_frontdoor_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test

Ran 12 tests OK
```

POD regression as part of Goal5150:

```text
python3 -m unittest \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 5 tests OK
```

## Genericity Evidence

The new tests include a non-Hausdorff facility/service-radius consumer. It uses
the same frontier-nearest continuation to compute worst-served demand over
facility cells. This keeps the API on the system side rather than as an X-HD
special case.

## Claim Boundary

This goal does not claim:

- full X-HD paper reproduction;
- author algorithm equivalence;
- RT-core performance;
- native fused continuation;
- exact paper dataset reproduction.

It only proves that RTDL now has a generic continuation from cell-MBR frontier
rows to nearest-witness columns.
