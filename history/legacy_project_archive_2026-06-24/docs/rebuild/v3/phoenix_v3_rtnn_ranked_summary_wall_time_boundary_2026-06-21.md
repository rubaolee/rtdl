# Phoenix V3 RTNN Ranked-Summary Wall-Time Boundary

Status: `rtnn_ranked_summary_wall_time_boundary_not_m7`.

This packet turns the reviewed RTNN ranked-summary intake into a V3 rebuild
tutorial boundary. It is not release evidence and not public speedup wording.

## Bottom Line

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
universal_rtnn_acceleration_claim_authorized: false
paper_reproduction_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
current_packet_external_review_status: claude_approved_after_p1_tutorial_fix
current_packet_2ai_consensus_status: claude_codex_consensus_complete_no_m7_promotion
```

The underlying intake already has Claude/Codex 2-AI consensus as reviewed
internal candidate evidence:

```text
docs/reviews/codex_phoenix_v3_rtnn_ranked_summary_intake_2ai_consensus_2026-06-20.md
```

This packet does not upgrade that status. It only makes the current teaching
surface explicit.

## Evidence

Source:

```text
docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json
```

| Distribution | Hot OptiX / Embree | Wall OptiX / Embree | Reading |
| --- | ---: | ---: | --- |
| clustered | 3.333x | 0.625x | hot signal, wall blocker |
| shell | 1.182x | 0.316x | small hot signal, wall blocker |
| uniform | 1.084x | 0.303x | marginal hot signal, wall blocker |

Wall ratios below 1.0 mean OptiX is slower than Embree. For example, 0.316x
means OptiX takes about 3.16x as long as Embree wall-to-wall. RTNN therefore
stays internal even though the hot ranked-summary metric is faster.

## Current Blockers

- `wall_timing_optix_slower_than_embree_for_all_three_distributions`
- `distribution_specific_not_universal_rtnn_acceleration`
- `paper_equivalent_rtnn_row_false`
- `summary_rows_materialized`
- `no_author_code_or_external_ann_baseline_comparison`
- `prepared_cuda_graph_replay_false`
- `no_multi_run_variance_evidence`
- `public_row_level_external_review_not_done`

## Allowed Wording

```text
RTNN ranked-summary is a V3 rebuild lesson with a distribution-specific hot
metric signal and a wall-time blocker. It is not an M7 release row.
```

## Forbidden Wording

```text
Do not claim RTNN V3 is 3.333x faster.
Do not claim V3 proves universal RTNN acceleration.
Do not claim RTDL beats Embree for RTNN end to end.
Do not claim RTNN is M7-qualified.
Do not claim ranked_summary is a paper-equivalent RTNN row.
```

## Tutorial

The current tutorial entry is:

```text
tutorials/current/11_rtnn_ranked_summary_boundary.md
```

It is a rebuild tutorial, not a release tutorial.

## External Review

The underlying RTNN intake has prior Claude/Codex consensus. Fresh external
review of this tutorial-boundary packet is now closed:

```text
docs/reviews/claude_phoenix_v3_rtnn_ranked_summary_wall_time_boundary_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2ai_consensus_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: teach RTNN as a wall-time boundary lesson, not as a performance claim.

1. Was I foolish?

   No. The prior 2-AI intake already accepts the hot signal and blocks M7
   because wall timing regresses.

2. If yes, what actions made the decision foolish?

   It would be foolish to quote the clustered 3.333x hot result without saying
   OptiX loses wall timing on all three distributions.

3. Was there another path that avoided getting stuck on that idea?

   Yes. Rerun the pod immediately, but the current user-facing gap is that the
   evidence boundary is not yet in the tutorial path.

4. Can I now try a different path that actually solves the problem?

   Yes. Add a rebuild-only RTNN lesson that makes hot metric versus wall metric
   impossible to miss.
