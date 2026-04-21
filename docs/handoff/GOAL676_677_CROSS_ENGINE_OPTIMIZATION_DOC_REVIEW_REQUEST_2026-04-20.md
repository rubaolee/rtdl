# Goal676/677 Cross-Engine Optimization Closure And Public Doc Review Request

Please review the current RTDL cross-engine visibility/count optimization
closure and public-doc refresh.

Return a verdict of `ACCEPT` or `BLOCK`, with concise reasons. If accepted,
confirm whether the performance claims are correctly bounded. If blocked,
identify the exact file and claim that must be fixed.

Primary report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal676_677_cross_engine_optimization_closure_and_doc_refresh_2026-04-20.md`

Public docs changed for this closure:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_main_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

Implementation and test evidence to sample:

- `/Users/rl2025/rtdl_python_only/tests/goal671_optix_prepared_anyhit_count_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal674_hiprt_prepared_anyhit_2d_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal675_vulkan_prepared_anyhit_2d_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal671_optix_prepared_anyhit_and_hiprt_boundary_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal672_optix_prepacked_ray_anyhit_count_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal673_optix_prepacked_ray_cleanup_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal674_hiprt_prepared_2d_anyhit_optimization_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal675_vulkan_prepared_2d_anyhit_packed_optimization_2026-04-20.md`

Verification already run locally:

- focused optimization/public-doc tests:
  `PYTHONPATH=src:. python3 -m unittest tests.goal671_optix_prepared_anyhit_count_test tests.goal674_hiprt_prepared_anyhit_2d_test tests.goal675_vulkan_prepared_anyhit_2d_test tests.goal506_public_entry_v08_alignment_test tests.goal654_current_main_support_matrix_test tests.goal655_tutorial_example_current_main_consistency_test -v`
  - result: `29` tests OK, `7` skipped
- public command truth audit:
  `PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py`
  - result: `valid: true`, `250` commands, `14` docs
- public entry smoke:
  `PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py`
  - result: `valid: true`
- whitespace:
  `git diff --check`
  - result: clean

Claims that must remain bounded:

- Apple RT scalar count win is not full emitted-row speedup.
- OptiX Linux GTX 1070 result is not RT-core evidence.
- HIPRT/Orochi CUDA result is not AMD GPU evidence.
- Vulkan prepared tuple-ray calls alone are not claimed faster; the measured
  win requires prepacked rays.
- None of these visibility/count optimizations prove DB, graph, one-shot, or
  broad backend speedups.
