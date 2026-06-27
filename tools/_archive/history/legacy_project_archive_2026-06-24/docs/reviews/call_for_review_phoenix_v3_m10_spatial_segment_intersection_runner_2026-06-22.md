# Call For Review: Phoenix V3 M10 Spatial Segment-Intersection Runner

Date: 2026-06-22
Status: `pending_external_review_not_release`

This packet asks for critical review of the M10 local implementation of a
generic `segment_intersection_topology_stream` prepared-session route. It does
not authorize release, public speedup wording, focused POD, or all-app POD by
itself.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_by_this_packet: false
full_all_app_pod_spend_authorized_by_this_packet: false
```

## Inputs

- M9 consensus:
  `docs/reviews/codex_heisenberg_phoenix_v3_m9_spatial_lsi_optix_2ai_consensus_2026-06-22.md`
- M10 JSON:
  `docs/rebuild/v3/phoenix_v3_spatial_segment_intersection_runner_m10_2026-06-22.json`
- M10 report:
  `docs/reports/phoenix_v3_spatial_segment_intersection_runner_m10_2026-06-22.md`
- Generic runner:
  `src/rtdsl/prepared_execution.py`
- Spatial/RayJoin harness:
  `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- M10 tests:
  `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`

## Implementation Summary

M10 adds:

- `run_segment_intersection_topology_stream_prepared_session`
- `PreparedExecutionRayJoinSegmentIntersectionTopologyStream`
- CLI route:
  `--execution-route prepared_execution_segment_intersection_topology_stream`
- Productized-runner metadata:
  `productized_execution_path`, `prepared_execution_session_runner`,
  `runtime_trunk_executes_end_to_end`, `topology_stream_prepared_handle`, and
  `topology_stream_m3_phase_table`

The implementation reuses existing generic/native pieces and intentionally
does not change native algorithms or add RayJoin paper-specific shortcuts.

Local gates passed:

```text
py -3 -m unittest tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test tests.v3_phoenix_rayjoin_prepared_execution_runner_wiring_test tests.v3_phoenix_spatial_lsi_optix_m9_intake_test
```

## Questions For Reviewer

1. Does M10 satisfy the M9 consensus scope?
2. Is the new helper generic runtime-trunk work rather than RayJoin app
   development?
3. Are claim boundaries still correct?
4. Is there any blocking local issue before a focused POD A/B?
5. Should one focused same-RT-hardware POD A/B be authorized comparing the old
   LSI route and the new productized segment-intersection route?
6. If POD is authorized, what exact guardrails should control it?

## Requested Verdict Labels

Choose exactly one:

- `approve_m10_focused_pod_ab`: accept local M10 and authorize one focused POD
  A/B only, not all-app POD.
- `approve_m10_no_pod_yet`: accept local M10, but require more local work
  before POD.
- `revise_m10_before_pod`: M10 is directionally right but needs fixes before
  review can authorize POD.
- `reject_m10`: M10 violates scope or is not a legitimate V3 runtime-trunk
  implementation.

Regardless of verdict, explicitly state:

- release authorization: yes/no
- public speedup authorization: yes/no
- focused POD authorization: yes/no
- all-app POD authorization: yes/no
- whether the implementation may be treated as productized-runner coverage for
  the Spatial/RayJoin LSI Set-A probe

## Goal-Level Decision Audit

Decision: request external review before any M10 POD spend.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish move would be to treat local route wiring as performance proof.
3. Was there another path?
   Yes: immediately run POD. That would skip the required 2-AI review.
4. Can I now try a different path?
   Yes: obtain the bounded review and only run focused POD if it is explicitly
   authorized.
