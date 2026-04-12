Please review Goal 312 in the live repo at:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_312_v0_5_linux_large_scale_native_embree_optix_perf.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal312_v0_5_linux_large_scale_native_embree_optix_perf_2026-04-12.md`

Code and benchmark script to inspect:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal312_kitti_native_embree_optix.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`

Please verify:
- the benchmark structure is technically honest and separates setup from hot
  execution for Embree and OptiX
- the parity claims against the native CPU/oracle path are credible
- the OptiX KNN ranking fix is described coherently and bounded correctly
- the report preserves the Linux-only and first-point-only boundary

Write the final review to:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal312_v0_5_linux_large_scale_native_embree_optix_perf_review_2026-04-12.md`
