# Goal670 Vulkan Performance Optimization Review Request

Please use a Gemini 3 model, if available, to review Vulkan performance optimization opportunities using the Goal669 playbook.

Primary playbook:

`/Users/rl2025/rtdl_python_only/docs/reports/goal669_cross_engine_performance_optimization_lessons_2026-04-20.md`

Vulkan source inputs:

- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`

Relevant prior evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal650_vulkan_native_early_exit_anyhit_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/vulkan_backend_report.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal65_vulkan_optix_linux_comparison_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal72_vulkan_long_county_prepared_exec_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal85_vulkan_hardware_validation_and_measurement_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_measurement_2026-04-05.md`

Write your report to:

`/Users/rl2025/rtdl_python_only/docs/reports/goal670_gemini3_vulkan_performance_optimization_review_2026-04-20.md`

Required sections:

- Current Vulkan performance state.
- What is already optimized.
- Top optimization opportunities, ranked by expected value and implementation risk.
- Workload-specific recommendations for ray/visibility, nearest-neighbor, graph, DB-style, and spatial overlay workloads.
- Vulkan-specific constraints, including acceleration-structure reuse, descriptor/buffer reuse, shader/pipeline reuse, output materialization, and driver variability.
- Risks/blockers that should prevent claims.
- Verdict: `ACCEPT`, `ACCEPT WITH NOTES`, or `BLOCK` for using the report as a Vulkan optimization roadmap.
