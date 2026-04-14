# Gemini Handoff: v0.5+v0.6 Detailed Code and Doc Audit

Work in:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

Write your report to:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_v0_5_plus_v0_6_detailed_code_and_doc_audit_2026-04-13.md`

## Audit intent

This is a strict error-finding audit, not a sign-off pass.

Your job is to help find:
- real bugs
- weak tests
- silent assumption failures
- doc drift
- stale claims
- missing boundaries
- review/goal-flow inconsistencies
- places where code and docs do not actually match

Be skeptical. Prefer finding concrete problems over giving approval language.

## Scope

Audit the repo from the `v0.5` transition through the current bounded `v0.6` graph line.

That means:
- released `v0.5` surfaces and their current docs
- current post-release `v0.5` audit/doc state
- current local `v0.6` graph code/doc/test/eval slice

## Read first

Start with these files:
- `/Users/rl2025/refresh.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5/support_matrix.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5/audit_report.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/comprehensive_v0_5_transition_audit_report_2026-04-12.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_v0_5_full_repo_audit_review_2026-04-12.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/v0_6_goal_sequence_2026-04-13.md`

Then inspect the current `v0.6` code surface:
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

Then inspect the current `v0.6` tests:
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

Then inspect the current `v0.6` goal docs/reports for semantic and process correctness:
- `docs/goal_337_v0_6_graph_workloads_version_plan.md`
- `docs/goal_338_v0_6_graph_workload_charter.md`
- `docs/goal_339_v0_6_graph_data_layout_contract.md`
- `docs/goal_340_v0_6_bfs_truth_path.md`
- `docs/goal_341_v0_6_triangle_count_truth_path.md`
- `docs/goal_342_v0_6_bfs_first_backend_closure.md`
- `docs/goal_343_v0_6_triangle_count_first_backend_closure.md`
- `docs/goal_344_v0_6_linux_graph_evaluation_and_paper_correlation.md`
- `docs/goal_353_v0_6_code_review_and_test_gate.md`
- `docs/goal_356_v0_6_real_graph_dataset_prep.md`
- `docs/goal_357_v0_6_wiki_talk_bfs_bounded_eval.md`
- `docs/goal_359_v0_6_wiki_talk_triangle_count_bounded_eval.md`
- matching reports under `docs/reports/`

## What to check

### 1. Code audit

For each important code file, determine:
- what it does
- whether the implementation matches the claimed contract
- whether there are hidden bugs or fragile assumptions
- whether tests really cover the risky behavior

Specifically look for:
- graph-shape assumptions not enforced
- sorted-neighbor assumptions not documented or not tested
- out-of-bounds or invalid-ID issues
- duplicate-edge / self-loop handling mistakes
- PostgreSQL query limitations that are under-documented
- oracle/Python contract mismatches
- script/report drift

### 2. Test audit

For each important test file, determine:
- what behavior it actually proves
- what risky behavior it misses
- whether any “green” tests are too weak to justify the claims

Be concrete about missing tests.

### 3. Public-doc audit

For each important public-facing doc, determine:
- whether version and status wording is correct
- whether Linux vs Windows/macOS support is honest
- whether backend claims are understandable to an outsider
- whether code/docs disagree
- whether docs expose internal-only material by mistake

### 4. Goal/process audit

Check whether the `v0.6` goals so far follow the required discipline:
- bounded scope
- external review saved
- internal review saved
- Codex consensus saved
- honest closure wording

Point out any gaps or suspicious closures.

## Output requirements

The report must be detailed and use tables.

Use these sections exactly:

## Verdict

Short overall assessment.

## Code Audit

Use a table with columns:
- Path
- Purpose
- Main Risks
- Test Coverage Status
- Problems Found
- Recommended Fix

## Test Audit

Use a table with columns:
- Path
- What It Proves
- What It Misses
- Strength
- Recommended Fix

## Public Doc Audit

Use a table with columns:
- Path
- Audience
- Status Correct?
- Problems Found
- Recommended Fix

## Goal Flow Audit

Use a table with columns:
- Goal
- Scope Bounded?
- External Review Saved?
- Internal Review Saved?
- Codex Consensus Saved?
- Closure Honest?
- Problems Found

## Top Findings

List the highest-signal real problems in severity order.

## Recommended Next Actions

Give a concrete ordered list of next steps.

## Final Judgment

State clearly:
- whether the `v0.5` released surface appears materially sound
- whether the current bounded `v0.6` line appears technically coherent
- whether any goals should be reopened
- which issues are documentation-only vs code-level

## Important style constraints

- Be strict.
- Prefer concrete findings over praise.
- Do not just summarize the repo.
- Do not assume that a green test means adequate coverage.
- If a report is overstated, say so explicitly.
- If a boundary is honest and acceptable, say that clearly too.
