# External Independent Release Check Request: Corrected RT v0.6

Date: 2026-04-15

## Purpose

Please perform an independent external release check for the corrected RT `v0.6`
graph line in this repository.

This is **not** a request to continue implementation. It is a request to assess
whether the current internal package is honest, coherent, and externally
credible enough to be considered release-ready after your independent review.

## Repository

- Working repository:
  - `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Review goals

Please evaluate all of the following:

1. Is the corrected RT `v0.6` graph line technically coherent?
2. Are the correctness claims adequately supported?
3. Are the performance claims adequately supported and honestly bounded?
4. Are the documents and goal-flow closure chain consistent?
5. Are there any release-blocking issues still open?

## Important context

This repository previously had an earlier mis-scoped graph-runtime line that was
rolled back from the public branch. The current line is the corrected RTDL-kernel
graph line aligned with the RT graph direction.

This means you should evaluate the corrected RT `v0.6` line as:

- RTDL kernels expressing graph workloads
- RT-style traversal / intersection implementation path
- correctness anchored by:
  - CPU / oracle
  - PostgreSQL
- high-performance backends:
  - Embree
  - OptiX
  - Vulkan

## Primary files to read

### Final benchmark / validation package

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/graph_rt_validation_and_perf_report_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/v0_6_rt_graph_correctness_and_performance_report_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/windows_codex_rt_graph_benchmark_handoff_2026-04-14.md`

### Final bounded closure package

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_402_v0_6_rt_graph_final_correctness_and_performance_closure.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal402_v0_6_rt_graph_final_correctness_and_performance_closure_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal402_v0_6_rt_graph_final_correctness_and_performance_closure_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-14-codex-consensus-goal402-v0_6-rt-graph-final-correctness-and-performance-closure.md`

### Correctness and performance gates

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_400_v0_6_postgresql_backed_all_engine_correctness_gate.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal400_v0_6_postgresql_backed_all_engine_correctness_gate_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal400_v0_6_postgresql_backed_all_engine_correctness_gate_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal400_v0_6_postgresql_backed_all_engine_correctness_gate_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-14-codex-consensus-goal400-v0_6-postgresql-backed-all-engine-correctness-gate.md`

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_401_v0_6_large_scale_engine_perf_gate.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal401_v0_6_large_scale_engine_perf_gate_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal401_v0_6_large_scale_engine_perf_gate_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal401_v0_6_large_scale_engine_perf_gate_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-14-codex-consensus-goal401-v0_6-large-scale-engine-perf-gate.md`

### Pre-release internal gates and hold state

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_403_v0_6_pre_release_code_and_test_cleanup.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal403_v0_6_pre_release_code_and_test_cleanup_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal403_v0_6_pre_release_code_and_test_cleanup_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal403_v0_6_pre_release_code_and_test_cleanup_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal403_v0_6_pre_release_code_and_test_cleanup_review_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-15-codex-consensus-goal403-v0_6-pre-release-code-and-test-cleanup.md`

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_404_v0_6_pre_release_doc_check.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal404_v0_6_pre_release_doc_check_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal404_v0_6_pre_release_doc_check_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal404_v0_6_pre_release_doc_check_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal404_v0_6_pre_release_doc_check_review_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-15-codex-consensus-goal404-v0_6-pre-release-doc-check.md`

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_405_v0_6_pre_release_flow_audit.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal405_v0_6_pre_release_flow_audit_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal405_v0_6_pre_release_flow_audit_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal405_v0_6_pre_release_flow_audit_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal405_v0_6_pre_release_flow_audit_review_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-15-codex-consensus-goal405-v0_6-pre-release-flow-audit.md`

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_406_v0_6_release_hold_after_internal_gates.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal406_v0_6_release_hold_after_internal_gates_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/claude_goal406_v0_6_release_hold_after_internal_gates_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_goal406_v0_6_release_hold_after_internal_gates_review_2026-04-14.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal406_v0_6_release_hold_after_internal_gates_review_2026-04-15.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-15-codex-consensus-goal406-v0_6-release-hold-after-internal-gates.md`

### Active sequence

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/history/goals/v0_6_goal_sequence_2026-04-14.md`

## Key implementation files

Please inspect these if you need to verify the main corrected RT graph path:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/api.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/ir.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/layout_types.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_reference.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_postgresql.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_perf.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_datasets.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/oracle/rtdl_oracle_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/embree/rtdl_embree_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_api.cpp`

## Key tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal389_v0_6_rt_graph_bfs_truth_path_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal390_v0_6_rt_graph_triangle_truth_path_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal391_v0_6_rt_graph_bfs_oracle_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal392_v0_6_rt_graph_triangle_oracle_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal393_v0_6_rt_graph_bfs_embree_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal394_v0_6_rt_graph_bfs_optix_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal395_v0_6_rt_graph_bfs_vulkan_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal396_v0_6_rt_graph_triangle_embree_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal397_v0_6_rt_graph_triangle_optix_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal398_v0_6_rt_graph_triangle_vulkan_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal400_v0_6_postgresql_graph_correctness_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal401_v0_6_large_scale_engine_perf_gate_test.py`

## Internal test evidence already recorded

- full suite:
  - `python3 -m unittest discover -s tests -p '*.py'`
  - result: `Ran 964 tests in 183.119s`
  - status: `OK (skipped=85)`

## Important honesty boundary

Please preserve these boundaries in your review:

- This line is internally review-complete, but **no release act has happened**.
- The Linux benchmark GPU was a GTX 1070 with **no RT cores**, so the OptiX
  numbers are non-RT-core baselines.
- Gunrock was accepted as a BFS baseline, but not as a trusted triangle-count
  baseline on the validated host/build.
- Some external baselines are not exact workload-shape matches:
  - RTDL uses bounded BFS expansion and bounded triangle probe slices
  - Neo4j and some other systems use broader/full-graph workload shapes

## Requested output

Please produce one independent written review that clearly says:

- ACCEPT / ACCEPT WITH GAPS / REJECT
- main release-blocking issues, if any
- non-blocking caveats
- whether this internal package is strong enough to hold for release pending
  external checks

Write your response to:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/external_independent_release_check_review_2026-04-15.md`
