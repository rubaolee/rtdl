# Call For Review - Goal5366 X-HD lb Denominator Reconciliation

Please strictly review Goal5366.

## Files To Review

```text
history/internal_docs/goal5366_xhd_lb_denominator_reconciliation_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5366_lb_denominator_reconciliation.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5366_lb_denominator_reconciliation.py
tests/goal5366_lb_denominator_reconciliation_test.py
```

Useful context:

```text
history/internal_docs/goal5365_xhd_rtdl_lb_counterpart_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
history/internal_docs/goal5363_xhd_lb_heavy_offload_semantics_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5363_lb_heavy_offload_semantics_audit.json
```

## Review Questions

1. Does Goal5366 correctly distinguish byte-formula shape alignment from actual
   row-count parity?

2. Is the interpretation of author `OffloadingSize` supported by source
   evidence: raw `(in_queue_idx, cell_id)` offload queue rows accumulated across
   batches in an author iteration?

3. Is the interpretation of RTDL `heavy_offload_peak_rows` supported by source
   evidence: generic cell-MBR frontier rows with `frontier_kind_code == 2`,
   counted after native row handling?

4. Does the artifact correctly show that the current observed delta is not
   explained by RTDL duplicate collapse in the Goal5365 run, because raw
   attempted count, emitted count, and heavy offload rows are all equal?

5. Does the report correctly identify the still-unmatched route regime:
   author iterative radius/in_queue semantics versus RTDL single-pass
   full-cover frontier semantics?

6. Does Goal5366 correctly refuse to authorize explicit `-lb` support,
   row-count parity, same-denominator memory parity, Figure 7, Figure 11,
   performance ratios, or full paper reproduction?

7. Is the proposed next gate right: either author-iteration-aligned RTDL lb
   trace, or raw author-denominator telemetry in the generic native collector?

8. Are there any hidden X-HD-specific core semantics introduced by Goal5366?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5366_lb_denominator_reconciliation
or
Verdict: approve_with_required_amendments
or
Verdict: block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to the 8 review questions:
1. ...
```
