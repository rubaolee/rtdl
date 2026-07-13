# Call For Review: Goals5386-5390 X-HD `-lb` Trace Packet

Date: 2026-07-10

Please strictly review the X-HD `-lb` trace packet covering Goals5386-5390.

## Review Scope

This packet asks whether the project has correctly advanced from a weak
count-only author oracle to a full-source RTDL trace-summary comparison, and
whether the conclusion is honest:

```text
explicit X-HD -lb remains unsupported because the full-source RTDL status stream
matches the author active-query count but fails author raw row-count and
hash/sample parity.
```

## Files To Review

### Goal5386: Author Trace V2 Patch Plan

```text
history/internal_docs/goal5386_xhd_author_trace_v2_patch_plan_result_2026-07-10.md
history/internal_docs/call_for_review_goal5386_xhd_author_trace_v2_patch_plan_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5386_author_trace_v2_patch_plan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5386_author_trace_v2_patch_plan.json
tests/goal5386_author_trace_v2_patch_plan_test.py
```

### Goal5387: Author Trace V2 Execution

```text
history/internal_docs/goal5387_xhd_author_trace_v2_execution_result_2026-07-10.md
history/internal_docs/call_for_review_goal5387_xhd_author_trace_v2_execution_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_lb256_status_trace_v2_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_patch_summary_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace_v2.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5387_author_trace_v2_execution.py
tests/goal5387_author_trace_v2_instrumentation_test.py
tests/goal5387_author_trace_v2_execution_test.py
```

### Goal5388: Generic Trace Summary Contract

```text
history/internal_docs/goal5388_xhd_status_trace_summary_contract_result_2026-07-10.md
history/internal_docs/call_for_review_goal5388_xhd_status_trace_summary_contract_2026-07-10.md
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5388_status_trace_summary_contract.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5388_status_trace_summary_contract.json
tests/goal5388_active_query_trace_summary_test.py
tests/goal5388_status_trace_summary_contract_test.py
```

### Goal5389: Source-Limited Bridge Trace Summary Smoke

```text
history/internal_docs/goal5389_xhd_bridge_trace_summary_smoke_result_2026-07-10.md
history/internal_docs/call_for_review_goal5389_xhd_bridge_trace_summary_smoke_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_bridge_trace_summary_smoke.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5389_source64_trace_summary_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5389_bridge_trace_summary_smoke.py
tests/goal5389_bridge_trace_summary_smoke_test.py
```

### Goal5390: Full-Source Trace Summary Gate

```text
history/internal_docs/goal5390_xhd_full_trace_summary_gate_result_2026-07-10.md
history/internal_docs/call_for_review_goal5390_xhd_full_trace_summary_gate_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5390_full_trace_summary_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5390_full_trace_summary_gate.py
tests/goal5390_full_trace_summary_gate_test.py
```

### Current Midterm Status

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5390_2026-07-10.md
memory/progress.md
memory/todo.md
```

## Critical Facts To Verify

1. Goal5386 is only a patch-plan / hook-validation artifact:

   ```text
   all_hooks_found = true
   all_required_fields_covered = true
   author trace v2 not yet executed in Goal5386
   ```

2. Goal5387 is an author-side oracle upgrade:

   ```text
   active_in_queue_size = 437645
   raw_offload_rows_before_sort_reduce = 27133990
   status_count_offloading_append = 27133990
   raw_offload_row_hash = 4333109858711462591
   raw_offload_row_sample_point_ids = [11168, 210712, 437119]
   raw_offload_row_sample_cell_ids = [2924, 17, 17]
   ```

   It does not implement RTDL `-lb`.

3. Goal5388 adds an app-neutral generic system helper:

   ```text
   active_query_status_trace_summary_numpy_columns
   contract = generic_active_query_status_trace_summary_v1
   ```

   Confirm there is no X-HD / paper / author identity in the helper contract.

4. Goal5389 is source-limited plumbing only:

   ```text
   source_limit = 64
   RTDL rows = 320
   author rows = 27133990
   row_count_parity = false
   hash_parity = false
   ```

5. Goal5390 is the decisive full-source gate:

   ```text
   source_limit = null
   active_query_count = 437645
   active_query_count_parity = true
   RTDL rows = 2188225
   author rows = 27133990
   row_count_parity = false
   RTDL hash = 10510374331443640811
   author hash = 4333109858711462591
   hash_parity = false
   ```

6. The packet must not claim:

   ```text
   explicit -lb support;
   row-count parity;
   hash/sample parity;
   Figure 7 reproduction;
   Figure 11 reproduction;
   same-denominator memory;
   author RT-core algorithm parity;
   author-vs-RTDL performance ratio;
   exact paper dataset reproduction;
   full X-HD paper reproduction.
   ```

## Main Review Questions

1. Is Goal5387 a valid author trace v2 oracle for the current
   Dragon -> AsianDragon `lb=256` diagnostic?

2. Is Goal5388's trace-summary helper genuinely generic and suitable as RTDL
   system API rather than X-HD app code?

3. Does Goal5389 correctly prove only source-limited trace-summary plumbing?

4. Does Goal5390 correctly supersede Goal5389 for the full-source parity
   question?

5. Does Goal5390 justify the conclusion that the remaining mismatch is native
   status-stream semantics, not source-limited plumbing?

6. Is the recommended next decision correct?

   ```text
   A. implement a genuine generic native multi-round status stream that changes
      the row denominator; or
   B. close explicit -lb as unsupported under the current RTDL route.
   ```

7. Should bridge runtime optimization be rejected as the next main path while
   row/hash parity is still wrong?

8. Are all claim boundaries correct and conservative?

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
approve_goals5386_5390_xhd_lb_trace_packet__full_denominator_mismatch_confirmed
```
