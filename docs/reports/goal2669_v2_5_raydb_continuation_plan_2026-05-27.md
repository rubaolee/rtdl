# Goal2669: v2.5 RayDB Partner-Continuation Plan

Status: descriptor-only benchmark integration plan, local-test backed.

Date: 2026-05-27

## Purpose

v2.5 has generic Triton/Numba preview continuations for grouped count and sum.
RayDB is the first benchmark row where those continuations naturally apply:
after RT traversal finds matching primitives, the app needs grouped count,
grouped sum, or composite average as sum plus count.

This goal adds a descriptor-only RayDB integration plan. It does not execute
Triton or Numba and does not change benchmark performance claims.

## Implemented Surface

Updated app:

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`

New function:

- `describe_raydb_v2_5_partner_continuation(mode)`

New test:

- `tests/goal2669_v2_5_raydb_continuation_plan_test.py`

## Mapping

| RayDB mode | v2.5 continuation plan |
| --- | --- |
| `count` | `segmented_count_i64` |
| `sum` | `segmented_sum_f64` |
| `avg_as_sum_count` | `segmented_sum_f64` + `segmented_count_i64` |
| `min` | `segmented_min_f64` reference/descriptor contract |
| `max` | `segmented_max_f64` reference/descriptor contract |

The plan records Triton as preferred and Numba as fallback, matching the
Goal2662 contract. Count/sum have preview partner kernels. Min/max are
reference/descriptor-only until partner kernels exist.

## Boundary

This is descriptor-only and preview-only:

- no public speedup claim;
- no benchmark promotion;
- no RT traversal replacement;
- no CuPy RawKernel requirement;
- no RayDB-specific native engine logic.

RayDB predicate encoding and result interpretation remain app code. The v2.5
continuation sees only group ids and numeric values.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2669_v2_5_raydb_continuation_plan_test
```

The test checks that count/sum/min/max/avg map to generic v2.5 operations and
that no promoted performance wording is introduced.

## Next Pod Work

On a CUDA pod, first run the Goal2665 continuation runner. After that, integrate
the Triton continuation into one RayDB prepared path and compare:

- OptiX traversal plus Triton continuation;
- OptiX traversal plus existing native/grouped reduction continuation;
- Embree same-contract baseline;
- correctness against PostgreSQL or the existing RayDB CPU oracle.
