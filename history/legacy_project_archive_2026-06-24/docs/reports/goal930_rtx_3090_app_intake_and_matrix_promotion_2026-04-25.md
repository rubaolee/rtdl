# Goal930 RTX 3090 App Intake And Matrix Promotion

Date: 2026-04-25

## Verdict

Status: local matrix updated from Goal929 evidence; no public speedup claim authorized.

Goal929 captured RTX 3090 artifacts for the current OOM-safe app groups. Goal930 applies a conservative app-by-app intake to the machine-readable support matrix and public matrix doc.

## Promotion Rules

An app or bounded sub-path may move to `ready_for_rtx_claim_review` / `rt_core_ready` only when the RTX artifact has:

- runner `ok`;
- analyzer `ok`;
- cloud contract `ok`;
- baseline-review contract `ok`;
- correctness/parity evidence appropriate to the artifact;
- a narrow allowed-claim string that excludes whole-app speedup overreach.

If correctness passed but the native path is slower, too small, or lacks scalable timing, the app is not promoted to claim-review readiness. It moves to a tuning hold instead.

## Intake Table

| App | Goal929 evidence | Decision | Reason |
|---|---|---|---|
| `robot_collision_screening` | Group A analyzer `ok` | keep `ready_for_rtx_claim_review` / `rt_core_ready` | Prepared ray/triangle any-hit scalar pose-count path already claim-review ready; Goal929 adds RTX 3090 regression evidence. |
| `outlier_detection` | Group B analyzer `ok` | keep `ready_for_rtx_claim_review` / `rt_core_ready` | Prepared fixed-radius threshold-count summary remains the bounded claim path. |
| `dbscan_clustering` | Group B analyzer `ok` | keep `ready_for_rtx_claim_review` / `rt_core_ready` | Prepared core-threshold summary remains the bounded claim path; clustering expansion remains outside. |
| `database_analytics` | Group C analyzer `ok`, native DB counters exported | keep `needs_interface_tuning` / `rt_core_partial_ready` | Real RTX native counters exist, but same-semantics baseline review and interface/materialization review are still required. |
| `service_coverage_gaps` | Group D analyzer `ok` | keep `ready_for_rtx_claim_review` / `rt_core_ready` | Prepared gap-summary claim path was already promoted; Goal929 confirms batch replay. |
| `event_hotspot_screening` | Group D analyzer `ok` | keep `ready_for_rtx_claim_review` / `rt_core_ready` | Prepared count-summary claim path was already promoted; Goal929 confirms batch replay. |
| `facility_knn_assignment` | Group D analyzer `ok` | keep `ready_for_rtx_claim_review` / `rt_core_ready` | Coverage-threshold decision sub-path remains the only claim path. |
| `road_hazard_screening` | Group E strict parity `pass`; native `1.876493 s` vs CPU `1.355715 s` | move to `needs_native_kernel_tuning`; keep `rt_core_partial_ready` | Correctness is proven, but native RTX path is slower than CPU at tested scale. |
| `segment_polygon_hitcount` | Group E strict parity `pass`; native `0.908164 s` vs host-indexed `0.021224 s` and CPU `0.026720 s` | move to `needs_native_kernel_tuning`; keep `rt_core_partial_ready` | Correctness is proven, but native RTX path is much slower than the current fallback. |
| `segment_polygon_anyhit_rows` | Group E strict parity `pass`, zero overflow | move to `needs_native_kernel_tuning`; keep `rt_core_partial_ready` | Correctness is proven, but the artifact is a small bounded gate, not scalable row-output performance evidence. |
| `graph_analytics` | Group F rerun analyzer `ok`; visibility, BFS, triangle native records pass analytic parity | promote to `ready_for_rtx_claim_review` / `rt_core_ready` | Bounded graph RT sub-paths now have strict RTX artifact evidence. Whole-app graph claims remain excluded. |
| `polygon_pair_overlap_area_rows` | Group H rerun analyzer `ok`; candidate discovery plus CPU refinement parity | promote to `ready_for_rtx_claim_review` / `rt_core_ready` | Candidate-discovery sub-path has phase-clean RTX evidence; exact area remains CPU/Python-owned. |
| `polygon_set_jaccard` | Group H rerun analyzer `ok` at `chunk-copies=20`; parity true | promote to `ready_for_rtx_claim_review` / `rt_core_ready` | Candidate-discovery sub-path is claim-review ready only for the reviewed chunked contract; larger chunks remain diagnostic failures. |
| `hausdorff_distance` | Group G manual small artifact only | keep `needs_real_rtx_artifact` / `rt_core_partial_ready` | Needs analyzer/intake and same-semantics baseline coverage before promotion. |
| `ann_candidate_search` | Group G manual small artifact only | keep `needs_real_rtx_artifact` / `rt_core_partial_ready` | Needs analyzer/intake and same-semantics baseline coverage before promotion. |
| `barnes_hut_force_app` | Group G manual small artifact only | keep `needs_real_rtx_artifact` / `rt_core_partial_ready` | Needs analyzer/intake and same-semantics baseline coverage before promotion. |

## Files Updated

- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `tests/goal705_optix_app_benchmark_readiness_test.py`
- `tests/goal803_rt_core_app_maturity_contract_test.py`
- `tests/goal814_graph_optix_rt_core_honesty_gate_test.py`
- `tests/goal816_polygon_overlap_rt_core_boundary_test.py`
- `tests/goal848_v1_rt_core_goal_series_test.py`
- regenerated `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.{json,md}`

## New Matrix Counts

- Public apps: 18
- `rt_core_ready`: 9
- `rt_core_partial_ready`: 7
- Out of NVIDIA RT scope: 2

## Boundary

This is an intake and matrix synchronization goal. It does not claim public speedups. It only records which bounded RTX sub-paths have enough evidence to enter later claim-review packaging.
