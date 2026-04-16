Please review Goal 426 for the `v0.7` RTDL DB line.

Read these first:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_426_v0_7_rt_db_embree_backend_closure.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal426_v0_7_rt_db_embree_backend_closure_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal415_v0_7_rt_db_execution_interpretation_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal416_v0_7_rt_db_lowering_runtime_contract_2026-04-15.md`

Inspect the implementation:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_scene.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal426_v0_7_rt_db_embree_backend_test.py`

Review questions:

1. Is this now a real RT-style Embree backend for the bounded DB family, rather than a hidden CPU fallback?
2. Does it stay inside the Goal 416 contract honestly?
3. Are any claims in the report overstated or missing a material limitation?

Write your answer to:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal426_v0_7_rt_db_embree_backend_closure_review_2026-04-15.md`
