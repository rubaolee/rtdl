# Call For Review: Phoenix V3 Spatial Active-P0 Closure Decision

Status: external review request, not a release approval.

Please critically review whether Phoenix V3 should keep
`spatial_rayjoin_topology_stream_author_gap` as an active P0 generic-engine item,
or close it as a no-go / future-research item for the current V3 release surface.

This is a product-quality and engineering-discipline question. A useful answer
may be negative. Do not approve broad V3, whole Spatial RayJoin, RayJoin-paper,
RTDL-beats-RayJoin, zero-copy, or release wording.

## Files To Review

- Current active queue:
  `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- Exact-f64 intake:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md`
- Exact-f64 review gate:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md`
- Same-dataset author timing basis:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.md`
- Adverse subset parity packet:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.md`
- Prior relation-status no-go:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.md`
- M3 gap analysis:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`
- M7 feasibility packet:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md`
- Current M7 row classification:
  `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`
- Release readiness gate:
  `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`

## Current Facts To Check

- Spatial RayJoin has no M7-qualified row in the current Phoenix packet.
- The exact-f64 device scalar-count repair is real internal generic-engine
  progress: it restores exact public-county parity at `47,262` rows and improves
  RTDL prepared-query median versus the prior exact executor by `3.680x`.
- The same-dataset RayJoin author Query timer is `1.865660 ms`; the current RTDL
  exact-f64 prepared-query median is `6.309319 ms`, so RayJoin author Query is
  about `3.382x` faster on that timing basis.
- `query_exec` did not print a RayJoin author result count in the same-dataset
  timing run, so author count parity is not verified there.
- A smaller adverse-subset parity packet passes, but that is not enough for M7.
- External review for the exact-f64 intake is currently blocked/missing.
- Current release readiness is `blocked_not_release`, partly because the generic
  engine work queue is open.

## Review Questions

1. Should `spatial_rayjoin_topology_stream_author_gap` stay active P0 for
   Phoenix V3, or should it be closed for current V3 as no-go/future research?
2. Is closing it now honest if the closure says: "real generic progress, no M7
   row, no RTDL-beats-RayJoin claim, reopen only after new RTX evidence beats
   same-dataset author timing or a reviewer explicitly accepts a weaker scope"?
3. Would closure make V3 more user-responsible by preventing endless Spatial
   work, or would it prematurely abandon a required V3 capability?
4. If closure is acceptable, what exact blockers and reopen conditions must be
   machine-recorded?
5. If closure is not acceptable, what single next generic-engine optimization
   should be attempted first, and what evidence would prove it is worth keeping?
6. Are there any claim-boundary risks in the proposed closure?

## Required Verdict Format

Please return exactly these sections:

- `verdict`: close-active-p0 / keep-active-p0 / reject-current-record
- `rationale`: short paragraph
- `must_record_if_closed`: bullet list
- `must_do_if_kept_active`: bullet list
- `claim_boundary_risks`: bullet list
- `recommended_next_action`: one paragraph

Be strict. The purpose is to protect users from a V3 release story that hides
negative evidence.
