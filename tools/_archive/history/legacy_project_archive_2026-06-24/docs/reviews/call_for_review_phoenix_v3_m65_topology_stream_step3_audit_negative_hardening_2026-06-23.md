# Call For Review: Phoenix V3 M65 Topology-Stream Step3 Negative Hardening

Requested verdict label:
`accept_m65_topology_stream_step3_negative_hardening_continue_local_no_pod_no_release`,
or a stricter/blocking label if warranted.

## Context

M64 made the complete non-authorizing topology-stream M3 bridge mandatory for
Step3 readiness. Claude accepted M64 but suggested low-priority hardening:
exercise additional negative paths. M65 claims to close that local test debt.

## Files To Review

- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`
- `src/rtdsl/prepared_execution.py`
- `docs/reports/phoenix_v3_m65_topology_stream_step3_audit_negative_hardening_2026-06-23.md`
- `docs/reports/phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md`

## Questions

1. Do the new negative tests cover the M64 carry-forward debt?
2. Do they prove bad bridge contract, bad bridge status, partial M3 table, and
   authorization-flag mistakes fail Step3?
3. Does segment-intersection now have its own broken-bridge negative path?
4. Are non-authorization boundaries preserved?
5. May local Phoenix V3 runtime work continue after M65?
6. What smallest fixes, if any, are required before M66?

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
- future-version host integration work
- external device-buffer interop claim
- low-level host interface work
- watch-row closure

## Suggested Verdict Shape

Use this only if you agree:

`accept_m65_topology_stream_step3_negative_hardening_continue_local_no_pod_no_release`

If you disagree, use a blocking verdict and list the smallest local fixes needed
before continuation.
