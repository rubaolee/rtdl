# Call For Review: Goal5388 X-HD Status Trace Summary Contract

Date: 2026-07-10

Please strictly review Goal5388.

## Files To Review

Primary report and artifact:

```text
history/internal_docs/goal5388_xhd_status_trace_summary_contract_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5388_status_trace_summary_contract.json
```

System API:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
```

Builder and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5388_status_trace_summary_contract.py
tests/goal5388_active_query_trace_summary_test.py
tests/goal5388_status_trace_summary_contract_test.py
```

Prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5381_full_bridge_probe_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5383_full_seeded_active_initial_best_probe_pod.json
```

## Questions

1. Is `active_query_status_trace_summary_numpy_columns` genuinely app-neutral,
   or does it leak X-HD / paper / author semantics into RTDL core?

2. Does the helper expose a useful generic summary shape for active-query
   offload rows?

   Expected:

   ```text
   row_count
   status_count_offloading
   active_query_count
   raw_offload_row_hash
   sample_indices
   samples
   ```

3. Does the helper fail closed on missing columns, mismatched shapes, and
   invalid sample indices?

4. Is it correctly exported through the public RTDL API surface?

5. Does Goal5388 correctly carry forward the Goal5387 author trace v2 target,
   especially:

   ```text
   active_in_queue_size = 437645
   raw_offload_rows_before_sort_reduce = 27133990
   raw_offload_row_hash present
   raw offload samples present
   cmin2 hashes present
   ```

6. Does the result honestly say current RTDL full probes still fail row-count
   parity and lack hash/sample comparability?

7. Is the claim boundary correct?  In particular, does Goal5388 avoid claiming
   explicit `-lb` support, row-count parity, hash/sample parity, Figure 7/11,
   memory parity, performance ratio, exact dataset, or full paper reproduction?

8. Are the focused tests meaningful enough for this contract?

   Expected:

   ```text
   Ran 15 tests
   OK
   ```

9. Is the recommended next goal correct: a native/generic status stream that
   emits this summary from actual RTDL raw status rows and compares it to the
   Goal5387 author trace v2 oracle?

10. Should Goal5388 close as:

    ```text
    status_trace_summary_api_ready__next_native_stream_must_emit_summary
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
10. ...
```

Requested verdict label if approved:

```text
approve_goal5388_status_trace_summary_api_ready_next_native_stream
```
