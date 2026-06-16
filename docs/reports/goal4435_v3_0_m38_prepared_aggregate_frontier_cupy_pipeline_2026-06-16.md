# Goal4435 / V3.0 M38 - Prepared Aggregate-Frontier CuPy Pipeline

## Result

M38 adds a prepared CuPy continuation for the M36 aggregate-frontier
device-column primitive. The goal is to remove avoidable hot-path setup from
the M37 one-shot partner: source columns, source lookup columns, target lookup
columns, and aggregate-node lookup columns are created once and kept resident
for repeated runs.

This is still the same V3 architecture boundary:

- RTDL engine primitive: generic `AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D`.
- Native producer: OptiX emits aggregate/exact frontier device columns.
- Partner continuation: app-owned CuPy inverse-square vector math consumes
  those columns.

## Public API

- `PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DCupy`
- `prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy`
- `AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT`

The M37 convenience function
`sum_aggregate_frontier_device_columns_weighted_vectors_2d_cupy` remains
available and now delegates through the prepared implementation.

## Hot-Path Contract

For repeated runs, callers prepare the partner once, then pass its resident
source columns into M36 by device pointer:

```python
prepared_vector = rt.prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
    points,
    points,
    tree["nodes"],
)
frontier = prepared_frontier.run_device_columns(
    row_capacity=row_capacity,
    **prepared_vector.frontier_source_device_args(),
)
vector_sum = prepared_vector.sum(frontier, softening=0.01)
```

The source columns are passed into M36 by device pointer, and the frontier rows
are not materialized on host. In short: frontier rows are not materialized on
host, and contribution rows are not materialized on host. The remaining
host-visible values are small scalar metadata such as row counts, overflow
status, and elapsed seconds.

- frontier rows are not materialized on host

## Claim Boundary

M38 is an implementation and architecture cleanup milestone, not a
whole-application speedup claim. The new metadata keeps the conservative flags:

- not a whole-application speedup claim
- `frontier_columns_materialized_on_host = False`
- `contribution_rows_materialized_on_host = False`
- `prepared_lookup_columns_resident = True`
- `setup_seconds_excluded_from_hot_path = True`
- `rt_core_speedup_claim_authorized = False`
- `whole_app_speedup_claim_authorized = False`
- `public_speedup_claim_authorized = False`
- `true_zero_copy_claim_authorized = False`

## Validation

Local tests:

```text
py -3 -m unittest discover -s tests -p "goal443*.py"
```

Pod tests:

```text
PYTHONPATH=src python -m unittest tests.goal4435_v3_0_m38_prepared_aggregate_frontier_cupy_pipeline_test -v
PYTHONPATH=src python -m unittest discover -s tests -p 'goal443*.py'
```

Both passed on the pod.

## 8192-Point Evidence

Evidence file:

- `docs/reports/goal4435_v3_0_m38_prepared_aggregate_frontier_cupy_pipeline_8192_2026-06-16.json`

Measured configuration:

- 8192 weighted points
- bucket size 64
- theta 0.5
- softening 0.01
- 341 tree nodes
- 3,440,003 frontier rows
- no overflow

Prepared setup costs, outside the repeated hot path:

- point generation and tree build: 0.089280 s
- OptiX frontier prepare: 0.287262 s
- CuPy partner prepare: 0.038401 s

Hot repeated medians:

- OptiX frontier traversal: 0.014188 s
- prepared CuPy partner vector sum: 0.008447 s
- native-plus-partner hot time: 0.022645 s
- Python wall time around both calls: 0.029041 s

Compared with M37's one-shot CuPy continuation on the same 8192-point
configuration, the partner median moved from 0.013083 s to 0.008447 s because
lookup/source/target/node columns are no longer rebuilt each hot call. That is a
partner hot-path cleanup result, not a whole-application speedup claim.
