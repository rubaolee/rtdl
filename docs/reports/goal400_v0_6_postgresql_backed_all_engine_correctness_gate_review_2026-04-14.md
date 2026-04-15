# Goal 400 Review: v0.6 PostgreSQL-Backed All-Engine Correctness Gate

Date: 2026-04-14
Status: accepted

## Review Basis

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal400_v0_6_postgresql_backed_all_engine_correctness_gate_review_2026-04-14.md`

Implementation/report:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_400_v0_6_postgresql_backed_all_engine_correctness_gate.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal400_v0_6_postgresql_backed_all_engine_correctness_gate_2026-04-14.md`

## Codex Assessment

Gemini's judgment is consistent with the code and with the live Linux evidence.

Goal 400 is a valid bounded correctness gate because:

- the PostgreSQL graph baseline matches the one-step RT-kernel semantics for:
  - `bfs`
  - `triangle_count`
- the SQL paths use explicit bounded temp-table preparation and graph indexes:
  - edge `(src)`
  - edge `(dst)`
  - edge `(src, dst)`
  - frontier `(vertex_id)`
  - visited `(vertex_id)`
  - seeds `(u, v)`
- the Linux PostgreSQL-backed suite is green:
  - `Ran 6 tests`
  - `OK`
- the Linux integrated graph + PostgreSQL suite is green:
  - `Ran 51 tests`
  - `OK`
- that Linux run also had live backend execution for:
  - Embree
  - OptiX
  - Vulkan

So the corrected `v0.6` graph line now has bounded correctness anchored by:

- Python
- native/oracle
- Embree
- OptiX
- Vulkan
- PostgreSQL

## Verdict

Accepted as a bounded Goal 400 PostgreSQL-backed all-engine correctness gate.
