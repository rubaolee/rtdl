# Call For Review - Goal5369 X-HD lb Queue-State Requirements

Please strictly review Goal5369.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5369_lb_queue_state_requirements.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5369_lb_queue_state_requirements.json
tests/goal5369_lb_queue_state_requirements_test.py
history/internal_docs/goal5369_xhd_lb_queue_state_requirements_result_2026-07-09.md
```

Relevant input evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5361_res4full_nonterminal_author_queue_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5364_lb_trace_gate_author_pair_contract.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5366_lb_denominator_reconciliation.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5367_lb_author_radius_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
```

## What Goal5369 Claims

Goal5369 is a requirements gate for the next X-HD `-lb` implementation step.
It does not implement explicit `-lb` support and does not claim denominator
parity.

It records that the following explanations for author `OffloadingSize` are now
rejected:

```text
byte formula mismatch
scalar radius mismatch alone
materialized RTDL heavy/offload rows
all raw same-radius kind2 rows
```

The key numbers are:

```text
author OffloadingSize       = 27,133,990
RTDL author-radius rows     = 21,006,960
RTDL raw same-radius kind2  = 304,981,889
raw kind2 / author          = 11.239846738352892
```

The proposed next gate is:

```text
author_queue_aligned_lb_trace
```

It requires explicit reporting of:

```text
active_in_queue_size
current_best_state_source
raw_offload_rows_before_sort_reduce
author_width_bytes
row_count_parity
```

## Review Questions

1. Does Goal5369 correctly consume the evidence from Goals5361 and 5364-5368?
2. Does it correctly distinguish the fields already aligned by Goal5361
   (`Iteration`, `NumInputPoints`, `NumOutputPoints`, `Radius`, `CMax2`) from
   the fields not yet aligned (`OffloadingSize`, raw offload rows, per-source
   current-best/cmin2)?
3. Are the numeric conclusions correct?
   - author `OffloadingSize = 27,133,990`
   - author-radius materialized RTDL rows `= 21,006,960`
   - raw same-radius kind2 rows `= 304,981,889`
   - raw kind2 / author `~= 11.24x`
4. Does the artifact correctly reject scalar-radius-only and raw-kind2-only
   explanations for author `OffloadingSize`?
5. Is the proposed next gate specific enough to prevent another denominator
   mismatch?
6. Does the requirements gate avoid promoting X-HD-specific behavior into RTDL
   core?
7. Does the claim boundary correctly forbid explicit `-lb` support, row-count
   parity, Figure 7/11 reproduction, author RT-core parity, performance ratio,
   exact paper reproduction, and full X-HD paper reproduction?
8. Are the tests sufficient for this requirements-gate stage?
9. Should the next implementation route be:
   - reconstruct RTDL queue/current-best state through prior iterations; or
   - instrument/regenerate author to expose queue/current-best arrays and raw
     offload rows?
10. Can Goal5369 be closed with:

```text
lb_queue_state_requirements_ready__implementation_requires_queue_state_reconstruction_or_author_instrumentation
```

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve / approve_with_required_amendments / block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Review question answers:
  1. ...
  2. ...
  ...
  10. ...

Recommended next step:
  ...
```
