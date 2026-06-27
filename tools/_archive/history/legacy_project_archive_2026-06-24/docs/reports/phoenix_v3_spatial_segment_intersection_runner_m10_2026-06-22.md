# Phoenix V3 M10 Spatial Segment-Intersection Runner

Status: `m10_local_productized_runner_implemented_not_pod_not_release`

This implements the smallest M10 authorized by the M9 2-AI consensus:
a generic `segment_intersection_topology_stream` prepared-session route.
It is not a performance result and does not authorize POD, release, or public
speedup wording.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized: false
full_all_app_pod_spend_authorized: false
true_zero_copy_claim_authorized: false
v4_embedding_or_external_zero_copy_authorized: false
```

## What Changed

- Added
  `run_segment_intersection_topology_stream_prepared_session` in
  `src/rtdsl/prepared_execution.py`.
- Added a thin LSI app adapter
  `PreparedExecutionRayJoinSegmentIntersectionTopologyStream` in
  `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`.
- Added CLI route:
  `--execution-route prepared_execution_segment_intersection_topology_stream`.
- Added local wiring/fake-runner tests:
  `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`.
- Updated M9 intake to remain reproducible after M10 by separating the frozen
  active-row payload from current code state.

## Boundary

This is generic runtime-trunk work:

- Runtime primitive: `segment_intersection_topology_stream`
- Productized path: `prepared_execution_session_runner`
- Output contract:
  `segment_segment_intersection_count_by_left_id_dense_device_column`
- Existing native pieces reused:
  `prepare_segment_pair_intersection_optix`,
  `pack_rayjoin_optix_compact_grouped_count_left_segments`,
  `left_id_count_prepared_left_device_columns`

Not done:

- No native algorithm change.
- No RayJoin paper-specific shortcut.
- No public speedup claim.
- No focused POD run.
- No all-app POD run.

## Local Gates

Passed:

```text
py -3 -m unittest tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test tests.v3_phoenix_rayjoin_prepared_execution_runner_wiring_test tests.v3_phoenix_spatial_lsi_optix_m9_intake_test
```

Result: `Ran 9 tests ... OK`

Passed:

```text
py -3 examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --help
```

Result: the new route appears in `--execution-route` choices. This is only a
CLI mount check, not a GPU performance run.

## What This Solves

M9 found that the frozen active row:

```text
goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048
```

was a V3-vs-V2 micro-regression outside the productized runner. M10 gives that
family a productized runner path so future evidence can come from the V3
runtime trunk instead of an app-layer loop.

## What It Does Not Prove

M10 does not prove Phoenix V3 is faster than V2.x. It does not prove this route
is faster than the old LSI route. It only makes the correct productized route
exist locally and makes its metadata/claim boundaries testable.

## Next Review Question

Should M10 be accepted as a local productized-runner implementation and
authorized for one focused same-RT-hardware POD A/B against the old LSI route,
or must more local evidence be collected first?

## Goal-Level Decision Audit

Decision: Implement the smallest local generic segment-intersection
topology-stream prepared-session route after M9 2-AI approval.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish actions would be to change native algorithms, tune RayJoin
   paper-specific behavior, or call this a performance win without POD
   evidence.
3. Was there another path?
   Yes: continue documentation-only analysis or burn POD immediately. Both
   would leave the productized-runner gap unresolved or spend money before the
   route existed.
4. Can I now try a different path?
   Yes: request 2-AI review of M10 and only then consider a focused POD A/B.
