# Codex 2-AI Refresh Consensus - Phoenix V3 M7 Packet After Hausdorff

Date: 2026-06-21

## Verdict

The Phoenix V3 M7 classification packet has been refreshed after the
Claude-approved Hausdorff threshold-summary P0 repair. The packet now records
five M7-qualified row-scoped rows and remains not release authorization.

This consensus is based on:

- Claude final review:
  `docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_p0_repair_final_review_2026-06-21.md`
- Codex Hausdorff consensus:
  `docs/reviews/codex_phoenix_v3_hausdorff_threshold_summary_p0_repair_2ai_consensus_2026-06-21.md`
- Updated packet:
  `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`
  and `.json`.

## Updated Counts

```text
Phoenix M7-qualified release rows: 5
route_map_m7_qualified_release_rows: 4
supplemental_m7_qualified_release_rows: 1
blocked_or_internal_rows: 15
row_scoped_public_claim_rows: 5
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Newly Promoted Row

```text
candidate_row_id: hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped
generic_capability: threshold_summary
app_id: hausdorff_xhd
comparison_group: hausdorff_threshold_copies_262144
```

Allowed wording stays exactly row-scoped:

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

## Remaining Queue

Only `collision_flag_stream` remains in the optimization-required reopen queue.
Its blocker is still wall/probe-reference/setup dominance, so hot-tail speedup
alone must not be promoted.

## Goal-Level Decision Self-Audit

Decision: refresh the classification packet after Hausdorff enters as exactly
one row-scoped M7 row.

1. Was I foolish?

   No. The refresh follows external review, Codex consensus, updated docs, and
   tests rather than unilateral promotion.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would have been leaving public docs at
   four rows while the generated packet counted five.

3. Was there another path?

   Yes. Keep Hausdorff blocked until a second GPU repeats it. That is more
   conservative but stricter than Claude's final approved row-scoped boundary.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep the new row machine-checked, then continue Phoenix V3 on the
   remaining generic blocker: collision wall-accounting/setup dominance.
