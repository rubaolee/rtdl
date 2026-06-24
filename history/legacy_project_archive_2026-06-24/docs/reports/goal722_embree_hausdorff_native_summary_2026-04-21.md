# Goal722: Embree Native Directed-Hausdorff Summary

Date: 2026-04-21

## Objective

Continue Embree app optimization after Goal721. Hausdorff distance was the next suitable target because the public app used Embree to emit all `k=1` nearest-neighbor rows and then used Python/`reduce_rows(max)` to compute the directed Hausdorff distance. The app does not need all nearest-neighbor rows when it only wants the final directed max distance and witness.

## Implementation

Added a native Embree summary API:

- `rtdl_embree_run_directed_hausdorff_2d`
- Python helper: `rtdsl.directed_hausdorff_2d_embree(query_points, search_points)`

Updated the app:

- `examples/rtdl_hausdorff_distance_app.py`
- New Embree-only option: `--embree-result-mode rows|directed_summary`
- Default remains `rows` to preserve the original RTDL nearest-row demo.

The first version reused the generic KNN callback and was near parity. The final version adds a dedicated nearest-only point-query state:

- `QueryKind::kNearestPoint`
- `NearestPointQueryState`

This avoids per-query KNN row-vector materialization inside the directed-summary path. It tracks only:

- current best neighbor id;
- current best distance;
- whether a hit exists.

## Correctness Evidence

Local macOS:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal722_embree_hausdorff_summary_test \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal710_embree_parallel_point_query_test

Ran 9 tests in 0.005s
OK
```

Linux `lestat@192.168.1.20`, isolated checkout `/tmp/rtdl_goal722`:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal722_embree_hausdorff_summary_test \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal710_embree_parallel_point_query_test

Ran 9 tests in 0.015s
OK
```

The tests verify:

- native symbol/source exposure;
- directed-summary mode matches row mode;
- directed-summary mode matches the brute-force oracle;
- empty point sets reject cleanly;
- existing KNN and threaded point-query tests still pass.

## Performance Evidence

Harness:

- `/Users/rl2025/rtdl_python_only/scripts/goal722_embree_hausdorff_summary_perf.py`

Mac JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal722_embree_hausdorff_summary_perf_local_2026-04-21.json`

Linux JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal722_embree_hausdorff_summary_perf_linux_2026-04-21.json`

The harness measures the Embree app computation phase only. It excludes the brute-force oracle because the oracle is not part of the Embree optimized path and would mask backend differences.

Linux median timing, 3 repeats:

| Copies | Points A | Points B | Row mode | Directed summary | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1024 | 4096 | 4096 | 0.3576s | 0.2558s | 1.40x |
| 4096 | 16384 | 16384 | 5.4058s | 3.8619s | 1.40x |

Mac median timing, 3 repeats:

| Copies | Points A | Points B | Row mode | Directed summary | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 1024 | 1024 | 0.0129s | 0.0104s | 1.24x |
| 1024 | 4096 | 4096 | 0.1349s | 0.1118s | 1.21x |
| 4096 | 16384 | 16384 | 1.7520s | 1.4165s | 1.24x |

## Interpretation

This is a real app-level Embree optimization for Hausdorff when the user wants the distance/witness summary rather than all nearest-neighbor rows.

The performance win comes from reducing dataflow and native bookkeeping:

- no full nearest-neighbor row emission for each point;
- no Python row reduction over all nearest rows;
- no per-query native KNN row vector in the summary callback.

The original row mode remains useful when the user wants inspectable nearest-neighbor rows.

## Release Boundary

Allowed claim:

- Hausdorff has an Embree native directed-summary mode.
- On measured Mac/Linux cases, the directed-summary mode is faster than the row/reduce path.
- Linux app-computation speedup is about `1.40x` at 4096 and 16384 points per set.

Not allowed:

- Do not claim this changes ANN or facility KNN performance.
- Do not claim a broad KNN speedup from the Hausdorff summary API.
- Do not compare this timing to full app CLI timing unless oracle/JSON phases are measured and disclosed separately.
