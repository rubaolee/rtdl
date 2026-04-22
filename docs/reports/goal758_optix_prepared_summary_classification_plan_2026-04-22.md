# Goal 758: OptiX Prepared Summary Classification Plan

Status: plan for consistency update after Goals 756 and 757.

## Problem

Goal 757 added prepared OptiX fixed-radius count-threshold traversal for two app
summary paths:

- `examples/rtdl_outlier_detection_app.py --backend optix --optix-summary-mode rt_count_threshold_prepared`
- `examples/rtdl_dbscan_clustering_app.py --backend optix --optix-summary-mode rt_core_flags_prepared`

The public and machine-readable OptiX app performance matrix still classifies
both apps as only `cuda_through_optix`. That was correct for the default
fixed-radius neighbor-row path, but it is now incomplete: these apps have an
explicit prepared summary path that uses OptiX traversal and avoids neighbor-row
materialization.

## Boundary

Do not promote the entire outlier or DBSCAN app to a broad RTX app speedup
claim.

- The default row path remains CUDA-style fixed-radius rows through the OptiX
  backend library.
- The prepared summary path is traversal-backed, but only for thresholded
  density summaries / DBSCAN core flags.
- DBSCAN clustering expansion remains Python-owned.
- Existing Linux evidence is from GTX 1070, which has no RT cores; it is
  backend behavior/performance evidence, not RTX RT-core speedup evidence.

## Proposed Change

1. Add a new OptiX app performance class:
   `optix_traversal_prepared_summary`.
2. Change `outlier_detection` and `dbscan_clustering` machine-readable
   classifications to this new class.
3. Update notes to explicitly state the default row path is still
   CUDA-through-OptiX while the explicit prepared summary path is traversal
   backed.
4. Update `docs/app_engine_support_matrix.md` so public readers see the same
   boundary.
5. Update tests so this nuance is enforced and cannot silently regress.

## Verification Plan

- Focused matrix tests:
  - `tests.goal690_optix_performance_classification_test`
  - `tests.goal687_app_engine_support_matrix_test`
  - `tests.goal757_prepared_optix_fixed_radius_count_test`
- Public doc smoke tests if affected:
  - `tests.goal497_public_entry_smoke_check_test`
  - `tests.goal515_public_command_truth_audit_test`
- `python3 -m py_compile` for the edited source/tests.
- `git diff --check`.

## Consensus Request

Reviewer should confirm whether the new class is the correct honesty-preserving
classification, or whether keeping app-level `cuda_through_optix` plus a note is
preferable. The implementation must not claim whole-app DBSCAN/outlier RTX
speedup before RTX-class phase-clean evidence exists.
