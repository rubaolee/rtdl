# Goal3808 Remaining Low-Risk Alias Cleanup

Date: 2026-06-07

## Purpose

Goal3806 inventoried the remaining active example helper names that still carry
historical version labels. Goal3808 handles the two low-risk app-facing
candidates from that inventory without removing the legacy names:

- Contact Manifold bounded witness descriptor:
  `describe_v2_4_bounded_witness_session` now has the current alias
  `describe_bounded_witness_session`.
- LibRTS spatial-index primitive-first plan:
  `v2_5_plan_payload` now has the current alias
  `primitive_first_plan_payload`, and the CLI exposes
  `--mode primitive_first_plan`.

The RayJoin `run_rayjoin_v2_9_numba_side_aware_topology_reference` helper is
not migrated in this goal. That name still marks a bounded topology-reference
lane rather than a promoted public route.

## Operations

| Area | Legacy name preserved | Current alias added | Contract effect |
| --- | --- | --- | --- |
| Contact Manifold | `describe_v2_4_bounded_witness_session` | `describe_bounded_witness_session` | Same generic bounded int64 witness-row descriptor; alias metadata records both names. |
| LibRTS spatial index | `v2_5_plan_payload` | `primitive_first_plan_payload` | Same prepared generic AABB index plan; alias metadata records both names and the current CLI mode. |

## Boundary

- No native engine code changed.
- No old compatibility helper was removed.
- No paper reproduction, release, package-install, true-zero-copy, public
  speedup, broad RT-core speedup, or app-specific native-engine claim is
  authorized.
- Historical protocol names and artifact keys remain stable.

## Validation

- Local Windows targeted tests:
  `tests.goal3808_remaining_low_risk_alias_cleanup_test`,
  `tests.goal3806_active_example_versioned_helper_inventory_test`,
  `tests.goal2659_v2_4_benchmark_protocol_integration_test`, and
  `tests.goal2736_tier_a_primitive_first_plan_alignment_test`.
- A5000 pod validation should run the same focused slice from a clean
  `origin/main` checkout after the commit lands.
