# Goal2495: RayDB-Style CPU Reference Fixture

Date: 2026-05-22

## Status

Goal2495 implements the CPU-only RayDB-style benchmark slice proposed in
Goal2494.

This is a local correctness and contract step. It does not use Embree, OptiX,
authors code, SSB data, or a pod.

## Implementation

Added generic RTDL reference code:

- `src/rtdsl/columnar_aggregate_reference.py`
- exports in `src/rtdsl/__init__.py`

Added benchmark app:

- `examples/v2_0/research_benchmarks/raydb_style/`
- `rtdl_raydb_style_benchmark_app.py`
- `README.md`

The generic reference surface uses app-agnostic names:

- `ColumnarRecordSet`
- `ColumnarAggregatePlan`
- `ColumnarAggregateResult`
- `evaluate_columnar_grouped_aggregate`

The RayDB naming stays in the benchmark app and docs only.

## Fixture

The fixture is a tiny denormalized columnar dataset with:

- `row_ids`
- `region_id`
- `ship_year`
- `discount`
- `quantity`
- `revenue`

The default predicate set is:

```text
ship_year between 1994 and 1995
discount between 4 and 6
quantity < 25
```

Matching records are rows 1, 2, 6, and 8. The expected grouped outputs by
`region_id` are:

| Mode | Expected rows |
| --- | --- |
| `count` | `region 0 -> 2`, `region 1 -> 1`, `region 2 -> 1` |
| `sum` | `region 0 -> 190`, `region 1 -> 200`, `region 2 -> 80` |
| `min` | `region 0 -> 90`, `region 1 -> 200`, `region 2 -> 80` |
| `max` | `region 0 -> 100`, `region 1 -> 200`, `region 2 -> 80` |
| `avg_as_sum_count` | `region 0 -> sum 190/count 2`, `region 1 -> sum 200/count 1`, `region 2 -> sum 80/count 1` |

## Run

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python \
  examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --mode all
```

## Claim Boundary

Goal2495 validates only a CPU oracle for a generic columnar grouped aggregate
contract. It does not claim:

- RayDB reproduction;
- authors-code comparison;
- SSB correctness;
- Embree support;
- OptiX support;
- SQL engine or DBMS behavior;
- public performance wording;
- row materialization support;
- native database-specific ABI.

## Next Step

Goal2496 should choose the first backend lowering target. The recommended next
step is Embree or a generic CPU-RT prepared-axis proof, because it can validate
the same contract without needing an NVIDIA pod.
