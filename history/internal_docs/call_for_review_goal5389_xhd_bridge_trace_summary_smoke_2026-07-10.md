# Call For Review: Goal5389 X-HD Bridge Trace Summary Smoke

Date: 2026-07-10

Please strictly review Goal5389.

## Files To Review

Primary report and artifact:

```text
history/internal_docs/goal5389_xhd_bridge_trace_summary_smoke_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_bridge_trace_summary_smoke.json
```

Raw POD smoke:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_source64_trace_summary_smoke_pod.json
```

Implementation and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5389_bridge_trace_summary_smoke.py
tests/goal5381_active_query_frontier_bridge_probe_test.py
tests/goal5389_bridge_trace_summary_smoke_test.py
```

Prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5388_status_trace_summary_contract.json
```

## Questions

1. Does the current X-HD active-query bridge probe now call the generic
   `active_query_status_trace_summary_numpy_columns` helper on actual RTDL
   offload rows?

2. Does the source-limited POD smoke contain a real `trace_summary` with:

   ```text
   contract = generic_active_query_status_trace_summary_v1
   row_count = 320
   active_query_count = 64
   raw_offload_row_hash present
   samples present
   ```

3. Does the probe correctly read the Goal5387 author trace v2 oracle and expose
   author hash/sample comparison fields?

4. Does the packet honestly state that this is source-limited and not full
   author denominator parity?

   Expected:

   ```text
   rtdl_bridge_offload_rows = 320
   author_raw_offload_rows_before_sort_reduce = 27133990
   row_count_parity = false
   hash_parity = false
   ```

5. Is the claim boundary correct?  In particular, does it avoid claiming
   explicit `-lb` support, row-count parity, hash/sample parity, Figure 7/11,
   memory parity, performance ratio, exact dataset, or full paper reproduction?

6. Are the tests sufficient for this smoke-level goal?

   Expected:

   ```text
   Ran 13 tests
   OK
   ```

7. Is the recommended next goal correct: a full or bounded native status-stream
   parity gate against Goal5387, not more source-limited smoke or bridge
   optimization?

8. Should Goal5389 close as:

   ```text
   bridge_trace_summary_smoke_ready__full_native_stream_parity_still_required
   ```

   or does it require amendment first?

## Expected Answer Shape

Please answer in this form:

```text
Verdict: approve / approve_with_required_amendments / block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to questions:
1. ...
2. ...
...
8. ...
```

Requested verdict label if approved:

```text
approve_goal5389_bridge_trace_summary_smoke_full_parity_still_required
```
