# Call For Review: Phoenix V3 M9 Spatial LSI OptiX Mechanics Intake

Date: 2026-06-22
Status: `pending_external_review_not_release`

This packet asks for a critical review of the M9 local mechanics intake for
the remaining Spatial/RayJoin LSI OptiX active loss. It does not authorize
release, public speedup wording, implementation, focused POD, or all-app POD.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized: false
full_all_app_pod_spend_authorized: false
implementation_authorized_by_this_packet: false
```

## Review Inputs

- M9 JSON:
  `docs/rebuild/v3/phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.json`
- M9 report:
  `docs/reports/phoenix_v3_spatial_lsi_optix_m9_intake_2026-06-22.md`
- M8 blocker queue:
  `docs/rebuild/v3/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.json`
- Relevant app route:
  `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- Productized runner code:
  `src/rtdsl/prepared_execution.py`

## M9 Intake Summary

Target row:

```text
goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048
```

Observed facts:

- V2.14: `0.00012254714965820312s`
- Current Phoenix V3: `0.0001379847526550293s`
- V3/V2 speedup: `0.8881209503239741x`
- Absolute delta: `15.437602996826172` microseconds slower
- Metric basis: both use `phases_sec.prepared_query_sec`
- Current route:
  `prepared_optix_left_id_dense_count_prepared_left_reuse`
- Payload has no `productized_execution_path`
- Payload has no `prepared_execution_session_runner`
- Payload has no `topology_stream_prepared_handle`
- Existing productized Spatial runner is PIP/point-location only.
- No productized `segment_intersection_topology_stream` prepared-session runner
  exists in `src/rtdsl/prepared_execution.py`.
- Current OptiX is not slow against current Embree in this group; the sanity
  ratio is `387.483x`, but it mixes `elapsed_sec` and
  `phases_sec.prepared_query_sec`, so it is not public speedup evidence.

M9 proposed interpretation:

The active row is a local V3-vs-V2 micro-regression and productization gap,
not an OptiX failure and not a reason to tune RayJoin-specific paper logic.
The next legitimate V3 action, if accepted, is an M10 candidate to productize
a generic `segment_intersection_topology_stream` prepared-session wrapper
around the existing RTDL-owned device-resident LSI pieces, then seek focused
POD only after code exists and another review authorizes it.

## Questions For Reviewer

1. Is M9 correct that this row should not be described as "OptiX is slow"?
2. Is M9 correct that immediate POD spend is premature because the payload
   already shows the active row bypasses the shared productized runner?
3. Is `segment_intersection_topology_stream` productization a legitimate V3
   runtime-trunk target rather than RayJoin app-specific tuning?
4. Does the 15.4 microsecond absolute delta weaken the case for speed-first
   work here enough that M10 should be evidence/contract-first?
5. Are there missing local facts that must be collected before M10 begins?
6. If M10 is allowed, what is the smallest implementation that proves the
   shared runtime trunk executes without turning this into app development?

## Requested Verdict Labels

Choose exactly one:

- `approve_m9_enter_m10_no_pod`: accept M9 and allow local M10 implementation
  planning only; POD remains blocked.
- `approve_m9_but_retarget`: accept the facts but choose a different next
  local target.
- `revise_m9_before_m10`: require more local evidence or corrections before
  any M10 work.
- `reject_m9`: M9 interpretation is wrong.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- focused POD authorization: yes/no
- all-app POD authorization: yes/no
- whether M10 may implement a generic productized
  `segment_intersection_topology_stream` prepared-session route

## Goal-Level Decision Audit

Decision: request external review before M10 implementation or POD.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish move would be to burn POD or edit runtime after only noticing
   a 0.888x ratio, without recording that it is a 15 microsecond V3/V2 row
   outside the productized runner.
3. Was there another path?
   Yes: jump straight into a rerun. That would spend user money before fixing
   the route classification.
4. Can I now try a different path?
   Yes: ask review to authorize or redirect a tiny M10 local implementation
   path for a shared LSI runtime trunk.
