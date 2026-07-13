# Call For Review: Goal5381 Active-Query Frontier Bridge POD Probe

Date: 2026-07-10

Please strictly review Goal5381:

```text
history/internal_docs/goal5381_active_query_frontier_bridge_probe_result_2026-07-10.md
```

Primary evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_source64_bridge_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_source4096_bridge_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_full_bridge_probe_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
tests/goal5381_active_query_frontier_bridge_probe_test.py
src/rtdsl/active_query_status.py
tests/goal5379_active_query_status_machine_reference_test.py
```

Background evidence:

```text
history/internal_docs/goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md
history/internal_docs/goal5379_active_query_status_machine_reference_result_2026-07-10.md
history/internal_docs/goal5380_active_query_frontier_bridge_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
```

## Requested Verdict Labels

Choose one:

```text
approve_goal5381_active_query_bridge_probe_no_parity__native_status_machine_needed
revise_goal5381_before_next_status_machine_work
block_goal5381_due_to_invalid_oracle_comparison
```

## Review Questions

1. Is Goal5381 correctly framed as a probe / negative row-parity result, not as
   explicit author-compatible `-lb` support?
2. Does the runner genuinely use generic RTDL contracts internally
   (`active_query_status_from_frontier_row_table_numpy_columns` and
   `generic_active_query_status_machine_reference_v1`) while keeping X-HD
   input/oracle ownership in the app?
3. Is the multiple-offload-row correction in the Goal5379 reference necessary
   and correctly tested?
4. Do the bounded POD smokes (64 and 4096 sources) prove the native frontier ->
   active-query bridge path runs without claiming full oracle parity?
5. Does the full POD artifact prove active-query-count parity but offload
   row-count mismatch?
6. Is the mismatch large enough to reject current frontier stream compatibility
   with the Goal5374 author oracle?
7. Is it correct to interpret the next hard problem as the native status-machine
   stream / denominator, rather than merely Python bridge performance?
8. Does the report preserve the required claim boundary:
   no full paper reproduction, no explicit `-lb`, no Figure 7/11, no memory
   parity, no author RT-core parity, and no performance ratio?
9. Is the recommended Goal5382 direction correct: native status-machine stream
   design first, with vectorized bridge as a secondary speed concern?
10. Are there any missing required amendments before moving to Goal5382?

## Expected Answer Shape

Please answer with:

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```

## Important Claim Boundary

The report intentionally says:

```text
row_count_parity = false
explicit_lb_support_claimed = false
same_denominator_memory_claimed = false
```

Please reject any summary that converts this into:

```text
RTDL supports X-HD -lb.
RTDL reproduces Figure 7 or Figure 11.
RTDL matches author OffloadingSize.
RTDL has full X-HD paper reproduction.
```
