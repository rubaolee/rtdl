Please review Goal 206 in the current RTDL repo checkout.

Read these files first:
- `/Users/rl2025/rtdl_python_only/docs/goal_206_knn_rows_embree.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal206_knn_rows_embree_2026-04-10.md`
- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_scene.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal206_knn_rows_embree_test.py`

Then write your review to:
- `/Users/rl2025/rtdl_python_only/docs/reports/gemini_goal206_knn_rows_embree_review_2026-04-10.md`

Response format:
- exactly three short sections titled `Verdict`, `Findings`, and `Summary`

Review focus:
- does the Embree path preserve the frozen `knn_rows` contract?
- does it match the existing Python truth-path and CPU/oracle semantics?
- are there any correctness or honesty issues that block closure?
