# Call For Review: Goal5382 X-HD Native Status-Machine Stream Design

Date: 2026-07-10

Please strictly review Goal5382.

## Files To Review

Result report:

```text
history/internal_docs/goal5382_xhd_native_status_machine_stream_design_result_2026-07-10.md
```

Design artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5382_status_machine_stream_design.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5382_status_machine_stream_design.py
```

Tests:

```text
tests/goal5382_status_machine_stream_design_test.py
```

Related evidence:

```text
history/internal_docs/goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md
history/internal_docs/goal5381_active_query_frontier_bridge_probe_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_full_bridge_probe_pod.json
src/rtdsl/active_query_status.py
```

## Context

Goal5381 showed that the current path:

```text
native cell-MBR frontier rows
-> active_query_status_from_frontier_row_table_numpy_columns
-> generic active-query status-machine reference
```

does not match the Goal5374 author `-lb` oracle:

```text
author offload rows = 27133990
RTDL bridge rows    = 2188225
row parity          = false
```

Goal5382 is a design/decision goal. It does not implement a native backend.
It defines the next generic native stream contract:

```text
generic_active_query_status_stream_v1
```

## Review Questions

1. Does Goal5382 correctly carry forward the Goal5374 and Goal5381 evidence,
   including the failed row-count parity?
2. Is the proposed `generic_active_query_status_stream_v1` contract app-neutral,
   or does it smuggle X-HD / author / paper semantics into RTDL core?
3. Is the required emission point correctly stated as before current frontier
   row dropping/collapsing/filtering that loses offload denominator information?
4. Is it correct to reject bridge vectorization as the immediate semantic fix,
   while allowing it later after row-count parity?
5. Are the required columns, status codes, telemetry, and fail-closed rules
   sufficient for the next native prototype gate?
6. Does the X-HD app mapping preserve the principle that app-specific option
   names, author comparisons, figure wording, and JSON formatting remain app
   owned?
7. Do the tests verify the important claims: evidence mismatch, app-neutral
   contract naming, bridge-optimization rejection, emission point, and forbidden
   claims?
8. Does Goal5382 avoid overclaiming explicit `-lb`, OffloadingSize parity,
   Figure 7/11 reproduction, performance parity, or full X-HD reproduction?
9. Is Goal5383 correctly identified as the next implementation goal if the
   design is approved?
10. Should Goal5382 close with:

```text
native_status_machine_stream_design_ready__explicit_lb_still_fail_closed
```

## Expected Answer Shape

Please answer with:

```text
Verdict:
  approve_goal5382_native_status_machine_stream_design
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  ...
  10. ...
```
