# Goal4433 / V3.0 M36 Aggregate Frontier Device Columns OptiX Producer

Date: 2026-06-16

## Result

M36 promotes `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` from an M35 fail-closed
contract target to the first executable OptiX/CUDA producer:
`implemented_optix_device_columns`.

The new route emits the generic aggregate-frontier schema as device-resident
columns:

In short, M36 produces device-resident columns for frontier payload handoff.

- `source_id`
- `frontier_kind_code`
- `item_id`
- `owner_aggregate_id`
- `dfs_index`
- `resume_index`
- `metadata_flags`
- `row_offsets`

## Native ABI

Added native symbols:

- `rtdl_optix_prepare_aggregate_frontier_device_columns_2d`
- `rtdl_optix_run_aggregate_frontier_device_columns_2d`
- `rtdl_optix_destroy_aggregate_frontier_device_columns_2d`

The implementation prepares the generic tree rows and CSR arrays once, then runs
three CUDA kernels:

1. count frontier rows per source;
2. prefix those counts into device `row_offsets`;
3. write the seven frontier columns on device.

This path does not wrap the old host-row collector and does not build
`frontier_i64_rows` before partner continuation.

## Python Surface

Added:

- `prepare_aggregate_frontier_device_columns_2d_optix`
- `PreparedOptixAggregateFrontierDeviceColumns2D`
- `OptixAggregateFrontierDeviceColumns2DOutput`

The low-level `run_device_columns(...)` accepts existing CUDA device pointers
for source ids, x, and y. The convenience `run_cupy(...)` creates those source
columns with CuPy for tests and exploratory use; that convenience path is not a
true zero-copy claim.

Output device memory is valid until the prepared handle is run again or closed.
The prepared handle owns the most recent output.

## Claim Boundary

This milestone authorizes an implementation claim for the OptiX device-column
producer only.

The following claims remain unauthorized:

- public speedup claim;
- RT-core speedup claim;
- whole-app speedup claim;
- true zero-copy claim;
- paper-reproduction claim.

The speedup claim remains unauthorized until a partner continuation consumes
the device columns and an end-to-end hot-path benchmark is recorded.

The producer is still app-generic. It excludes force laws, scoring, app
reduction, solver logic, and automatic partner selection. A Barnes-Hut or other
aggregate app must consume these columns through a partner continuation.

## Pod Evidence

Evidence file:
`docs/reports/goal4433_v3_0_m36_aggregate_frontier_device_columns_optix_8192_2026-06-16.json`

Same M34-style aggregate-frontier configuration:

- source points: 8,192
- bucket size: 64
- tree nodes: 341
- frontier rows: 3,440,003
- row count matches M34 same-config row count: true
- overflow: false
- hot native traversal median: 0.014224568 s
- repeats: 0.014160577, 0.014192177, 0.014259675, 0.014262230,
  0.014224568 s

This measurement is intentionally not a whole-app speedup claim. It measures the
new device-column producer and shows that the specific M34 debt, host
frontier-row materialization before partner continuation, is removed for this
OptiX route.

## Why It Matters

M34 showed that the old aggregate-frontier path was dominated by host
materialization of millions of frontier rows. M36 removes that specific
materialization boundary for the OptiX side: the frontier payload can now stay
on device for a same-stream or event-ordered partner continuation.

This is the right V3 direction: RTDL owns generic primitive production, while
the app or partner owns the app-specific math.
