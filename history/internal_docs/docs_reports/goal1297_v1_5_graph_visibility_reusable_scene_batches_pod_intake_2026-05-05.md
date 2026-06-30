# Goal1297: Graph Visibility Reusable Scene Batches Pod Intake

Date: 2026-05-05

## Source

- Commit: `3fbc36330bddd74db5782a5c31294943d9f7666a`
- Pod repo: `/workspace/rtdl_goal1292`
- Pod env: reused Goal1292 OptiX/CUDA environment from
  `docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.sh`

## Command

```text
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py \
  --backend optix \
  --scenario visibility_edges \
  --output-mode summary \
  --copies 30000 \
  --visibility-query-repeats 100 \
  --visibility-ray-batches 4 \
  --require-rt-core
```

## Result

The OptiX graph visibility summary path reused one generic prepared
ray/triangle scene across four ray batches.

| Field | Value |
| --- | ---: |
| Candidate edge rays | 120000 |
| Visible edges | 30000 |
| Blocked edges | 90000 |
| Ray batches | 4 |
| Query repeats per batch | 100 |
| Prepared scene reused | true |

Timing phases:

| Phase | Seconds |
| --- | ---: |
| Input construction | 0.020167388021945953 |
| Blocker pack | 0.2842858899384737 |
| Ray pack total | 0.03096035122871399 |
| Scene prepare | 0.8149793520569801 |
| Ray prepare total | 0.0005995091050863266 |
| Any-hit query total | 0.02673371694982052 |
| Any-hit query first | 0.0001653563231229782 |
| Any-hit query mean | 0.00006683429237455129 |
| Any-hit query min | 0.00006304308772087097 |
| Summary postprocess | 0.00000040978193283081055 |

Focused pod tests passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1297_v1_5_graph_visibility_reusable_scene_batches_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test
```

Result: 15 tests OK.

## Artifacts

- `docs/reports/goal1297_v1_5_graph_visibility_reusable_scene_batches_pod_results/graph_visibility_batches_30k_x100_b4.json`
- `docs/reports/goal1297_v1_5_graph_visibility_reusable_scene_batches_pod_results/source_commit.txt`
- `docs/reports/goal1297_v1_5_graph_visibility_reusable_scene_batches_pod_results/unittest_goal1297_goal814.txt`

## Boundary

This is internal v1.5 graph visibility evidence. It proves that the graph app
can reuse the app-name-free generic OptiX prepared scene session across ray
batches for the bounded `visibility_edges` sub-path. It does not claim whole
graph analytics acceleration, BFS acceleration, triangle-count acceleration, or
public speedup wording.
