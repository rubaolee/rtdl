# Call For Review: Goal5384 X-HD Multi-Round Active-Query Status

Please strictly review Goal5384.

## Files To Review

Implementation:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
```

Tests:

```text
tests/goal5384_multiround_active_query_status_test.py
tests/goal5384_multiround_status_requirements_test.py
```

Artifact builder and artifact:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5384_multiround_status_requirements.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5384_multiround_status_requirements.json
```

Result report:

```text
history/internal_docs/goal5384_xhd_multiround_active_query_status_result_2026-07-10.md
```

Context reports:

```text
history/internal_docs/goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md
history/internal_docs/goal5381_active_query_frontier_bridge_probe_result_2026-07-10.md
history/internal_docs/goal5382_xhd_native_status_machine_stream_design_result_2026-07-10.md
history/internal_docs/goal5383_active_initial_best_status_probe_result_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5383_2026-07-10.md
```

## Review Questions

1. Does `active_query_status_multiround_reference_numpy_columns` implement a
   genuinely generic multi-round active-query status reference rather than an
   X-HD-specific `-lb` shortcut?
2. Does the new helper preserve app-neutral naming and metadata in RTDL core?
3. Does the synthetic test actually exercise multi-round behavior:
   offload in one round, feedback by `active_queue_index`, and completion in a
   later round?
4. Does the implementation correctly preserve multiple raw offload rows and
   cumulative `raw_offload_rows_before_sort_reduce` telemetry?
5. Do fail-closed tests cover malformed feedback and unknown continuation
   status kinds?
6. Does the artifact correctly carry forward the Goal5374 author oracle
   (`27133990` offload rows) and the Goal5383 no-go (`2188225` rows,
   row parity false)?
7. Does the report correctly say this is a CPU/reference contract and not native
   backend completion?
8. Does the report correctly keep explicit author `-lb` unsupported / fail
   closed?
9. Is the next plan correct: native multi-round status stream or stronger
   author trace, not more single-pass prune modes or CPU bridge vectorization?
10. Are any claim boundaries overstated, especially around Figure 7, Figure 11,
    author RT-core parity, performance ratios, or full X-HD reproduction?

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve_goal5384_multiround_status_reference
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 10 review questions:
  1. ...
  ...
  10. ...
```

## Requested Verdict If Clean

```text
approve_goal5384_multiround_status_reference__explicit_lb_still_fail_closed
```
