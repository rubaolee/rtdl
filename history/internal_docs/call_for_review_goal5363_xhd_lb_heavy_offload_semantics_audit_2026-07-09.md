# Call For Review - Goal5363 X-HD lb / Heavy-Cell Offload Semantics Audit

Please strictly review Goal5363.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5363_lb_heavy_offload_semantics_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5363_lb_heavy_offload_semantics_audit.json
tests/goal5363_lb_heavy_offload_semantics_audit_test.py
history/internal_docs/goal5363_xhd_lb_heavy_offload_semantics_audit_result_2026-07-09.md
```

Relevant prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5352_rt_core_feature_parity_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5282_author_offload_mapping_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5283_figure11_disposition_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
```

## Review Questions

1. Does Goal5363 correctly identify author `lb` semantics from source:
   `FLAGS_lb -> config.lb -> processing_threshold`?
2. Does it correctly record that author `lb=0` disables heavy-cell offload by
   rewriting the threshold to `UINT32_MAX`?
3. Does it correctly record that author `lb=N` offloads cells with point count
   strictly greater than `N`?
4. Does it correctly identify author offload row shape as `(in_queue index,
   cell id)` and the CUDA `loadBalanceProcessing` stage?
5. Does it correctly list author fields `RTTime`, `CUDATime`,
   `OffloadingSize`, `WL`, and `WL Heavy Peak`?
6. Does it honestly treat RTDL's `cell_point_count > max_inline_points` rule as
   only a candidate shape-aligned mapping, not explicit `-lb` support?
7. Does it correctly preserve the prior Figure 7 / Figure 11 denominator
   blockers instead of claiming reproduction?
8. Is the proposed next gate
   `bounded_lb_processing_threshold_route_trace_gate` the right next step?
9. Does it avoid app-specific RTDL core changes and keep all X-HD semantics in
   the paper app / audit layer?
10. Should Goal5363 close as
    `lb_heavy_offload_semantics_audit_ready__next_gate_bounded_lb_trace`?

## Expected Verdict Labels

Choose one:

```text
approve_goal5363_lb_heavy_offload_semantics_audit
approve_with_required_amendments
revise_goal5363_lb_heavy_offload_semantics_audit
block_goal5363_lb_heavy_offload_semantics_audit
```

## Requested Claim Boundary

Allowed if approved:

```text
RTDL has a shape-aligned generic threshold/offload asset that may become a
bounded author -lb mapping after a dedicated lb=0/lb=N trace gate.
```

Forbidden:

```text
explicit -lb support
author RT-core parity
Figure 7 reproduction
Figure 11 reproduction
same-denominator memory claim
performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```
