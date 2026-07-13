# Call For Review - Goal5375 X-HD RTDL Status-Machine Counterpart Assessment

Please strictly review Goal5375.

## Files To Review

Primary report:

```text
history/internal_docs/goal5375_xhd_rtdl_status_machine_counterpart_assessment_result_2026-07-10.md
```

Primary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5375_rtdl_status_machine_counterpart_assessment.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5375_rtdl_status_machine_counterpart.py
```

Tests:

```text
tests/goal5375_rtdl_status_machine_counterpart_test.py
```

Context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_inline_global_bound_lb_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5373_rtdl_status_machine_telemetry_surface.json
```

## Review Context

Goal5374 produced an author-side oracle:

```text
Author OffloadingSize = 27133990
RawOffloadRowsBeforeSortReduce = 27133990
RawOffloadRowsAuthorWidthBytes = 217071920
ActiveInQueueSize = StatusInitCount = 437645
```

Goal5375 asks whether any current RTDL surface already matches that oracle.

It compares four current surfaces:

```text
author_radius_inline_kind2_current_surface
author_radius_inline_global_bound_kind2_current_surface
author_radius_noinline_raw_kind2_current_surface
goal5365_full_cover_lb256_behavior_gate_surface
```

## Key Evidence

Goal5375 reports:

| Candidate | RTDL rows | Author - RTDL | Ratio | Parity |
|---|---:|---:|---:|---|
| inline kind2 | 21,006,960 | 6,127,030 | 0.7741935484 | false |
| inline + global-bound | 21,006,960 | 6,127,030 | 0.7741935484 | false |
| no-inline raw kind2 | 304,981,889 | -277,847,899 | 11.2398467384 | false |
| Goal5365 full-cover lb256 | 24,508,120 | 2,625,870 | 0.9032258065 | false |

Therefore:

```text
any_candidate_row_count_parity = false
minimum_gate_passed = false
explicit_lb_support_authorized = false
```

## Questions For Reviewer

1. Does Goal5375 correctly use the Goal5374 author oracle as the denominator?
2. Are the four RTDL candidate surfaces the relevant current evidence to test?
3. Does the artifact correctly show that no current candidate matches author
   raw offload row count?
4. Is the "best current candidate" classification correct
   (`goal5365_full_cover_lb256_behavior_gate_surface`, delta 2,625,870)?
5. Does Goal5375 correctly reject existing global-bound early break as an author
   status-machine counterpart?
6. Does the report correctly prevent explicit `-lb` support from being exposed?
7. Are the remaining missing semantics listed correctly:
   author cmin2/current-best restore by `in_q_idx`, cmax2 abort counter,
   miss queue semantics, loadBalanceProcessing feedback, and row parity?
8. Do the tests protect both numeric mismatch and claim boundary?
9. Is the next recommended goal correct: implement or probe a real RTDL
   status-machine mode against the Goal5374 author oracle?
10. Is there any hidden evidence that would justify explicit `-lb` support now?

## Expected Answer Shape

```text
Verdict:
  approve_goal5375_rtdl_status_machine_counterpart_assessment
  OR approve_with_required_amendments
  OR block_goal5375_rtdl_status_machine_counterpart_assessment

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

## Requested Verdict Label If Approved

```text
approve_goal5375_current_rtdl_surface_fails_author_lb_oracle__implement_status_machine_next
```
