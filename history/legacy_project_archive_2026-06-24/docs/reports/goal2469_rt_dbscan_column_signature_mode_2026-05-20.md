# Goal2469 - RT-DBSCAN grouped-stream column-signature mode

Date: 2026-05-20

Status: local benchmark-app optimization plus pod evidence. This adds a
no-row benchmark mode; the row-vs-column pod timing is recorded in
`docs/reports/goal2469_grouped_stream_column_signature_pod_2026-05-20.md`.

## Purpose

Goal2468 pod evidence showed that the current grouped-stream benchmark gap is
mostly Python row handling:

- `rows_materialization_sec`;
- `densify_cluster_labels_sec`;
- benchmark `signature_sec`.

The existing mode, `optix_rt_core_grouped_stream_cupy_components_3d`, remains
the row-returning compatibility path. Goal2469 adds a separate mode:

```text
optix_rt_core_grouped_stream_cupy_column_signature_3d
```

This mode runs the same prepared grouped-stream OptiX/CuPy computation but
computes the benchmark signature directly from partner column arrays instead
of converting every point to a Python dictionary row and then densifying those
rows.

## Scope

Added behavior:

- signature helper over host arrays copied from partner columns;
- explicit no-row mode in the benchmark app;
- timing field `column_signature_sec`;
- metadata `materializes_python_rows = false`;
- metadata `signature_source = partner_column_arrays_no_python_row_dicts`;
- fail-fast behavior if `--include-rows` is requested for the no-row mode.
- runner switch `--signature-mode row|column`, so future pod comparisons use
  the same prepared-handle repeat protocol as Goal2468.

Preserved behavior:

- existing grouped-stream component-row mode is unchanged;
- native grouped RT ABI is unchanged;
- labels and core flags still come from the same generic prepared grouped
  stream path;
- paper and broad speedup claim flags remain false.

## Boundary

This does not add a native ABI, does not change clustering semantics, and does
not authorize a performance claim. It is a benchmark-app path that avoids
unnecessary Python row objects when the caller only needs a signature.

## Local Verification

Passed local focused RT-DBSCAN regression gate:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2469_rt_dbscan_column_signature_mode_test \
  tests.goal2468_rt_dbscan_overhead_breakdown_instrumentation_test \
  tests.goal2467_blocked_grouped_continuation_design_test \
  tests.goal2465_grouped_union_all_items_intersection_cull_test \
  tests.goal2463_grouped_union_all_items_path_test \
  tests.goal2461_grouped_stream_self_query_device_path_test \
  tests.goal2459_grouped_stream_threshold_capped_core_flags_test \
  tests.goal2457_generic_grouped_stream_continuation_implementation_test
```

Result: 35 tests passed.

Passed syntax and whitespace gates:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m py_compile \
  examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  tests/goal2469_rt_dbscan_column_signature_mode_test.py

git diff --check
```

Broad `unittest discover` is not used as the acceptance gate for this slice:
the current repository-wide baseline still contains many historical
documentation, artifact-manifest, and missing legacy-file failures unrelated
to the RT-DBSCAN grouped-stream benchmark path.

## Pod Result

The pod run compared:

```text
python3 scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --output-dir docs/reports/goal2469_grouped_stream_row_signature_pod \
  --point-count 32768 \
  --point-count 65536 \
  --repeat-count 5 \
  --signature-mode row

python3 scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --output-dir docs/reports/goal2469_grouped_stream_column_signature_pod \
  --point-count 32768 \
  --point-count 65536 \
  --repeat-count 5 \
  --signature-mode column
```

on the same `clustered3d` 32,768 and 65,536 point rows. The observed win is not
from faster RT traversal; it comes from removing row materialization and label
densification from the benchmark-app path. See
`docs/reports/goal2469_grouped_stream_column_signature_pod_2026-05-20.md` for
raw artifact paths, environment, exact medians, and claim boundary.
