# Phoenix V3 M9 Spatial LSI OptiX Mechanics Intake

Status: `m9_spatial_lsi_optix_mechanics_intake_not_release_not_pod`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized: false
full_all_app_pod_spend_authorized: false
implementation_authorized_by_this_packet: false
```

## Target Row

- Row: `goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048`
- Command: `python3 examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py --workload lsi --execution-route prepared_optix_left_id_dense_count --result-mode count --dataset derived/authored_lsi_crossing_tiled_x2048 --no-rows --repeat 5 --warmup 1`
- V2.14 sec: `0.000122547150`
- Current Phoenix V3 sec: `0.000137984753`
- V3/V2 speedup: `0.888121x`
- Absolute delta: `15.438` microseconds slower
- Metric source: `phases_sec.prepared_query_sec`

This row is a V3-vs-V2 regression row, not an OptiX-vs-Embree result.
Current OptiX is `387.483x`
over the current Embree row in the same comparison group, but that sanity
ratio mixes `elapsed_sec` and
`phases_sec.prepared_query_sec` and is not a public speedup claim.

## Route Finding

- Workload: `lsi`
- Execution route: `prepared_optix_left_id_dense_count_prepared_left_reuse`
- Productized execution path: `None`
- `prepared_execution_session_runner` present: `false`
- `topology_stream_prepared_handle` present: `false`
- App-layer wrapper: `PreparedRayJoinOptixCompactGroupedCountSegments.run_packed_left_dense_count`

## Productized Runner Gap

- Point-location topology-stream runner exists:
  `true`
- Segment-intersection topology-stream runner exists:
  `true`
- Existing productized Spatial runner scope:
  `PIP point-location only`
- Current LSI route scope:
  `app-layer prepared-left dense left-id count wrapper`

LSI has useful RTDL-owned device-resident pieces, but the measured active loss row does not enter the shared prepared_execution_session_runner and emits no topology_stream_prepared_handle. If current code now contains a segment_intersection_topology_stream runner, that is M10 follow-up work; it does not retroactively change the frozen M9 active row payload. The V3 trunk gap is generic segment_intersection_topology_stream productization, not RayJoin-specific paper tuning.

## Candidate Next Work

- `m10_segment_intersection_topology_stream_prepared_session`: Add a productized prepared-session wrapper for the existing LSI generic segment-pair left-id count route, mirroring the point-location runner metadata and residency gates.
- `m10_metric_hygiene_repeat_stability`: After a productized LSI route exists, run a focused repeat-stability probe on the same RT hardware before any all-app spend.
- `reject_rayjoin_specific_native_tuning`: Do not add RayJoin-only native logic or paper-specific shortcuts to make this row green.

## Checks

Failed checks: `none`

| Check | Pass |
| --- | --- |
| `target_row_found` | `true` |
| `v2_v3_same_metric_source` | `true` |
| `target_is_microsecond_delta` | `true` |
| `payload_not_productized_runner` | `true` |
| `payload_has_no_topology_stream_handle` | `true` |
| `point_location_runner_exists` | `true` |
| `active_payload_not_productized_even_if_current_code_has_runner` | `true` |
| `segment_intersection_runner_current_state_recorded` | `true` |
| `pip_productized_runner_blocks_lsi` | `true` |
| `lsi_app_layer_device_residency_exists` | `true` |
| `not_an_optix_vs_embree_slowdown` | `true` |
| `old_docs_already_point_to_reusable_runner_gap` | `true` |

## Goal-Level Decision Audit

Decision: Treat Spatial/RayJoin LSI OptiX as a local mechanics intake and candidate productized segment-intersection trunk item, not as immediate POD work.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish path would be to call this an OptiX failure, burn POD rerunning a 15-microsecond delta, or tune RayJoin-specific code before checking whether the shared runtime trunk is even executing.
3. Was there another path?
   Yes: jump straight to a focused POD run. That would be premature because the payload already shows the row bypasses the productized runner.
4. Can I now try a different path?
   Yes: first productize or explicitly reject a generic segment_intersection_topology_stream prepared-session route, then seek 2-AI review before focused POD.
