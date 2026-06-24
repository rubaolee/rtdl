# Phoenix V3 RTNN M112 Reconciliation Packet

Status: `rtnn_m112_reconciled_no_m7_promotion`.

This packet reconciles the earlier M104-M112 RTNN clean-target work with
the stricter Phoenix V3 M7 release bar. It is not release authorization
and it promotes zero RTNN rows.

## Bottom Line

RTNN has real generic ranked_summary engine progress, but no Phoenix M7
row is promoted from the current evidence. The small 65k raw-row ladder
has wall-time regression; the large KITTI aggregate route is strong but
blocked by tie/parity and precision/output-contract boundaries.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows from this packet: 0
```

## Evidence Reconciliation

| Evidence | Strong fact | Blocking fact | Reading |
| --- | --- | --- | --- |
| Current 65k raw summary | Hot OptiX/Embree: clustered 3.333x, shell 1.182x, uniform 1.084x | Wall ratios are all below 1.0 | Boundary evidence only. |
| M104 exact float64 KITTI same-input gate | OptiX/Embree 15.498x on 1,000,000 points | strict kth checksum mismatch; tie-stable only | Candidate needs tie policy review or repair. |
| M106 full-batch aggregate | 0.153553s hot query; 787.530x vs M104 Embree | float32, exact=false, not same-output with author RTNN | Strong engine route, not M7 today. |
| M111 partner continuation | uniform CuPy 0.082908s; clustered CuPy 2.041410s | no same-contract speed baseline | Runtime evidence, not public speed row. |

## Why No M7 Promotion

- `current_65k_raw_summary_wall_timing_regresses`
- `m104_exact_float64_has_tie_sensitive_kth_checksum_mismatch`
- `m106_fastest_full_batch_route_is_float32_and_exact_false`
- `author_same_input_comparison_is_not_same_output_contract`
- `m110_m111_partner_continuation_has_no_same_contract_speed_baseline`
- `paper_dataset_reproduction_not_authorized`
- `fresh_phoenix_m7_review_not_done_for_any_rtnn_row`

## Next M7 Paths

### rtnn_kitti_exact_tie_stable_aggregate_review

Rebuild or rerun the exact float64 same-input aggregate gate with a reviewed tie-stable equivalence policy, or repair the kth checksum mismatch.

`can_use_existing_evidence_directly: false`

### rtnn_full_batch_float32_same_contract_m7_rerun

Run a focused same-contract float32 aggregate packet with CPU/reference parity, phase/wall timing, source manifest, and 2-AI review.

`can_use_existing_evidence_directly: false`

## Queue Effect

Keep `rtnn_ranked_summary_wall_path` open, but refine it: old M112 evidence proves a large aggregate route exists, while M7 still needs tie/parity or float32 same-contract repair.

## Goal-Level Decision Audit

Decision: Reconcile RTNN M112 clean-target evidence with the Phoenix M7 bar without promoting RTNN.

1. Was I foolish?
   No. This prevents both under-reading M112 and overclaiming it as V3 release evidence.
2. If yes, what actions made the decision foolish?
   It would be foolish to use the M106 787.53x-vs-Embree figure as a public RTNN row while ignoring float32/exact=false and same-output-contract blockers.
3. Was there another path that would have avoided getting stuck on that idea?
   Declare RTNN solved from M112 or leave the wall-time regression packet alone. Either path loses key evidence.
4. Can I now try a different path that actually solves the problem?
   Keep RTNN in the engine queue with a narrower next action: exact tie-stable aggregate review or float32 same-contract rerun.
