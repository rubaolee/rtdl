# Goal 707: Codex Response To Claude BLOCK Finding

Date: 2026-04-21
Status: fixed locally; Claude re-review accepted

## Original Claude Finding

Claude reviewed Goal707 and returned `BLOCK` because four public app-matrix
OptiX cells were labeled `direct_cli_native` while their OptiX performance
classification was `host_indexed_fallback`.

Affected apps:

- `graph_analytics`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

Claude's reasoning was correct: `direct_cli_native` means native backend support
for the app RTDL core, while `host_indexed_fallback` means the OptiX-facing app
path dispatches to CPU-side host-indexed logic. Those labels cannot describe
the same OptiX app path.

## Fix Applied

`/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py` now marks the
four affected OptiX app cells as `direct_cli_compatibility_fallback`.

`/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md` now shows
the same four OptiX cells as `direct_cli_compatibility_fallback`.

`/Users/rl2025/rtdl_python_only/tests/goal707_app_rt_core_redline_audit_test.py`
now pins this relationship:

- each affected app has app-engine OptiX status
  `direct_cli_compatibility_fallback`;
- each affected app keeps OptiX performance class `host_indexed_fallback`.

## Verification

Focused local tests passed:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal707_app_rt_core_redline_audit_test

Ran 21 tests in 0.003s
OK
```

`git diff --check` also passed.

## Consensus State

- Codex: ACCEPT after fixing Claude's label contradiction.
- Gemini Flash: ACCEPT for the red-line report and app audit.
- Claude: initial BLOCK finding accepted as valid and fixed; re-review returned
  ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal707_claude_rereview_2026-04-21.md`.

## Decision

The Goal707 red-line standard is now internally consistent:

- DB app: valid RTDL DB app, OptiX path remains
  `python_interface_dominated`, not a clean RTX flagship.
- Graph app: valid RTDL graph app, Embree CPU BVH/point-query path exists,
  OptiX/Vulkan graph paths remain compatibility/fallback for performance
  claims.
- Spatial apps: Embree CPU spatial-query paths are real RT-style CPU
  execution; only measured OptiX traversal paths on RTX-class hardware can
  support NVIDIA RT-core app claims.
