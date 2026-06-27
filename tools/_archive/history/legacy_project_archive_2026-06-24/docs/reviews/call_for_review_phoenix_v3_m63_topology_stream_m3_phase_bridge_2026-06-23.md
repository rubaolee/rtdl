# Call For Review: Phoenix V3 M63 Topology-Stream M3 Phase Bridge

Requested verdict label:
`accept_m63_topology_stream_m3_phase_bridge_continue_local_step2_no_pod_no_release`,
or a stricter/blocking label if warranted.

## Context

M61 recorded a phase-bridge gap: prepared execution has its own phase model,
while topology-stream public-row readiness requires the six-phase M3 table:

- `static_scene_prepare_sec`
- `query_stream_prepare_sec`
- `device_transfer_or_residency_sec`
- `rt_traversal_sec`
- `topology_continuation_sec`
- `host_return_or_scalar_materialization_sec`

M62 tightened the local contract gates but did not implement the reusable
prepared-execution-to-topology-stream phase bridge. M63 claims to implement that
bridge locally for both point-location and segment-intersection topology-stream
families.

## Files To Review

- `src/rtdsl/prepared_execution.py`
- `src/rtdsl/v3_0_topology_stream_accounting.py`
- `scripts/v3_phoenix_m61_topology_stream_gap_ledger.py`
- `docs/rebuild/v3/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`
- `tests/v3_phoenix_m61_topology_stream_gap_ledger_test.py`
- `docs/reports/phoenix_v3_m63_topology_stream_m3_phase_bridge_2026-06-23.md`

## Questions

1. Is `_topology_stream_m3_bridge_metadata` a reusable runtime-runner bridge,
   not app-specific Spatial/RayJoin tuning?
2. Does it correctly build or validate `topology_stream_m3_phase_table_v1` and
   `topology_stream_prepared_handle_v1` payloads for both topology-stream
   families?
3. Do tests and ledger evidence show the bridge is complete for both
   point-location and segment-intersection fake probes?
4. Are all public/release/POD/V4/true-zero-copy boundaries preserved?
5. Does this close the M61 phase-bridge gap enough to continue local Step-2
   topology-stream runtime work?
6. What smallest fixes, if any, are required before M64?

## Non-Authorization Required In Your Verdict

Your verdict must explicitly state that it does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- focused POD spend
- public speedup wording
- broad V3-over-V2 claim
- whole-app speedup claim
- paper reproduction claim
- RTDL-beats-RayJoin claim
- true-zero-copy claim
- V4 work
- embedding
- C ABI
- watch-row closure

## Suggested Verdict Shape

Use this only if you agree:

`accept_m63_topology_stream_m3_phase_bridge_continue_local_step2_no_pod_no_release`

If you disagree, use a blocking verdict and list the smallest local fixes needed
before Step-2 continuation.
