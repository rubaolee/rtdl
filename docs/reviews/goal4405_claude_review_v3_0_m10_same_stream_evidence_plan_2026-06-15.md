# Claude-Lens Review: Goal4405 V3.0 M10 Same-Stream Evidence Plan

Date: 2026-06-15

Reviewer: Claude-lens independent subagent via `multi_agent_v1`

Reviewed artifact: `docs/reports/goal4405_v3_0_m10_same_stream_evidence_plan_2026-06-15.md`

VERDICT: ACCEPT_WITH_GATES

## Top Findings

1. M10 is the right next objective, but only as a narrow evidence gate, not as claim promotion.
2. The plan directly follows the M9 report: M9 proved device-resident CuPy and Numba grouped-stream rows, including the threshold-7 predicated case, while explicitly keeping `same_stream_ready=false` and `true_zero_copy_ready=false`.
3. CuPy and Numba must both pass with the same contract, same parameters, and matching signatures. Missing either partner must fail closed.
4. Same-stream evidence must be hardware-observable per partner row: CUDA event pairs or Nsight stream correlation around the exact native OptiX producer and partner continuation. Host timers or `stream_handle: 0` are not enough.
5. No-hidden-copy evidence must include pointer identity plus transfer counters or equivalent proof for the measured steady-state handoff.
6. The threshold-7 predicated case must remain in scope because it exercises `all_core_flags_true=false`, not just the trivial all-core path.

## Required Gates

- CuPy and Numba rows are both required in the same packet.
- `same_stream_ready=true` requires a hardware-observed producer-to-consumer stream-ordering record for that exact row.
- `true_zero_copy_ready=true` requires `transfer_counter_observed=true`, `host_materialized=false`, and `hidden_copy_observed=false`.
- Validation materialization must occur after the measured native plus partner window.
- Public flags remain false: no public speedup, no RT-core speedup, no automatic partner selection, and no broad true-zero-copy wording.

## Risks

The main false-positive risk is that the current `InstrumentationPacket.same_stream_ready` property is satisfied by any CUDA-event or Nsight evidence record. M10 validation must prove that the event pair belongs to the exact producer-consumer handoff for each partner row.

The zero-copy risk is scope creep. M9 metadata can include host-query or setup transfer modes in parts of the path, so M10 may only claim the measured steady-state grouped-stream handoff unless it separately proves setup, input, and acceleration-structure phases.

Numba stream interop may differ from CuPy stream interop on the pod. A partner-specific blocked row is better than a forced promotion.

## Wording Boundary

Allowed after a passing M10:

"M10 records path-specific same-stream/no-hidden-copy evidence for the prepared OptiX grouped-stream fixed-radius component continuation with explicit CuPy and Numba partner rows, for the measured steady-state handoff only."

Blocked wording:

- "V3.0 is zero-copy."
- "RTDL has no hidden copies."
- "RTDL accelerates arbitrary CuPy or Numba code."
- "This authorizes a public speedup claim."
- "This is RTDL-only performance."
- "This proves whole-app DBSCAN or broad RT-core acceleration."

## Final Recommendation

Proceed, but keep the gate sharp. M10 should turn M9's honest "not ready yet" flags into either per-row evidence-backed readiness or another explicit fail-closed artifact.
