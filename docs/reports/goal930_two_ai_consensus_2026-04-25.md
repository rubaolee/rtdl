# Goal930 Two-AI Consensus

Date: 2026-04-25

## Scope

Review the Goal930 app-by-app RTX 3090 intake and the resulting support-matrix changes.

Primary report:

`docs/reports/goal930_rtx_3090_app_intake_and_matrix_promotion_2026-04-25.md`

## Verdicts

| Reviewer | Verdict | Blockers | Notes |
|---|---:|---|---|
| Claude | ACCEPT | None | Confirms graph/polygon promotions are bounded and road/segment tuning holds are honest. |
| Gemini | ACCEPT | None | Confirms matrix/doc/test synchronization and no speedup overclaim. |
| Codex | ACCEPT | None | Focused tests and static checks pass locally. |

## Consensus

Goal930 is accepted.

The reviewers agree that:

- `graph_analytics` can move to `ready_for_rtx_claim_review` / `rt_core_ready` only for bounded visibility any-hit and native graph-ray BFS/triangle candidate-generation sub-paths.
- `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` can move to `ready_for_rtx_claim_review` / `rt_core_ready` only for native-assisted candidate discovery; exact area/Jaccard refinement remains CPU/Python-owned.
- `polygon_set_jaccard` readiness is limited to the reviewed `chunk-copies=20` contract; larger chunks remain diagnostic failures.
- `road_hazard_screening`, `segment_polygon_hitcount`, and `segment_polygon_anyhit_rows` should remain `rt_core_partial_ready` and move to `needs_native_kernel_tuning`, because RTX correctness passed but performance/scalable timing is not claim-ready.
- No public speedup claim is authorized by Goal930.

## Verification

Local verification:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests/goal705_optix_app_benchmark_readiness_test.py \
  tests/goal803_rt_core_app_maturity_contract_test.py \
  tests/goal814_graph_optix_rt_core_honesty_gate_test.py \
  tests/goal816_polygon_overlap_rt_core_boundary_test.py \
  tests/goal848_v1_rt_core_goal_series_test.py \
  tests/goal759_rtx_cloud_benchmark_manifest_test.py \
  tests/goal824_pre_cloud_rtx_readiness_gate_test.py

Ran 49 tests in 3.719s
OK
```

Additional checks passed:

```text
python3 -m py_compile src/rtdsl/app_support_matrix.py scripts/goal759_rtx_cloud_benchmark_manifest.py scripts/goal889_graph_visibility_optix_gate.py scripts/goal762_rtx_cloud_artifact_report.py
git diff --check
```
