# Phoenix V3 M31 Prepared-Session Family Audit Inventory

Date: 2026-06-23

Status: `prepared_session_family_step3_inventory_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
```

## Inventory Method

After adding the shared M31 audit helper, Codex performed a static inventory of
`src/rtdsl/prepared_execution.py` to identify which prepared-session families
set the Step-3 metadata needed by `audit_prepared_execution_session_metadata`:

- `runtime_trunk_executes_end_to_end`;
- `internal_device_residency_between_rtdl_phases`;
- `hot_path_host_materialization`;
- `continuation_contract`;
- `productized_execution_path`.

This inventory is not a performance run and does not replace per-route POD
evidence. It identifies which families can participate in the new shared audit
contract without additional metadata work.

## Static Family Coverage

| Family helper | Step-3 fields present? | Current interpretation |
| --- | --- | --- |
| `run_fixed_radius_count_threshold_3d_self_query_prepared_session` | no | Base fixed-radius self-query runner; needs Step-3 metadata if promoted as a Set-A family |
| `run_fixed_radius_threshold_reached_count_2d_prepared_session` | yes | Threshold-summary route has explicit trunk/residency/no-host fields |
| `run_fixed_radius_ranked_summary_3d_prepared_session` | yes | RTNN-style ranked-summary route has explicit trunk/residency/no-host fields |
| `run_aabb_index_query_2d_range_intersection_prepared_session` | no | AABB range-intersection helper lacks Step-3 residency audit fields |
| `run_aabb_index_query_2d_count_prepared_session` | no | AABB count helper lacks Step-3 residency audit fields; currently Set-B/control-sensitive |
| `run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session` | no | LibRTS-style OptiX prepared query-set count helper lacks Step-3 metadata; Set-B/control-sensitive |
| `run_radius_graph_component_signature_3d_prepared_session` | yes | RTDBSCAN component-signature route has explicit trunk/residency/no-host fields, but prior POD result was parity not material |
| `run_point_location_topology_stream_prepared_session` | yes | RayJoin point-location route has explicit fields, but prior POD result was not material |
| `run_segment_intersection_topology_stream_prepared_session` | yes | Segment-intersection topology route has explicit fields |
| `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` | yes | Barnes-Hut aggregate-tree/fused-vector route has explicit fields; M29 boundary still applies |
| `run_ray_triangle_weighted_summary_device_output_stream_prepared_session` | yes | Triangle weighted-summary device-output route has explicit fields and accepted focused probe evidence |

## Engineering Read

The current engine is no longer a pure skeleton: multiple Set-A families expose
the Step-3 metadata. The remaining weakness is that this is not yet uniformly
enforced across all helpers, and some helpers still look like base runner
wrappers rather than fully audited residency/continuation nodes.

The strongest next Step-4 candidates are:

1. `fixed_radius_ranked_summary_3d` because RTNN M30 is the pending second
   Set-A family under post-M22/M29 review.
2. `ray_triangle_weighted_summary_device_output_stream` because Triangle has
   accepted focused evidence and already avoids hot-path scalar materialization.
3. `radius_graph_component_signature_3d` because it is the right continuation
   shape for RTDBSCAN, even though the current measured result is parity.

Do not spend more time trying to make AABB count rows into Set-A proof. They
are useful control/Set-B evidence and LibRTS watch rows, but they are not the
main residency/continuation lever.

## Negative Control Enforcement

M32 adds route-level negative assertions for the families that currently run
through the prepared-session runner but do not report the Step-3/Step-4 facts:

- base fixed-radius self-query: blocked Set-A seed;
- AABB range-intersection rows: blocked Set-B control;
- AABB native query-handle counts: blocked Set-B control;
- OptiX AABB prepared-query-set counts: blocked Set-B control.

Those helpers are allowed to keep `runtime_executed=true` as a runner-call fact.
They are not allowed to pass `accept_step3_ready` or
`accept_step4_continuation_core_ready` until real residency, no-hot-host-stage,
runtime-trunk-family, continuation-contract, and focused-gain-gate evidence is
present.

The three AABB helpers are additionally marked in code as
`set_a_probe_candidate=false` and `set_b_control_candidate=true`, matching the
M27 LibRTS/AABB Set-B triage.

## Evidence Generator Follow-Up

M31 also wires the shared audit payload into future focused evidence packets for
six Step-2/Step-3 families:

- RTNN repeat50 runner packet:
  `scripts/v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py`
  writes `runner_step3_audit` and fails serious packets when
  `runner_step3_residency_default_ready` is false.
- Triangle focused runner packet:
  `scripts/v3_phoenix_triangle_runner_m18_pod_ab.py` writes `step3_audit` on
  the runner variant plus `runner_step3_audit` in the summary, and fails
  non-dry-run packets when Step-3 readiness is false.
- Barnes-Hut focused runner packet:
  `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py` writes per-row
  `step3_audit` fields, summarizes `runner_step3_audit_rows`, and requires
  `runner_step3_residency_default_ready_all_samples` before a Step-1
  replacement candidate can pass.
- RTDBSCAN M3.4 repeated-runner packet:
  `scripts/v3_phoenix_rtdbscan_runner_m3_4_pod_ab.py` writes per-row
  `step3_audit` fields and summarizes
  `runner_step3_residency_default_ready_all_runner_samples`, while preserving
  the existing no-material-gain/no-release interpretation.
- RayJoin point-location focused runner packet:
  `scripts/v3_phoenix_rayjoin_point_location_runner_pod_ab.py` writes per-row
  `step3_audit` fields and summarizes `runner_step3_audit_rows`, while keeping
  material status gated by same-contract legacy-over-runner speedup plus audit
  readiness.
- Hausdorff threshold focused runner packet:
  `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py` audits both
  directed legs exposed by
  `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`,
  writes `step3_audit`, `step3_audit_status`, `step3_audit_missing_fields`,
  and `step3_residency_default_ready`, and preserves the existing no-release
  boundary.

Older evidence generated before M31 does not contain the new audit payload. It
must not be retroactively rewritten; if a rerun is authorized later, the new
payload will be produced by the scripts.

In addition to those six focused packet generators, the generic
`run_segment_intersection_topology_stream_prepared_session` helper now has a
route-level `runtime_audit()` assertion in
`tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`. This is
a core-helper contract check, not POD evidence and not a speed claim.

## Next Work

1. Use the audit helper in future route reports so every focused probe reports
   `step3_residency_default_ready` or a concrete missing-field list.
2. Add route-level audit assertions for RTNN, Triangle, Barnes-Hut, RTDBSCAN,
   RayJoin, and Hausdorff evidence tests where those tests already inspect
   final metadata.
3. Retry Claude M30 review when Claude is available.

## Goal-Level Decision Audit

Decision: treat M31 inventory as a Step-3 enforcement map, not as a performance
result.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be to equate static field presence with benchmark
   speedup. This inventory explicitly avoids that.

3. Was there another path?

   Yes: keep working from old prose notes. That would allow more route-specific
   drift and make it harder to see which families are truly runner-auditable.

4. Can I now try a different path that actually solves the problem?

   Yes. Use the shared audit fields to drive Step 4 continuation-core work and
   require future focused probes to expose missing residency/accounting facts.
