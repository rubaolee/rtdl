# Gemini Collaborator Review: RTDL v0.5 Pre-Release

You are reviewing the current RTDL `v0.5` line as a **technical collaborator**,
not as a casual outside user.

Your job is to find real problems in the existing work before final release
packaging. Be strict. Prefer finding concrete technical weaknesses over being
polite.

Write your final report to:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_v0_5_collaborator_pre_release_review_2026-04-13.md`

## 1. Required context to read first

Read these files before making judgments:

1. `/Users/rl2025/refresh.md`
2. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`
3. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/README.md`
4. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/goals/v0_5_goal_sequence_2026-04-11.md`
5. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/README.md`
6. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/support_matrix.md`
7. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/pre_release_plan.md`
8. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/code_test_plan.md`
9. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/audit_and_external_review_packet.md`
10. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal320_v0_5_preview_readiness_audit_2026-04-12.md`
11. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/audits/comprehensive_v0_5_transition_audit_report_2026-04-12.md`
12. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/final_v0_5_preview_session_audit_summary_2026-04-12.md`
13. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/audits/gemini_v0_5_full_repo_audit_review_2026-04-12.md`
14. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/v0_5_external_aggressive_user_audit_2026-04-12.md`

## 2. Review stance

This is **not** the next external-user action.

You are acting as a collaborator who understands that:

- the repo is at `v0.5 preview`, not final release
- Linux is the primary performance-validation host
- Windows/local macOS are bounded correctness hosts
- the NN/backend line is already substantially real
- the remaining work is release-quality judgment, packaging, and honesty

You should review for:

- technical coherence
- release honesty
- missing tests
- weak tests
- stale or contradictory docs
- release blockers
- hidden packaging risks
- areas where the repo claims more than it has actually proven

## 3. Required code/test inspection

Inspect the code and test surfaces that matter most for `v0.5`:

### Core runtime/package surfaces

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/external_baselines.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/layout_types.py`

### RTNN / real-data surfaces

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_kitti.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_comparison.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_cunsearch.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_cunsearch_live.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_duplicate_audit.py`

### Primary test surfaces

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/claude_v0_5_full_review_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/test_core_quality.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal298_v0_5_embree_3d_fixed_radius_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal299_v0_5_embree_3d_bounded_knn_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal300_v0_5_embree_3d_knn_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal315_v0_5_vulkan_3d_nn_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal328_v0_5_layout_types_name_collision_test.py`

## 4. Required command/test pass

If tool execution is available, run these exact commands and use the observed
results in your review:

### Broad regression gate

```bash
cd /Users/rl2025/worktrees/rtdl_v0_4_main_publish
python3 -m unittest tests.claude_v0_5_full_review_test
```

### Focused runtime / NN gate

```bash
cd /Users/rl2025/worktrees/rtdl_v0_4_main_publish
python3 -m unittest \
  tests.goal292_v0_5_native_3d_fixed_radius_oracle_test \
  tests.goal293_v0_5_native_3d_bounded_knn_oracle_test \
  tests.goal296_v0_5_native_3d_knn_oracle_test \
  tests.goal298_v0_5_embree_3d_fixed_radius_test \
  tests.goal299_v0_5_embree_3d_bounded_knn_test \
  tests.goal300_v0_5_embree_3d_knn_test \
  tests.goal315_v0_5_vulkan_3d_nn_test \
  tests.goal328_v0_5_layout_types_name_collision_test
```

If you cannot run a command, say so explicitly and explain what blocked you.

## 5. What to audit

Your report must answer these questions:

1. Is the current `v0.5` pre-release package technically coherent?
2. Do the docs tell the same story across:
   - README
   - docs index
   - support matrix
   - pre-release package
3. Are there any meaningful gaps in the current test gate?
4. Are there any code or packaging risks that still deserve bounded fixes before
   final release?
5. Is the current state honestly ready for the **final external review round**?
6. What should be fixed before writing the final `v0.5` release statement?

## 6. Output format

Your report must contain these sections in this order:

### A. Executive Verdict

State one of:

- `ready for final external review`
- `not ready for final external review`

Then explain why in 3-6 sentences.

### B. Findings Table

Use a table with columns:

- `Area`
- `Severity`
- `Finding`
- `Why It Matters`
- `Recommended Action`

Only include real findings. If you find none in an area, say that explicitly in
the later coverage sections.

### C. Code/Test Assessment

Use a table with columns:

- `Surface`
- `Status`
- `Evidence`
- `Concern`

Cover:

- runtime surface
- NN workload surface
- backend surface
- broad regression test gate
- focused runtime/NN test gate

### D. Docs/Release Assessment

Use a table with columns:

- `Document`
- `Current Role`
- `Status`
- `Problem`
- `Recommended Fix`

### E. Remaining Release Blockers

Flat bullet list only.

If you think there are no real blockers before the final external review round,
say that explicitly.

### F. Final Recommendation

State:

1. whether the repo is ready for the **final bounded external review round**
2. whether any bounded internal fix should happen before that
3. what the likely final-release package should still contain

## 7. Review style constraints

- Be strict.
- Do not praise the repo just for effort.
- Do not rewrite the package; audit it.
- Do not drift into open-ended product ideation.
- Keep the review grounded in the current repo state.
- If you make an inference instead of observing a fact, label it clearly.
