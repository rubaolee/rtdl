# Codex + Heisenberg 2-AI Consensus: Phoenix V3 M9 Spatial LSI OptiX

Date: 2026-06-22
Status: `approve_m9_enter_m10_no_pod`

Review request:
`docs/reviews/call_for_review_phoenix_v3_m9_spatial_lsi_optix_mechanics_intake_2026-06-22.md`

M9 intake:

- JSON:
  `docs/rebuild/v3/phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.json`
- Report:
  `docs/reports/phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.md`

## Consensus Verdict

Codex and Heisenberg agree:

- The `0.8881209503239741x` row is a V3-vs-V2 OptiX-route
  micro-regression of about `15.4` microseconds on the same
  `phases_sec.prepared_query_sec` metric basis.
- It must not be described as "OptiX is slow" or as an OptiX-vs-Embree
  failure.
- The current active LSI route bypasses the shared
  `prepared_execution_session_runner` and emits no
  `topology_stream_prepared_handle`.
- Immediate POD spend is not authorized.
- The smallest next legitimate M10 is local implementation of a generic
  productized `segment_intersection_topology_stream` prepared-session route,
  evidence/contract-first.

## Authorizations

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized: false
full_all_app_pod_spend_authorized: false
M10_local_implementation_authorized: true
M10_POD_authorized: false
```

## M10 Scope

Allowed:

- Add a generic
  `run_segment_intersection_topology_stream_prepared_session` wrapper in
  `src/rtdsl/prepared_execution.py`, mirroring the point-location runner's
  metadata, repeat handling, residency gates, and claim boundaries.
- Wire one thin Spatial/RayJoin LSI harness route through that wrapper using
  the existing prepared-left dense count pieces.
- Emit `productized_execution_path`, `prepared_execution_session_runner`,
  topology-stream metadata, residency flags, and claim-boundary flags.
- Add focused local contract tests.

Forbidden:

- No native algorithm changes.
- No RayJoin paper-specific shortcuts.
- No public speedup claim.
- No POD before the M10 local route exists and receives another review.

## Reviewer Notes

Heisenberg selected `approve_m9_enter_m10_no_pod` and answered:

- The row should not be described as OptiX slow.
- Immediate POD is premature because the route does not enter the shared
  runner.
- Generic `segment_intersection_topology_stream` productization is legitimate
  V3 runtime-trunk work only if it remains generic segment-pair/count-contract
  work.
- A `15.4` microsecond delta makes M10 evidence/contract-first rather than
  speed-first.
- No blocking missing local facts remain before M10.

## Goal-Level Decision Audit

Decision: accept M9 and enter local M10 implementation without POD.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish actions would be to call the row an OptiX failure, spend POD on
   a 15 microsecond delta, or tune RayJoin-specific native logic.
3. Was there another path?
   Yes: retarget another blocker or immediately rerun on POD. Both would leave
   the productized-runner gap unresolved.
4. Can I now try a different path?
   Yes: implement the smallest generic segment-intersection topology-stream
   prepared-session route locally, then seek review before focused POD.
