# Goal 759: RTX Cloud Benchmark Manifest Report

Status: implemented and locally verified.

## What Changed

Added a deterministic machine-readable manifest for the next paid NVIDIA RTX
cloud run:

- `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`

The manifest records exact commands, app path, scale, OptiX performance class,
benchmark readiness, allowed claim, non-claim, and preconditions for each
candidate path.

## Manifest Entries

Included for the next RTX cloud run:

- `database_analytics`: prepared DB session profiler for `sales_risk`.
- `database_analytics`: prepared DB session profiler for `regional_dashboard`.
- `outlier_detection`: prepared fixed-radius density threshold summary.
- `dbscan_clustering`: prepared fixed-radius core-flag summary.
- `robot_collision_screening`: prepared OptiX pose-flag summary.

Explicitly excluded:

- `hausdorff_distance`, `ann_candidate_search`, and `barnes_hut_force_app`
  because current paths are CUDA-through-OptiX or Python/app dominated, not
  RT-core traversal app claims.
- `graph_analytics` and segment/polygon OptiX app paths because current public
  paths are still host-indexed fallback for RTX app-claim purposes.
- Apple/HIPRT-specific apps because this manifest is for NVIDIA OptiX RTX cloud
  runs.

## Correction Found During Goal759

The manifest surfaced one stale source note in
`/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`: robot
collision still said native pose-level OptiX summaries were future ABI work.
That was stale after the prepared pose-flag path landed. The note now states
that OptiX has prepared scalar hit-count and prepared native pose-flag summary
modes, while edge witnesses still require row mode.

## Verification

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test

Ran 17 tests in 0.124s
OK
```

Manifest generation and JSON validation:

```text
PYTHONPATH=src:. python3 scripts/goal759_rtx_cloud_benchmark_manifest.py \
  --output-json docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json
python3 -m json.tool docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json
```

Static checks:

```text
python3 -m py_compile \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  tests/goal759_rtx_cloud_benchmark_manifest_test.py \
  src/rtdsl/app_support_matrix.py
git diff --check
```

All passed.

## Consensus

Plan review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal759_gemini_flash_plan_review_2026-04-22.md`
- Verdict: ACCEPT.

Finish review is requested after this report.
