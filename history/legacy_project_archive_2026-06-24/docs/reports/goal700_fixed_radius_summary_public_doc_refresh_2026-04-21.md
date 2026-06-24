# Goal700 Fixed-Radius Summary Public Doc Refresh

Date: 2026-04-21

Verdict: ACCEPT as a documentation and public-surface consistency update.

## Scope

Goal700 updates the public documentation around the optional OptiX fixed-radius
summary modes added in Goals695-699.

Files updated:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/application_catalog.md`
- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- `/Users/rl2025/rtdl_python_only/tests/goal700_fixed_radius_summary_public_doc_test.py`

## Public User Message

The outlier and DBSCAN apps now document optional OptiX summary modes:

- `--optix-summary-mode rt_count_threshold` for outlier density-threshold
  summaries;
- `--optix-summary-mode rt_core_flags` for DBSCAN core flags.

These modes avoid full neighbor-row materialization for the bounded summary
outputs.

## Honesty Boundary

The public OptiX performance class remains `cuda_through_optix` for both apps.

This goal does not claim:

- KNN acceleration;
- Hausdorff acceleration;
- ANN acceleration;
- Barnes-Hut acceleration;
- full DBSCAN cluster-expansion acceleration;
- RTX speedup before RTX-class evidence exists.

The docs explicitly say that RTX-class measurements are still pending and that
the DBSCAN summary mode emits core flags only.

## Verification

Focused verification:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal686_app_catalog_cleanup_test

PYTHONPATH=src:. python3 -m py_compile \
  tests/goal700_fixed_radius_summary_public_doc_test.py

git diff --check
```

Result: `16` tests OK, `py_compile` OK, `git diff --check` OK.

## Release Meaning

Goal700 keeps the user-facing docs synchronized with the current post-v0.9.6
mainline fixed-radius summary work while preserving the release honesty
boundary. It prepares users and reviewers to understand the optional summary
modes before cloud RTX performance data exists.
