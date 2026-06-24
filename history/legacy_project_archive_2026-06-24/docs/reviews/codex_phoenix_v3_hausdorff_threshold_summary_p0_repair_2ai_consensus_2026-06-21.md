# Codex 2-AI Consensus - Phoenix V3 Hausdorff Threshold-Summary P0 Repair

Date: 2026-06-21

## Verdict

Consensus complete: Claude + Codex approve exactly one row-scoped M7
classification for the large Hausdorff threshold-summary row, subject to the
strict final wording below.

This does not authorize V3 release, broad V3-over-V2 claims, full Hausdorff
claims, X-HD paper-reproduction claims, all-scale claims, all-threshold claims,
or all-GPU claims.

## Evidence

Primary packet:

```text
docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.json
```

Artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_repeat5_20260621/summary.json
docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_large_stability_20260621/summary.json
```

External reviews:

```text
docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_repeat5_m7_review_2026-06-21.md
docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_p0_repair_final_review_2026-06-21.md
```

The first Claude review approved conditionally but blocked on missing stability
data and missing oracle definition. The repaired packet closes both P0s:

- five independent paired process samples for the large row;
- all five phase-total ratios above 1x;
- weakest phase-total speedup: 1.2243669013234328x;
- phase-total ratio mean/stddev: 1.240042444838897 / 0.01179874030631055;
- deterministic `expected_tiled_hausdorff(copies=N)` oracle definition;
- prepared-mode timing disclosure that phase-total includes scene preparation.

## Approved Row

```text
generic_capability: threshold_summary
candidate_row_id: hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped
app_id: hausdorff_xhd
comparison_group: hausdorff_threshold_copies_262144
points_per_side: 1048576
threshold: 0.4
backend_pair: OptiX directed_threshold_prepared vs Embree directed_threshold_prepared
hardware: single RTX 4000 Ada pod
independent_paired_samples: 5
inner_repeat_warmup: 5 / 1
m7_promotion_authorized: true
row_scoped_public_speedup_claim_authorized: true
release_authorized: false
```

## Exact Allowed Wording

```text
RTDL V3 includes a generic Hausdorff threshold-summary route where, at
1,048,576 points per side and threshold 0.4 on a single RTX 4000 Ada pod,
prepared OptiX fixed-radius threshold decisions beat the same-contract Embree
route across five independent paired process samples: query speedup mean
1.639x, phase-total speedup mean 1.240x (phase-total includes scene
preparation), weakest phase-total speedup 1.224x, with repeat=5/warmup=1
inside each sample. Smaller rows in the same rerun are query wins but not
phase-total wins.
```

## Forbidden Wording

```text
RTDL computes full Hausdorff faster.
Hausdorff V3 is faster end to end.
X-HD is reproduced.
V3 is faster than V2.
OptiX is faster for all Hausdorff scales.
OptiX is faster for all threshold values.
OptiX is faster for all RTX GPUs.
OptiX beats Embree at the 65,536-point or 262,144-point scale end to end.
The threshold-summary route is faster for all input sizes.
Phase-total speedup is X without counting scene preparation.
```

## Non-Blocking Notes To Preserve

- Oracle correctness evidence covers the positive threshold case for this
  fixture and threshold. It does not independently prove the negative threshold
  branch.
- The five stability samples were run sequentially on one pod. The final
  wording therefore says "single RTX 4000 Ada pod" and must not become a
  general RTX claim.
- The row is threshold-summary only; it is not exact Hausdorff distance or
  witness materialization.

## Goal-Level Decision Self-Audit

Decision: promote exactly one large Hausdorff threshold-summary row into the M7
classification packet after Claude P0 repair approval and Codex consensus.

1. Was I foolish?

   No. The first review blocked promotion; I repaired the evidence instead of
   overriding it. The final claim uses the conservative stability rerun, not
   the more flattering single-run number.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would have been to promote the earlier
   query-only or single-run 1.264x result without stability and oracle
   definition.

3. Was there another path that would have avoided getting stuck on that idea?

   Yes. I could have left Hausdorff blocked and moved to collision flags. That
   would be safe, but it would ignore evidence that is now strong enough under
   row-scoped boundaries.

4. Can I now try a different path that actually solves the problem?

   Yes. Update the generated M7 classification packet, docs, wording gate, and
   tests so the row is machine-checked under this exact boundary.
