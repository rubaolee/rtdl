# Phoenix V3 Spatial Topology-Stream Redo Alignment

Date: 2026-06-22
Status: `spatial_topology_stream_redo_aligned_internal_row_not_public_speedup`

This closes the Phoenix redo interpretation for the Spatial/RayJoin
topology-stream work. The retained capability is
`point_location_topology_stream`, not "RTDL beats RayJoin":

```text
generic_capability: point_location_topology_stream
app_probe: spatial_rayjoin
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
app_specific_native_engine_logic_allowed: false
```

## Retained Row

Exactly one Spatial-linked row remains in the current internal
13-row / 9-capability Phoenix surface:

```text
row_id: point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7
packet: docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json
status: default-path M7 row accepted with boundary, not release
```

The row is limited to the `br_county.cdb` self-query probe, `y_then_x` point
order, exact emitted count 47,262, repeat=50, sample=7. It is a guarded
squared-boundary plus prefilter-zero improvement inside the reusable
relation-status corrected point-location topology stream.

## Why This Stays In V3

The row closes the old missing Spatial topology-stream capability-family gap.
It has exact-count evidence, a default-on guarded predicate optimization,
fallback coverage for squared-boundary edge cases, and Claude/Codex boundary
review. Removing it would hide real M0-M149 generic engine work that belongs in
the internal Phoenix surface.

## Why This Does Not Release V3

The serious same-hardware V2.14 vs Phoenix V3 paired run still controls the
major-version release decision:

```text
same_metric_comparison_count: 52
overall_geomean_v3_speedup_vs_v2_14: 1.0117790403434224
apps_with_geomean_gt_1_05: 1
apps_with_geomean_lt_0_95: 2
release_consideration_eligible: false
```

Those facts mean the Spatial row cannot be turned into a broad V3 claim. It
remains internal release-surface evidence only.

## Evidence Boundary

The default path clears the same-dataset RayJoin author Query timer as a
timing bar:

```text
exact_emitted_count: 47262
default_path_median_ms: 1.0805986821651459
default_path_worst_ms: 1.083526760339737
author_query_ms: 1.86566
default_path_speedup_vs_author_query_timer: 1.7265058997313072
default_path_speedup_vs_disable_control: 5.371926183589535
author_result_count_parity_verified: false
author_result_count_printed: false
```

Because the author run did not print result count, the author Query timer is a performance bar,
not same-result public proof. This is why public Spatial
speedup, RayJoin paper reproduction, and `RTDL beats RayJoin` wording stay
blocked.

## Historical No-Go Kept As Warning

The earlier hotpath no-go remains important:

```text
previous_hotpath_status: spatial_rayjoin_hotpath_probe_no_go_author_gap_not_closed
best_older_legal_rtdl_query_ms: 5.406518
author_query_ms: 1.86566
device_filtered_observed_count: 47570
expected_exact_count: 47262
device_filtered_route_rejected: true
```

The later guarded squared-boundary default path supersedes the no-go only for
one internal row. It does not revive route-mixed timing, over-counting
device-filtered routes, or public RayJoin claims.

## Gap-1 Boundary

This row does not complete Gap 1. It proves one generic point-location
topology-stream predicate optimization in a default path, but it does not prove
that the productized prepared execution/session runner executes across
multiple Set-A probes.

For the next all-app scorecard, Spatial can be a Set-A probe only if the
productized topology/point-location execution path is the measured source of
the win and exactness remains stable. Public RayJoin author comparisons require
separate result-count and paper-scope proof. Classification must be frozen
before the run.

## Forbidden Readings

- Do not claim RTDL beats RayJoin.
- Do not claim Spatial RayJoin is publicly accelerated.
- Do not claim RTDL reproduces the RayJoin paper.
- Do not claim the default-path row authorizes public speedup wording.
- Do not revive the device-filtered 47,570-count route.
- Do not claim the author Query timer alone proves same-result RayJoin parity.
- Do not claim the Spatial row proves broad V3-over-V2.x speedup.
- Do not claim the Spatial row completes Gap 1.

## Next

Keep the topology-stream row in the current internal surface. Do not spend
Phoenix time on Spatial/RayJoin public speedup wording unless author
result-count parity and paper-scope requirements are separately proven. If
Spatial is used next, productize the generic point-location topology stream
through the prepared execution/session runner and measure it as a Set-A route.

## Goal-Level Decision Audit

Decision: close Spatial topology_stream for Phoenix redo as one retained
internal point_location_topology_stream row, not as public Spatial/RayJoin
speedup or V3 release evidence.

1. Was I foolish?

   No. The decision keeps the reviewed default-path row while explicitly
   preserving the author-result-count and public-claim blockers.

2. If yes, what actions made the decision foolish?

   It would be foolish to turn the default-path timing bar into
   `RTDL beats RayJoin` wording, ignore the author result-count parity gap, or
   revive over-counting device-filtered routes.

3. Was there another path?

   Demote Spatial entirely because earlier hotpath probes failed. That would
   hide the later guarded squared-boundary default-path evidence and reopen a
   solved capability-family gap.

4. Can I now try a different path?

   Retain exactly one internal topology-stream row, document the public-claim
   blockers, and only count future Spatial work if it lands in a shared
   productized topology runner.
