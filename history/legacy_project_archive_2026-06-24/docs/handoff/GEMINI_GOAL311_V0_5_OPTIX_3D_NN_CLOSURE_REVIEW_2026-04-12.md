Please review Goal 311 in the live repo at:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_311_v0_5_optix_3d_nn_closure.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal311_v0_5_optix_3d_nn_closure_2026-04-12.md`

Code to inspect:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_core.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal311_v0_5_optix_3d_nn_test.py`

Please verify:
- the 3D OptiX ABI and runtime dispatch are technically coherent
- `bounded_knn_rows` is implemented honestly through fixed-radius rows plus
  Python-side ranking
- the Linux parity evidence is sufficient and honestly described
- the report keeps the platform/performance boundary explicit

Write the final review to:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal311_v0_5_optix_3d_nn_closure_review_2026-04-12.md`
