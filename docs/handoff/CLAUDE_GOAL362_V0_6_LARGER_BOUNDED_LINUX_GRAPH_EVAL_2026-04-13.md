# Claude Handoff: Goal 362 v0.6 larger bounded Linux graph evaluation

Work in:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

Implement the next bounded `v0.6` evaluation slice after Goal 361.

## Goal

Goal 362: larger bounded Linux real-data graph evaluation

## Scope

Keep the scope bounded.

Extend the current real-data Linux evaluation on `SNAP wiki-Talk` to a larger
bounded case for:
- `bfs`
- `triangle_count`

Preserve the current triangle-count real-data transform:
- simple undirected
- self-loops dropped
- canonical undirected edges deduped

Do not claim:
- full dataset closure
- final benchmark status
- paper-scale reproduction

## Timing contract

Use the corrected timing contract from Goal 361:
- `postgresql_seconds`
  - query-only
- `postgresql_setup_seconds`
  - setup/load/index/analyze

Do not regress to combined PostgreSQL timing.

## Read first

Start by reading:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal361_v0_6_audit_adoption_and_eval_correction_2026-04-13.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_eval.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal357_wiki_talk_bfs_eval.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal359_wiki_talk_triangle_count_eval.py`

## Required work

1. Choose the next larger bounded `wiki-Talk` sizes that are still reasonable.
2. Implement any script updates needed for the larger bounded runs.
3. Add or update focused tests if needed.
4. Run the relevant local tests.
5. Write the goal/report artifacts in the repo:
   - a goal file under `docs/`
   - a report under `docs/reports/`
6. Write your final review-ready summary to:
   - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal362_v0_6_larger_bounded_linux_graph_eval_2026-04-13.md`

## Output requirements

Your final report must include:
- what scale was chosen and why
- which files changed
- what tests were run
- the actual measured results
- the current honesty boundary for the slice

## Constraints

- Keep the repo honest and bounded.
- Do not revert unrelated changes.
- Prefer focused additions over broad refactors.
