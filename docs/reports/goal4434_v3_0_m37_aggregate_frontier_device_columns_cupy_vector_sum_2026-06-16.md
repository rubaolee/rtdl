# Goal4434 / V3.0 M37 Aggregate Frontier Device Columns CuPy Vector Sum

Date: 2026-06-16

## Result

M37 adds a CuPy partner continuation that consumes the M36
`AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` output and computes an aggregate-frontier
weighted inverse-square vector sum.

New function:

- `sum_aggregate_frontier_device_columns_weighted_vectors_2d_cupy`

New app-scoped contract:

- `generic_aggregate_frontier_device_columns_weighted_vector_sum_2d_v1`

## Boundary

This is a CuPy partner continuation, not a native RTDL engine primitive.

The frontier rows are not materialized on host. The continuation wraps the M36
device columns as CuPy arrays, computes contribution vectors on device, and
reduces by source id with CuPy.

The math is app-scoped inverse-square math. It remains outside the RTDL generic
engine boundary. RTDL provides the generic frontier producer; the partner owns
the Barnes-Hut-style force law and vector reduction.

## Claims

Authorized:

- implementation claim for the CuPy partner continuation;
- same-device consumption claim for M36 frontier columns;
- correctness claim only where compared against the existing fused reference.

Not authorized:

- RT-core speedup claim;
- whole-app speedup claim;
- public benchmark speedup claim;
- true zero-copy claim;
- paper reproduction claim.

The whole-app speedup claim remains unauthorized until we benchmark a full
prepared pipeline, including source-column residency, M36 frontier production,
this continuation, and any final materialization required by the app.

## Pod Evidence

Evidence file:
`docs/reports/goal4434_v3_0_m37_aggregate_frontier_device_columns_cupy_vector_sum_8192_2026-06-16.json`

Same M36/M34-style aggregate-frontier configuration:

- source points: 8,192
- bucket size: 64
- tree nodes: 341
- frontier rows: 3,440,003
- frontier overflow: false
- M36 frontier native traversal: 0.016584214 s
- CuPy partner continuation repeats: 0.165681690, 0.012954913,
  0.013083003 s
- CuPy partner continuation warm median: 0.013083003 s
- aggregate contribution rows: 479,913
- exact contribution rows: 2,960,090

The first continuation repeat includes CuPy allocation/kernel warmup effects.
The warm repeats show that the device-column frontier payload can be consumed by
partner app math without pulling the 3.44M frontier rows back to host.
