# Goal904 Two-AI Consensus

Date: 2026-04-24

## Scope

Goal904 adds an explicit native OptiX graph-ray source path for graph BFS and
triangle-count candidate generation. The path is gated by
`RTDL_OPTIX_GRAPH_MODE=native` or `--optix-graph-mode native`; the public default
remains host-indexed until a real RTX cloud artifact validates compile,
correctness, and phase selection.

## Review Inputs

- Primary report:
  `docs/reports/goal904_optix_graph_ray_mode_2026-04-24.md`
- Claude review:
  `docs/reports/goal904_claude_review_2026-04-24.md`
- Gemini review:
  `docs/reports/goal904_gemini_review_2026-04-24.md`
- Focused tests:
  `tests/goal904_optix_graph_ray_mode_test.py`,
  `tests/goal903_embree_graph_ray_traversal_test.py`,
  `tests/goal902_app_by_app_rt_usage_report_test.py`

## Consensus

| Reviewer | Verdict | Notes |
|---|---|---|
| Claude Sonnet 4.6 | ACCEPT after remediation | Initial BLOCK found that OptiX pipeline launch params require a `params` symbol. The implementation now splits BFS and triangle kernels, each declaring `__constant__ ... params`. |
| Gemini | ACCEPT after remediation | Confirmed split kernels, explicit native-mode gating, and no RTX runtime/speedup claim before cloud validation. |

## Accepted Boundary

- Source-level native OptiX graph-ray BFS and triangle-count paths exist.
- The default OptiX graph path remains conservative and host-indexed.
- `--require-rt-core` still fails for BFS and triangle-count before cloud
  promotion, even when native mode is selected.
- No public NVIDIA RT-core performance claim is authorized from this goal.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal904_optix_graph_ray_mode_test tests.goal903_embree_graph_ray_traversal_test tests.goal902_app_by_app_rt_usage_report_test -v
```

Result: `10` tests, `OK`.

```text
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_graph_bfs.py examples/rtdl_graph_triangle_count.py examples/rtdl_graph_analytics_app.py tests/goal904_optix_graph_ray_mode_test.py tests/goal903_embree_graph_ray_traversal_test.py src/rtdsl/app_support_matrix.py
git diff --check
```

Result: both passed.

## Next Gate

The next material validation requires the consolidated RTX cloud run. The cloud
artifact must prove:

- `make build-optix` succeeds with the new graph kernels
- native BFS rows match CPU/oracle rows
- native triangle-count rows match CPU/oracle rows
- runtime phase logs prove `RTDL_OPTIX_GRAPH_MODE=native` was selected
- post-cloud external review accepts the artifact before any claim promotion
