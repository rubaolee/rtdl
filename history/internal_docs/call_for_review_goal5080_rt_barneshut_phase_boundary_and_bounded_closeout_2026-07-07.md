# Call For Review: Goal5080 RT-BarnesHut Phase Boundary And Bounded Closeout

Date: 2026-07-07

## Requested Verdict Label

`approve_goal5080_bounded_same_input_correctness_closed__narrow_phase_review_ready__no_whole_envelope_speedup`

## Review Scope

Please review:

- `history/internal_docs/goal5079_rt_barneshut_live_pod_generic_force_gate_result_2026-07-07.md`
- `history/internal_docs/goal5080_rt_barneshut_phase_boundary_and_bounded_closeout_result_2026-07-07.md`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/full_pod_reproduction_gate/summary.json`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/generic_aggregate_force_same_input_gate/summary.json`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/same_input_performance_gate/summary.json`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/same_input_performance_gate/phase_boundary_review.json`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/phase_boundary_review_gate/summary.json`

## Context

Goal5079 ran the full live POD gate. It passed all correctness and timing-summary gates, including the generic aggregate force same-input gate.

Goal5080 is the follow-up phase-boundary analysis. It asks what can honestly be claimed now.

## Key Facts To Review

Correctness:

```text
generic aggregate same-input force comparison:
  matched = true
  mismatch_count = 0
  max_rel_error = 2.1112736725325853e-06

legacy author-policy CUDA diagnostic comparison:
  matched = true
  mismatch_count = 0
  max_rel_error = 2.6233255615631954e-06
```

Narrow phase timing:

```text
author_treelogy_timing_ms.rt_core_force = 2.083 ms
rtdl_diagnostic_timing_ms.resident_kernel_min = 0.856544017791748 ms
narrow min ratio = 0.4112069216475026
```

Broader reported envelope:

```text
RTDL compile + tree_prepare + H2D + resident_kernel_min = 469.34572154283524 ms
Author preprocessing + execution = 185.44600000000003 ms
Broader envelope ratio = 2.530902373428573
```

Phase review gate:

```text
status = blocked_review_incomplete_or_mismatched
performance_review_complete = false
phase_boundary_accepted = false
reviewed_ratio_matches_summary = true
reviewed_summary_path_matches = true
```

The phase review JSON is intentionally a draft until external review accepts or rejects it.

## Review Questions

1. Does Goal5080 correctly distinguish bounded same-input correctness from full paper reproduction?
2. Does the generic aggregate same-input evidence justify saying bounded same-input scalar force correctness is closed?
3. Is the narrow timing phase (`author rt_core_force` vs `RTDL resident_kernel_min`) labeled narrowly enough?
4. Is it correct to say the narrow resident force kernel is faster on this POD run, while refusing to claim whole-program speedup?
5. Does the broader envelope calculation correctly show RTDL is about `2.53x` slower when reported compile, prepare, H2D, and kernel time are compared to author preprocessing plus execution?
6. Should the phase review gate remain incomplete until an external reviewer explicitly sets `performance_review_complete=true` and `phase_boundary_accepted=true`?
7. Does the report avoid promoting `paper_reproduction_complete=true`?
8. Does the report preserve the generic-system/app boundary, especially around `ContinuationPayloadOpening` and app-owned author prepared-state parsing?
9. Are there any blocking issues before closing Goal5080 with the requested verdict?
10. What exact claim wording should be allowed in future public/internal summaries?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 10 review questions
