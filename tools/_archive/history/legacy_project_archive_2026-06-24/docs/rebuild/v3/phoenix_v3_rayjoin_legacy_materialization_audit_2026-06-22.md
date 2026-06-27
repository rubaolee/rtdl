# Phoenix V3 RayJoin Legacy Materialization Audit

Date: 2026-06-22
Status: `rayjoin_materialization_audit_complete_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized: false
```

## Decision

RayJoin is a valid next Phoenix V3 family only as a
`point_location_topology_stream` runtime-family probe. It is not a
whole-app target and it does not authorize pod spend yet.

Recommended next probe: `pip_relation_status_corrected_executor_through_prepared_execution_runner`

Productize the existing point_location_topology_stream relation-status corrected scalar-count route through the shared prepared execution/session runner. Do not present this as full RayJoin.

## Route Assessment

| Route | Source | V3 Source Exists | Immediate Probe | Reading |
| --- | --- | ---: | ---: | --- |
| `pip_exact_prepared_points` | host_candidate_download_and_host_exact_refine | true | false | It has a host boundary, but it is also the validation authority path. It should not be used as a speed claim without a validated device replacement. |
| `pip_relation_status_corrected_executor` | device_resident_scalar_count_executor | true | true | This is the cleanest RayJoin topology-stream candidate to productize through the prepared execution runner. |
| `lsi_default_count` | host_packed_left_exact_count | true | false | A better LSI route already exists through prepared-left/dense device columns, so this is a baseline source, not the next trunk target. |
| `lsi_dense_left_id_count` | device_resident_left_id_count_column | false | false | The current hot route already removed the host boundary; wrapping it alone risks another RTDBSCAN-like parity result. |
| `overlay_active_count_device_continuation` | device_resident_shape_pair_active_count_executor | false | false | The current hot route is already device-continuation based; it is a later generalization target, not the first material probe. |

## Pod Decision

No pod yet. First add local runner metadata/tests and confirm the comparison basis: runner-vs-legacy/current-legacy path for productization credit, and V3 runner vs V2.14 for release-score evidence.

## Checks

- `default_lsi_host_left_route_present`: `true`
- `pip_partial_host_refine_boundary_recorded`: `true`
- `pip_relation_status_device_executor_present`: `true`
- `lsi_dense_device_column_route_present`: `true`
- `overlay_device_continuation_route_present`: `true`
- `claim_boundaries_present`: `true`

## Goal-Level Decision Audit

Decision: Use RayJoin only as a point-location topology-stream family candidate, not as a full-app pod target.

1. Was I foolish?
   No. This avoids direct pod spend before identifying where a real host-boundary source exists.
2. If yes, what actions made the decision foolish?
   It would be foolish to run full RayJoin or quote old large OptiX-over-Embree ratios without separating host-boundary sources from routes that are already device resident.
3. Was there another path?
   Run the RayJoin pod immediately. That would be faster administratively, but likely repeats RTDBSCAN's failure mode if the selected hot route already removed the host boundary.
4. Can I now try a different path that actually solves the problem?
   Productize one topology-stream route through the shared runner first, then spend pod time only on a focused runner-vs-legacy comparison.

## Non-Authorization

This audit authorizes no release, no public speedup wording, no broad
V3-over-V2.x wording, no true-zero-copy wording, no external embedding
wording, and no pod spend. Release remains `redo_required`.
