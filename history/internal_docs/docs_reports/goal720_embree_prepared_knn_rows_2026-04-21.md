# Goal720: Prepared Embree KNN Rows

Date: 2026-04-21

## Objective

Continue Embree app-performance optimization after Goal717/Goal718 by testing whether KNN-style spatial apps benefit from a reusable Embree BVH handle.

Target app family:

- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_ann_candidate_app.py`
- `examples/rtdl_facility_knn_assignment.py`

## Implementation

Added a native prepared 2-D KNN API:

- `rtdl_embree_knn_rows_2d_create`
- `rtdl_embree_knn_rows_2d_run`
- `rtdl_embree_knn_rows_2d_destroy`

Added Python API:

- `rtdsl.prepare_embree_knn_rows_2d(search_points)`
- `rtdsl.PreparedEmbreeKnnRows2D`

The prepared handle builds an Embree user-primitive point scene once, then runs repeated query batches against the same scene. It returns the existing `knn_rows` schema:

- `query_id`
- `neighbor_id`
- `distance`
- `neighbor_rank`

The implementation preserves existing KNN behavior:

- duplicate point-query callbacks are deduplicated by neighbor id;
- per-query rows are sorted by distance, then neighbor id;
- `neighbor_rank` is reassigned after sorting and truncation to `k`;
- output rows are stable-sorted by `query_id`.

## Correctness Evidence

Local macOS:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal717_embree_prepared_fixed_radius_summary_test \
  tests.goal718_embree_prepared_app_modes_test

Ran 6 tests in 0.014s
OK
```

Linux `lestat@192.168.1.20`, isolated checkout `/tmp/rtdl_goal720`:

```text
make build-embree
Embree 4.3.0

PYTHONPATH=src:. python3 -m unittest -v tests.goal720_embree_prepared_knn_rows_test

Ran 2 tests in 0.014s
OK
```

The focused parity test compares prepared KNN rows with one-shot Embree rows for the public facility KNN kernel and verifies repeated use with different `k` values.

## Performance Evidence

Harness:

- `scripts/goal720_embree_prepared_knn_perf.py`

Local macOS JSON:

- `docs/reports/goal720_embree_prepared_knn_perf_local_2026-04-21.json`

Linux JSON:

- `docs/reports/goal720_embree_prepared_knn_perf_linux_2026-04-21.json`

Linux median timing, 3 repeats:

| App | Copies | Query rows | Search rows | k | One-shot Embree | Prepared run-only | Speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hausdorff | 256 | 2048 | 1024/pass | 1 | 0.0329s | 0.0334s | 0.98x |
| ANN candidate | 256 | 768 | 768 | 1 | 0.0099s | 0.0100s | 1.00x |
| Facility KNN | 256 | 1024 | 1024 | 3 | 0.0217s | 0.0213s | 1.02x |
| Hausdorff | 1024 | 8192 | 4096/pass | 1 | 0.4500s | 0.4566s | 0.99x |
| ANN candidate | 1024 | 3072 | 3072 | 1 | 0.1295s | 0.1322s | 0.98x |
| Facility KNN | 1024 | 4096 | 4096 | 3 | 0.2776s | 0.2784s | 1.00x |
| Hausdorff | 4096 | 32768 | 16384/pass | 1 | 7.1141s | 7.1456s | 1.00x |
| ANN candidate | 4096 | 12288 | 12288 | 1 | 2.0292s | 2.0380s | 1.00x |
| Facility KNN | 4096 | 16384 | 16384 | 3 | 4.0907s | 4.1202s | 0.99x |

## Interpretation

Prepared KNN is correctness-useful but not a material performance win for the current public KNN apps on Linux. Scene construction is already a small fraction of total time for these workloads. The dominant cost is the query traversal and KNN candidate-maintenance path itself.

This differs from fixed-radius count-threshold summaries in Goal717/Goal718, where prepared handles and compact summary outputs avoid expensive repeated scene setup and row materialization. KNN still emits neighbor rows and still performs per-query ranking.

## Release Boundary

Do not claim that prepared KNN accelerates the current KNN apps. The honest claim is narrower:

- RTDL now has a reusable prepared Embree 2-D KNN primitive.
- Correctness matches one-shot Embree KNN rows.
- On the measured Mac/Linux fixtures, app-level prepared KNN is near parity rather than a speedup.
- Public app defaults should not be switched to prepared KNN yet.

## Next Optimization Direction

The next Embree optimization should target KNN traversal itself rather than scene reuse:

- reduce candidate bookkeeping overhead in the callback;
- investigate tighter initial query radius estimates for tiled or bounded datasets;
- add app-level summary outputs where apps only need max/min/primary neighbor results instead of full row materialization;
- keep prepared KNN for repeated-batch use cases where a long-lived search set receives many query batches.
