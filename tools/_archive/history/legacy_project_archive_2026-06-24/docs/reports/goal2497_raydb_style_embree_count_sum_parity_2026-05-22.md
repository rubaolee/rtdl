# Goal2497: RayDB-Style Embree Count/Sum Parity

Date: 2026-05-22

## Status

Goal2497 implements the first backend parity path for the RayDB-style benchmark
slice.

The implementation covers Embree grouped `count` and `sum` only. CPU remains
the oracle for `min`, `max`, and `avg_as_sum_count`.

## Implementation

Added generic conversion helpers:

- `columnar_record_set_to_row_mappings`
- `columnar_plan_to_grouped_query`

These live in `src/rtdsl/columnar_aggregate_reference.py` and are exported from
`rtdsl.__init__`.

Updated the benchmark app:

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- CLI now accepts `--backend cpu_python_reference|embree`
- Embree `--mode all` runs only `count` and `sum`
- unsupported Embree modes fail closed

## Backend Boundary

Goal2497 does not add native code. It uses existing Embree columnar payload
symbols through the existing Python compatibility wrapper:

```text
ColumnarRecordSet + ColumnarAggregatePlan
-> row mappings for current compatibility wrapper
-> prepare_embree_db_dataset(..., transfer="columnar")
-> grouped_count / grouped_sum
-> compare with CPU oracle
```

This is not the final clean API shape. It is a parity bridge that proves the
generic columnar contract can reach existing Embree columnar execution without
adding a RayDB-specific native ABI.

## Claim Boundary

Goal2497 does not claim:

- RayDB reproduction;
- authors-code comparison;
- public performance;
- OptiX support;
- SQL engine behavior;
- DBMS behavior;
- row materialization support;
- new native database-specific ABI.

## Next Step

Goal2498 should add OptiX parity for the same `count` and `sum` contract when an
NVIDIA pod is available. It should preserve the same claim boundary and record
hardware, CUDA/OptiX versions, commands, and correctness artifacts.
