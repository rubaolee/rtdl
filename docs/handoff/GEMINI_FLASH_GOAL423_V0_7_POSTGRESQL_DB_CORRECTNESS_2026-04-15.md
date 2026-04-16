Please review Goal 423 for the RTDL `v0.7` DB line.

Read:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal423_v0_7_postgresql_db_correctness_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/db_postgresql.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/db_reference.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal423_v0_7_postgresql_db_correctness_test.py`

Judge whether Goal 423 is acceptably closed as a bounded PostgreSQL-backed correctness goal for `conjunctive_scan`.

Focus on:
- whether PostgreSQL is a real external correctness anchor here
- whether the report accurately states the Linux validation evidence
- whether the use of `run_cpu(...)` is honestly bounded
- whether there is any blocker

Write your review to:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal423_v0_7_postgresql_db_correctness_review_2026-04-15.md`
