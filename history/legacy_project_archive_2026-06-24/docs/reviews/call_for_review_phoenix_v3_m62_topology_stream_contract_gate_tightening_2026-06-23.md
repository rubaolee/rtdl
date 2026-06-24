# Call For Review: Phoenix V3 M62 Topology-Stream Contract Gate Tightening

Requested verdict label:
`accept_m62_local_gate_tightening_continue_step2_no_pod_no_release`,
or a stricter/blocking label if warranted.

## Context

M61 selected the Spatial/RayJoin topology-stream lane as the next Step-2 Set-A
family, but Claude left three P2 review debts:

1. The M61 current-surface checks were too close to source text-mining.
2. The topology-stream runner should explicitly write
   `true_zero_copy_claim_authorized=false`.
3. The internal 2.2815293995x routing delta needed a sanity cap.

M62 claims to close those three debts locally. It does not run POD and does not
authorize release or public performance wording.

## Files To Review

- `src/rtdsl/prepared_execution.py`
- `scripts/v3_phoenix_m61_topology_stream_gap_ledger.py`
- `docs/rebuild/v3/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json`
- `docs/rebuild/v3/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.md`
- `tests/v3_phoenix_m61_topology_stream_gap_ledger_test.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py`
- `docs/reports/phoenix_v3_m62_topology_stream_contract_gate_tightening_2026-06-23.md`

## Questions

1. Did M62 adequately replace weak whole-file source checks with real runner
   metadata-value checks for both point-location and segment-intersection
   topology-stream families?
2. Is the explicit `true_zero_copy_claim_authorized=false` metadata now present
   in the relevant topology-stream runner outputs and locked by tests?
3. Is the internal-delta sanity cap (`1.0x < delta < 10.0x`) sufficient for this
   local ledger gate?
4. Does the stable probe-metadata subset avoid nondeterministic ledger churn
   while preserving the necessary contract evidence?
5. Are all non-authorization boundaries preserved?
6. May the Phoenix V3 work continue to Step-2 implementation after M62, while
   still keeping POD/all-app/release/public-claim gates closed?

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

`accept_m62_local_gate_tightening_continue_step2_no_pod_no_release`

If you disagree, use a blocking verdict and list the smallest local fixes needed
before Step-2 continuation.
