# Call For Review: Goal5390 X-HD Full Trace Summary Gate

Date: 2026-07-10

Please strictly review Goal5390.

## Files To Review

Primary report and artifact:

```text
history/internal_docs/goal5390_xhd_full_trace_summary_gate_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_gate.json
```

Raw POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_pod.json
```

Implementation and tests:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5390_full_trace_summary_gate.py
tests/goal5390_full_trace_summary_gate_test.py
```

Prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_bridge_trace_summary_smoke.json
history/internal_docs/goal5389_xhd_bridge_trace_summary_smoke_result_2026-07-10.md
```

## Questions

1. Does Goal5390 genuinely run the full-source bridge gate, not a
   source-limited smoke?

   Expected:

   ```text
   source_limit = null
   source_limit_applied = false
   point_count_a = 437645
   ```

2. Does the artifact emit a real generic trace summary from actual RTDL rows?

   Expected:

   ```text
   contract = generic_active_query_status_trace_summary_v1
   active_query_count = 437645
   row_count = 2188225
   raw_offload_row_hash = 10510374331443640811
   ```

3. Does the full-source RTDL bridge match the author active query count but fail
   the author row/hash/sample parity?

   Expected:

   ```text
   active_query_count_parity = true
   row_count_parity = false
   hash_parity = false
   author rows = 27133990
   RTDL rows = 2188225
   ```

4. Is the conclusion correct that the remaining blocker is native
   status-stream semantics, not source-limited plumbing?

5. Does the packet correctly avoid claiming explicit `-lb` support, Figure 7,
   Figure 11, same-denominator memory, author RT-core algorithm parity,
   performance ratio, exact paper dataset reproduction, or full X-HD paper
   reproduction?

6. Are the tests sufficient for this gate?

   Expected:

   ```text
   Ran 12 tests
   OK
   ```

7. Should Goal5390 close as:

   ```text
   native_status_stream_denominator_mismatch__lb_remains_unsupported
   ```

   or does it require amendment first?

8. What is the correct next move?

   Options:

   ```text
   A. implement a genuine generic native multi-round status stream;
   B. close explicit -lb as unsupported under the current RTDL execution model;
   C. continue bridge/runtime optimization despite row/hash mismatch.
   ```

   The report recommends A or B, and explicitly rejects C as the main path.

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
approve_goal5390_full_trace_summary_gate__lb_denominator_mismatch_confirmed
```
