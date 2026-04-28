# Goal1061 Event Hotspot Public Wording Packet

Date: 2026-04-28

## Boundary

This packet prepares one candidate public RTX wording line for external review.
It does not edit public docs, authorize release, or authorize broad/whole-app
speedup claims.

## Source Evidence

| Field | Value |
| --- | --- |
| App/path | `event_hotspot_screening / prepared_count_summary` |
| Source audit | `docs/reports/goal1060_post_goal1058_speedup_candidate_audit_2026-04-28.json` |
| Artifact | `docs/reports/goal1052_post_goal1048_cloud_batch/prepared_count_summary.json` |
| RTX phase key | `scenario.timings_sec.optix_query` |
| RTX phase | `0.16599858924746513` s |
| Fastest same-semantics baseline | `embree_summary_path` |
| Fastest baseline phase | `0.2566157499095425` s |
| Baseline / RTX ratio | `1.5458911492734937` |
| Current public wording status | `public_wording_not_reviewed` |
| Public speedup claims authorized before this review | `0` |

The RTX phase is above the 100 ms floor used by the project wording gate, and
the ratio is above the 1.20 margin floor. Goal1060 classified this row as
`candidate_for_separate_2ai_public_claim_review`.

## Candidate Wording

On the recorded RTX A5000 Goal1058 artifact, the bounded RTDL
`event_hotspot_screening / prepared_count_summary` query phase measured
`0.165999` s and was `1.55x` faster than the fastest reviewed same-semantics
non-OptiX baseline for that prepared count-summary sub-path. This is not a
whole-app hotspot-screening speedup claim, not a default-mode claim, and not a
claim about neighbor-row output, Python-side postprocessing, validation, or
unrelated application stages.

## Reviewer Questions

- Is the wording strictly limited to the prepared count-summary query phase?
- Does the wording avoid whole-app, default-mode, broad RT-core, and
  Python-postprocess claims?
- Is the use of `1.55x` defensible from the Goal1060 ratio and source artifact?
- If accepted, should `rtdsl.rtx_public_wording_matrix()` promote only this
  event-hotspot sub-path to `public_wording_reviewed` while keeping
  `public_speedup_claim_authorized_count` gates at `0` unless separately
  changed?
