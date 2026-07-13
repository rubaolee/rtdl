# Call For Review - Goal5378 X-HD `-lb` Status-Machine Direction Decision

Date: 2026-07-10

Please strictly review Goal5378.  This is a **decision/design goal**, not a new
performance or kernel implementation claim.

## Files To Review

Primary report:

```text
history/internal_docs/goal5378_xhd_lb_status_machine_direction_decision_2026-07-10.md
```

Decision artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5378_lb_status_machine_direction_decision.json
```

Supporting evidence:

```text
history/internal_docs/goal5372_xhd_author_shader_status_machine_gap_result_2026-07-09.md
history/internal_docs/goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md
history/internal_docs/goal5375_xhd_rtdl_status_machine_counterpart_assessment_result_2026-07-10.md
history/internal_docs/goal5376_status_machine_candidate_contract_result_2026-07-10.md
history/internal_docs/goal5377_frontier_status_probe_mode_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5375_rtdl_status_machine_counterpart_assessment.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5377_frontier_status_probe_mode_comparison.json
```

Current comprehensive handoff:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5377_2026-07-10.md
```

## Review Questions

1. Does Goal5378 correctly read the evidence from Goals5372/5374/5375/5376/5377?

2. Is it correct that scalar-radius tuning, raw-kind2 counting, existing
   global-bound, and `heavy-before-inline-prune` have all failed to explain the
   author `OffloadingSize = 27,133,990` denominator?

3. Is the selected direction,
   `authorize_generic_active_query_status_machine_design`, justified by the
   evidence?

4. Does the proposed active-query/status-machine direction stay generic enough
   for RTDL core, rather than embedding X-HD-specific author behavior?

5. Does Goal5378 correctly keep explicit `-lb` fail-closed?

6. Does Goal5378 avoid claiming row-count parity, same-denominator Figure 11
   memory parity, Figure 7 reproduction, author RT-core parity, performance
   parity, or full X-HD paper reproduction?

7. Is Goal5379, as proposed, the right next goal: a CPU/NumPy generic
   active-query status-machine reference before native/OptiX implementation?

8. Are the minimum fields for Goal5379 sufficient:

   ```text
   query_row_id
   active_queue_index
   source_id
   current_best_sq
   status
   offload_cell_id
   miss_queue_row
   completed_nearest_row
   ```

9. Is Goal5380 correctly deferred until Goal5379 pins the generic reference
   semantics?

10. Should this direction be approved, revised, or blocked?

## Expected Answer Shape

Please answer in this form:

```text
Verdict:
  approve_goal5378_status_machine_direction
  or approve_with_required_amendments
  or revise_goal5378_direction
  or block_goal5378_due_to_genericity_or_evidence_gap

Blocking findings:
  - ...

Required amendments:
  - ...

Non-blocking notes:
  - ...

Answers to the 10 review questions:
  1. ...
  ...
  10. ...
```

## Claim Boundary To Enforce

Goal5378 may claim:

```text
The next valid implementation direction is a generic active-query /
status-machine model, or fail-closed explicit -lb.

The heavy-before-inline-prune probe is a no-go.
```

Goal5378 must not claim:

```text
explicit -lb support;
row-count parity;
same-denominator memory parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
performance parity or ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```
