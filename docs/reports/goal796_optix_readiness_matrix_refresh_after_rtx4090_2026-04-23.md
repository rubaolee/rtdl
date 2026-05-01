# Goal796 OptiX Readiness Matrix Refresh After RTX 4090 Evidence

Date: 2026-04-23

## Verdict

Status: `updated`.

Goal795 preserved RTX 4090 evidence makes three prepared scalar sub-paths eligible for claim-review discussion. The matrix now reflects that without turning them into broad whole-app speedup claims.

## Changed Source Of Truth

- Code: `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- Public doc: `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- Test: `/Users/rl2025/rtdl_python_only/tests/goal705_optix_app_benchmark_readiness_test.py`

## New Readiness Position

| App | Previous readiness | New readiness | Allowed claim boundary |
|---|---|---|---|
| `outlier_detection` | `needs_phase_contract` | `ready_for_rtx_claim_review` | Prepared fixed-radius scalar threshold-count sub-path only. |
| `dbscan_clustering` | `needs_postprocess_split` | `ready_for_rtx_claim_review` | Prepared fixed-radius core-threshold summary only; no full DBSCAN clustering claim. |
| `robot_collision_screening` | `needs_phase_contract` | `ready_for_rtx_claim_review` | Prepared ray/triangle any-hit scalar pose-count sub-path only; no full robot-planning claim. |

## Unchanged Boundaries

- Database analytics remains `needs_interface_tuning`.
- Graph analytics remains `needs_native_kernel_tuning`.
- Segment/polygon OptiX-facing app paths remain `needs_native_kernel_tuning`.
- Hausdorff, ANN, and Barnes-Hut remain excluded from RTX RT-core app claims because the current public OptiX paths are CUDA-through-OptiX/GPU-compute style, not dominant RT-core traversal claims.

## Rationale

The preserved RTX 4090 run has phase-clean evidence for prepared scalar native outputs. That is materially stronger than the earlier GTX 1070 or pending-A5000 language, so the old matrix was stale. The refresh deliberately uses `ready_for_rtx_claim_review`, not a release or public-speedup status.
