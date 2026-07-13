# Call For Review - Goal5226 ModelNet40 All-400 Operational Controls

Please strictly review Goal5226.

## Files To Review

```text
history/internal_docs/goal5226_modelnet40_all400_operational_controls_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
```

## Context

Goal5224 proved the algorithm-aware ModelNet40 route on one selected pair per
category:

```text
40 / 40 matched
```

Goal5225 proved heavy-pair feasibility:

```text
largest-1: 2.7M-point pair matched
largest-10: 10 / 10 matched
```

Goal5226 should be reviewed as an **operational readiness** goal for all-400,
not as an all-400 reproduction result.

## Review Questions

1. Does the runner now support chunked execution by explicit range and by
   chunk index/size?
2. Does it preserve global case indices across chunks, rather than renumbering
   each chunk locally?
3. Does `--skip-completed` skip only previously successful per-case artifacts,
   while leaving failed/incomplete cases eligible for rerun?
4. Does `--continue-on-error` capture failures per case without losing later
   case execution?
5. Does `--aggregate-existing-cases` rebuild a summary from per-case artifacts
   and preserve failure counts?
6. Are the tests sufficient for this operational-control layer?
7. Does the implementation remain app-owned, with no ModelNet40/X-HD/Hausdorff
   paper semantics promoted into RTDL core?
8. Does the report avoid claiming all-400 completion, all-2000 completion,
   exact paper input identity, performance reproduction, or full X-HD paper
   reproduction?
9. Is Goal5227 correctly identified as the next step: running the all-400
   unique-pair gate in chunks and aggregating the result?

## Expected Verdict Label

```text
approve_goal5226_modelnet40_all400_operational_controls_ready
```
