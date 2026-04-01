# Goal 20 Iteration 1 Pre-Implementation Report

## Scope

This report reviews the uploaded external Claude audit against the current RTDL repository state before any revision work is accepted.

## Initial Classification

### Accepted and actionable now

1. **Two workloads still use `native_loop` rather than BVH-backed traversal.**
   - Verified in [lowering.py](/Users/rl2025/rtdl_python_only/src/rtdsl/lowering.py) where both `segment_polygon_hitcount` and `point_nearest_segment` lower to `accel_kind="native_loop"`.
   - Verified in [rtdl_embree.cpp](/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp) where both implementations execute explicit nested loops instead of Embree scene traversal.
   - This is already documented, but it remains a valid limitation and should be described consistently.

2. **No exact / robust geometry mode.**
   - Verified in [lowering.py](/Users/rl2025/rtdl_python_only/src/rtdsl/lowering.py): lowering rejects precision other than `float_approx`.
   - Verified in [reference.py](/Users/rl2025/rtdl_python_only/src/rtdsl/reference.py): current semantics are float-based with inclusive boundary handling for PIP.
   - Action: make the boundary and exact-mode status easier to find and less likely to be over-claimed.

3. **Workload extensibility still requires coordinated multi-file changes.**
   - Still true in the current architecture.
   - This is a design pressure finding rather than a discrete bug, but the repo should document it more explicitly and avoid implying that workload addition is already cheap.

4. **Embree binding complexity is real.**
   - [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py) remains large and pointer-heavy.
   - This is not necessarily a bug, but it is a valid maintainability concern.

5. **CI / cross-platform automation is still missing.**
   - No current CI workflow files were found in the repo.
   - Action: docs should describe this honestly as a limitation.

### Accepted but partly already documented

6. **Missing guidance on runtime execution modes.**
   - The repo now has some guidance for `dict`, `raw`, and prepared/raw modes, but it is spread across multiple reports and runtime docs rather than one obvious user-facing place.
   - Action: consolidate and cross-link runtime mode guidance.

7. **Formal semantics documentation could be tighter.**
   - PIP boundary behavior is documented as inclusive in multiple places, so the audit overstates total absence.
   - But there is still room to add a more direct semantics/troubleshooting note in one central doc.

### Likely outdated or overstated

8. **Silent output truncation.**
   - Current native entrypoints return dynamically allocated rows via `copy_rows_out(rows)` and `row_count_out = rows.size()`.
   - The current Embree CPU runtime path does not appear to use a fixed-capacity output buffer with silent truncation.
   - This claim may reflect an older OptiX-style output-capacity design or stale assumptions rather than the current local Embree implementation.
   - Needs explicit confirmation during the revision round, but current evidence points to "outdated for the local Embree path".

9. **Test scale and missing docs are understated or stale.**
   - The audit says "18 test files"; the current repo has materially more than that and currently reports 80 passing tests.
   - Some of the cited "missing docs" already exist, though they are scattered.

## Proposed Revision Scope

1. tighten the docs around:
   - `native_loop` vs BVH-backed workloads,
   - exact-mode limitations,
   - execution-mode selection (`dict`, `raw`, prepared/raw),
   - current CI / portability status,
   - maintainability boundaries for workload growth
2. add a short audit-response note that explicitly rejects or narrows the stale truncation claim unless Claude can point to a current path that still truncates silently
3. only make code changes if Claude identifies a current behavior bug rather than a documentation or architecture-status issue

## Current Position

The uploaded audit is directionally strong and useful, but not every finding should be treated as a current bug. The next step should be to send this classified scope to Claude and Gemini for review before making repo changes.
