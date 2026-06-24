# Call For Review: Phoenix V3 Repeated Prepared-Session Runner M3.3

Date: 2026-06-22
Requested reviewer: Claude
Protocol: one bounded automated attempt; if unavailable, record failure and continue non-release engineering.

## Review Request

Please critically review the Phoenix V3 M3.3 local contract change.

Controlling context:

- Phoenix V3 remains `redo_required`.
- Current serious same-RT-hardware V2.14 vs Phoenix V3 all-app geomean is
  `1.011779x`, not release-level performance.
- Release, public speedup, broad V3-over-V2, true-zero-copy, V4/C ABI/embedding
  claims are all forbidden.
- The current core gap is a productized execution path that actually executes
  reusable prepared/session work without app-specific native shortcuts.

## Files To Review

```text
src/rtdsl/prepared_execution.py
src/rtdsl/__init__.py
tests/v3_phoenix_prepared_execution_session_runner_test.py
docs/reports/phoenix_v3_repeated_prepared_session_runner_m3_3_2026-06-22.md
docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md
```

## What Changed

M3.3 adds:

```text
run_repeated_prepared_execution_session(task, measured_repeat_count=...)
```

This API performs:

```text
one cache lookup / prepare phase
warmup inside the runner
N measured prepared executions inside the runner
one prepared-execution report payload
```

The existing single-run API now shares the same internal execution path with
`measured_repeat_count=1`.

The generic helper routes now accept `measured_repeat_count` with default
behavior unchanged:

```text
run_fixed_radius_count_threshold_3d_self_query_prepared_session
run_aabb_index_query_2d_range_intersection_prepared_session
run_radius_graph_component_signature_3d_prepared_session
```

Package surface exports now include:

```text
PreparedExecutionSessionTask
PreparedExecutionSessionResult
run_prepared_execution_session
run_repeated_prepared_execution_session
```

## Validation Already Run

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test

Ran 17 tests
OK
```

Also verified:

```text
import rtdsl as rt
hasattr(rt, "run_repeated_prepared_execution_session") == True
hasattr(rt, "PreparedExecutionSessionTask") == True
```

## Questions For Reviewer

1. Does this change correctly address a generic Phoenix V3 runtime gap rather
   than adding app-specific benchmark logic?
2. Are the claim boundaries still sufficiently strict?
3. Is the repeated-run metadata strong enough to prove one cache lookup,
   measured repeats, and one report payload at local-contract level?
4. Is this only local contract progress, not pod evidence and not a Set-A
   material win?
5. What required edits, if any, should be made before this M3.3 step can be
   treated as closed local engineering progress?

## Expected Verdict Labels

Use one:

```text
approve_local_contract_not_release
approve_with_required_edits_not_release
reject_needs_redesign
blocked_review_not_obtained
```

Explicitly state:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_rerun_authorized: false
```
