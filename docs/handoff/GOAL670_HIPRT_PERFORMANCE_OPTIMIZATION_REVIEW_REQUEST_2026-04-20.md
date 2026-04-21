# Goal670 HIPRT Performance Optimization Review Request

Please review HIPRT performance optimization opportunities using the Goal669 playbook.

Primary playbook:

`/Users/rl2025/rtdl_python_only/docs/reports/goal669_cross_engine_performance_optimization_lessons_2026-04-20.md`

HIPRT source inputs:

- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_kernels.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`

Relevant prior evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal639_v0_9_5_hiprt_native_early_exit_anyhit_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal565_hiprt_prepared_ray_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal566_hiprt_prepared_nn_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal567_hiprt_prepared_graph_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_2026-04-18.md`

Write your report to:

`/Users/rl2025/rtdl_python_only/docs/reports/goal670_claude_hiprt_performance_optimization_review_2026-04-20.md`

Required sections:

- Current HIPRT performance state.
- What is already optimized.
- Top optimization opportunities, ranked by expected value and implementation risk.
- Workload-specific recommendations for ray/visibility, nearest-neighbor, graph, DB-style, and spatial overlay workloads.
- Mechanism honesty boundaries, including HIPRT-on-NVIDIA/Orochi versus real AMD GPU validation.
- Risks/blockers that should prevent claims.
- Verdict: `ACCEPT`, `ACCEPT WITH NOTES`, or `BLOCK` for using the report as a HIPRT optimization roadmap.
