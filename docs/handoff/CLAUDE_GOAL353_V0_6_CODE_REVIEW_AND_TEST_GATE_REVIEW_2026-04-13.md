# Claude Handoff: Goal 353 v0.6 Code Review and Test Gate Review

Work in:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

Your task is to perform the second external review leg for Goal 353, but not as a passive reviewer only. You should:

1. Review the full bounded `v0.6` code surface implemented so far.
2. Identify any high-risk missing tests or weak tests.
3. Add or improve tests directly in the repo where needed.
4. Run the focused relevant test commands yourself.
5. Write a technical review report to:
   - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal353_v0_6_code_review_and_test_gate_review_2026-04-13.md`

Start by reading these files:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_353_v0_6_code_review_and_test_gate.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal353_v0_6_code_review_and_test_gate_2026-04-13.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal353_v0_6_code_review_and_test_gate_review_2026-04-13.md`

Then review these `v0.6` implementation files:
- `src/rtdsl/graph_reference.py`
- `src/rtdsl/graph_datasets.py`
- `src/rtdsl/graph_eval.py`
- `src/rtdsl/external_baselines.py`
- `src/rtdsl/oracle_runtime.py`
- `src/native/oracle/rtdl_oracle_abi.h`
- `src/native/oracle/rtdl_oracle_internal.h`
- `src/native/oracle/rtdl_oracle_graph.cpp`
- `src/native/oracle/rtdl_oracle_api.cpp`
- `src/native/rtdl_oracle.cpp`
- `scripts/goal352_linux_graph_truth_native_postgresql.py`
- `scripts/goal357_wiki_talk_bfs_eval.py`
- `scripts/goal359_wiki_talk_triangle_count_eval.py`

Then review these existing tests:
- `tests/goal345_v0_6_bfs_truth_path_test.py`
- `tests/goal346_v0_6_triangle_count_truth_path_test.py`
- `tests/goal348_postgresql_bfs_baseline_test.py`
- `tests/goal349_postgresql_triangle_count_baseline_test.py`
- `tests/goal350_v0_6_bfs_oracle_test.py`
- `tests/goal351_v0_6_triangle_count_oracle_test.py`
- `tests/goal352_v0_6_graph_eval_test.py`
- `tests/goal356_v0_6_graph_dataset_prep_test.py`
- `tests/goal357_v0_6_wiki_talk_bfs_eval_test.py`
- `tests/goal359_v0_6_wiki_talk_triangle_count_eval_test.py`

Rules:
- Do not broaden scope beyond the bounded `v0.6` graph opening line.
- Do not revert unrelated work.
- Prefer adding focused regression tests over speculative refactors.
- If you find a real bug that must be fixed to support the tests, fix it directly and test it.
- Keep the boundaries honest:
  - bounded graph applications
  - Linux-first validation
  - real-data slices are still bounded, not full closure

Required output report structure:
- `## Verdict`
- `## Findings`
- `## Test Additions`
- `## Commands Run`
- `## Remaining Risks`

In `## Findings`, prioritize real problems over praise. If there are no material findings, say that explicitly.

In `## Test Additions`, list every file you changed and why.

Your final state should leave:
- the repo with any new/updated test files saved
- the report written to the required path
