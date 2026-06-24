# Call For Review: Phoenix V3 M64 Topology-Stream Step3 Audit Gate

Requested verdict label:
`accept_m64_topology_stream_step3_audit_gate_continue_local_step2_no_pod_no_release`,
or a stricter/blocking label if warranted.

## Context

M63 created a reusable topology-stream M3 phase bridge. M64 claims to make that
bridge mandatory for topology-stream Step3 readiness by extending
`audit_prepared_execution_session_metadata`.

## Files To Review

- `src/rtdsl/prepared_execution.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`
- `docs/reports/phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md`
- `docs/reports/phoenix_v3_m63_topology_stream_m3_phase_bridge_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json`

## Questions

1. Does M64 correctly restrict the new Step3 bridge requirement to topology-stream
   Set-A candidates, avoiding collateral damage to non-topology runners?
2. Are the required bridge fields sufficient to prevent a topology-stream
   candidate from passing Step3 with a missing/partial M3 table?
3. Does the negative test prove broken bridge metadata becomes
   `incomplete_step3_audit`?
4. Are non-authorization boundaries preserved?
5. May local Phoenix V3 Step-2/Step3 topology-stream work continue after M64?
6. What smallest fixes, if any, are required before M65?

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

`accept_m64_topology_stream_step3_audit_gate_continue_local_step2_no_pod_no_release`

If you disagree, use a blocking verdict and list the smallest local fixes needed
before Step-2/Step3 continuation.
