# Call For Review: Goal5387 X-HD Author Trace V2 Execution

Date: 2026-07-10

Please strictly review Goal5387.

## Files To Review

Primary result:

```text
history/internal_docs/goal5387_xhd_author_trace_v2_execution_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
```

Raw POD evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_lb256_status_trace_v2_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_patch_summary_pod.json
```

Implementation and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace_v2.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5387_author_trace_v2_execution.py
tests/goal5387_author_trace_v2_instrumentation_test.py
tests/goal5387_author_trace_v2_execution_test.py
```

Prior context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5385_author_trace_v2_spec.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5386_author_trace_v2_patch_plan.json
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5386_goal5387_in_progress_2026-07-10.md
```

## Questions

1. Does Goal5387 really execute the author trace v2 on POD, rather than only
   producing a dry-run patch plan?

2. Does the raw POD JSON contain `LBTraceV2` with the Goal5385 schema and the
   required batch fields?

3. Do the core counts match Goal5374?

   Expected:

   ```text
   active_in_queue_size = 437645
   iteration_3 OffloadingSize = 27133990
   raw_offload_rows_before_sort_reduce = 27133990
   status_count_offloading_append = 27133990
   status_count_init = 437645
   ```

4. Does Goal5387 add useful state evidence beyond Goal5374, especially cmin2
   hashes/samples, raw offload row hash/sample, miss/completed counters, and
   loadBalanceProcessing feedback counts?

5. Is the instrumentation limited to the external author source tree and not
   RTDL core?

6. Is the claim boundary correct?  In particular, does the packet avoid
   claiming RTDL explicit `-lb` support, row-count parity, Figure 7/11
   reproduction, memory parity, exact paper dataset reproduction, performance
   ratio, or full X-HD reproduction?

7. Are the tests meaningful enough for this goal?

   Expected test run:

   ```text
   Ran 24 tests in 3.187s
   OK
   ```

8. Is the recommended next goal correct: an RTDL native/generic multi-round
   status stream counterpart against the Goal5387 author trace v2 oracle?

9. Are there any hidden denominator shifts or overclaims in the result report?

10. Should Goal5387 be closed as:

    ```text
    author_trace_v2_oracle_ready__native_counterpart_next
    ```

    or is an amendment required first?

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
approve_goal5387_author_trace_v2_oracle_ready_native_counterpart_next
```
