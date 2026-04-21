# Goal721: Embree KNN Bookkeeping Optimization

Date: 2026-04-21

## Objective

Continue Embree optimization after Goal720 showed that prepared KNN scene reuse is correct but not the main performance lever for current KNN apps.

The new hypothesis was that the KNN callback itself was paying excessive per-query overhead. The old path allocated and maintained an `std::unordered_set<uint32_t>` for every KNN query to deduplicate Embree point-query callbacks. That is disproportionate for common RTDL app cases where `k` is small (`k=1` for Hausdorff/ANN, `k=3` for facility assignment).

## Implementation

Changed only the native Embree KNN bookkeeping path:

- Removed `seen_neighbor_ids` from `KnnRowsQueryState` and `KnnRowsQueryState3D`.
- Replaced per-query `std::unordered_set` allocation with a tiny active-row duplicate check:
  `knn_rows_have_neighbor(...)`.
- Kept duplicate safety for active KNN rows.
- Kept radius tightening after the first full candidate set is available.
- Kept row sorting and rank assignment unchanged.

This affects:

- one-shot 2-D `knn_rows`;
- prepared 2-D `knn_rows`;
- one-shot 3-D `knn_rows`.

It intentionally does not change fixed-radius neighbor paths, where the result set can be larger and an unordered set remains appropriate.

## Correctness Evidence

Local macOS focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal710_embree_parallel_point_query_test \
  tests.goal293_v0_5_native_3d_bounded_knn_oracle_test

Ran 8 tests in 0.027s
OK
```

Linux `lestat@192.168.1.20`, isolated checkout `/tmp/rtdl_goal721`:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal710_embree_parallel_point_query_test

Ran 6 tests in 0.009s
OK
```

The focused tests cover:

- prepared 2-D KNN parity with one-shot Embree;
- 2-D KNN thread-count stability;
- 3-D KNN thread-count stability;
- 3-D native oracle parity on macOS.

## Linux Performance

New perf file:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal721_embree_knn_bookkeeping_perf_linux_2026-04-21.json`

Previous baseline:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal720_embree_prepared_knn_perf_linux_2026-04-21.json`

Median timing, 3 repeats, Linux:

| App | Copies | Old one-shot | New one-shot | One-shot speedup | Old prepared run | New prepared run | Prepared speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hausdorff | 1024 | 0.4500s | 0.3253s | 1.38x | 0.4566s | 0.3309s | 1.38x |
| ANN candidate | 1024 | 0.1295s | 0.0942s | 1.37x | 0.1322s | 0.0963s | 1.37x |
| Facility KNN | 1024 | 0.2776s | 0.2176s | 1.28x | 0.2784s | 0.2232s | 1.25x |
| Hausdorff | 4096 | 7.1141s | 5.1011s | 1.39x | 7.1456s | 5.1604s | 1.38x |
| ANN candidate | 4096 | 2.0292s | 1.4666s | 1.38x | 2.0380s | 1.4649s | 1.39x |
| Facility KNN | 4096 | 4.0907s | 3.1933s | 1.28x | 4.1202s | 3.2114s | 1.28x |

## Interpretation

This is a real Embree KNN optimization. The performance improvement comes from reducing per-query CPU bookkeeping overhead in the native KNN callback, not from changing the RTDL app layer or the Python interface.

The result also clarifies Goal720:

- prepared KNN scene reuse remains useful as an API primitive;
- prepared-vs-one-shot is still near parity for current app shapes;
- the meaningful win was inside the traversal callback path shared by both one-shot and prepared KNN.

## Release Boundary

Allowed claim:

- Embree KNN rows are faster for the measured Hausdorff, ANN candidate, and facility KNN app kernels after removing per-query hash-set bookkeeping.
- Linux large-case speedups are about `1.28x-1.39x` versus the immediate Goal720 baseline.

Not allowed:

- Do not claim a universal KNN speedup across all distributions, all `k`, or all app-level JSON/CLI flows.
- Do not claim prepared KNN alone accelerates these apps.
- Do not apply this bookkeeping replacement to fixed-radius neighbor paths without separate correctness/performance evidence.
