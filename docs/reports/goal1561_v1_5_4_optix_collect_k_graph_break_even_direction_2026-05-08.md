# Goal 1561: OptiX COLLECT_K Graph Break-Even Direction

## Verdict

Do not continue per-call, per-level graph replay.

The only graph direction still worth testing is persistent topology reuse across repeated compatible collect-k calls. If RTDL cannot reuse a graph executable across many calls with the same topology, the next performance work should move to kernel fusion instead.

## Evidence

- Current repo commit: `9fa1e39f802d8ec06a76217d9289444e23569449`
- Goal 1559 diagnostic artifact: `docs/reports/goal1559_v1_5_4_optix_collect_k_level_graph_update_probe_2026-05-08.json`
- Goal 1560 control artifact: `docs/reports/goal1560_v1_5_4_optix_collect_k_level_graph_replay_control_2026-05-08.json`
- Goal 1560 rejected candidate artifact: `docs/reports/goal1560_v1_5_4_optix_collect_k_level_graph_replay_candidate_2026-05-08.json`
- Goal 1561 background current profile: `docs/reports/goal1561_v1_5_4_optix_collect_k_current_longcase_bg_profile_2026-05-08.json`

Background pod work kept running while this analysis was written. It reran 13 graph-related guards and a current-stack long-case profile from clean `9fa1e39f`.

## Current Long-Case Shape

| candidates | total ms | merge launch ms | merge sync ms | merge launches | metadata fields |
|---:|---:|---:|---:|---:|---:|
| 65537 | 0.287675 | 0.086704 | 0.082335 | 23 | 34 |
| 131072 | 0.312462 | 0.091803 | 0.121761 | 23 | 65 |

The long cases still have enough merge-launch activity to justify launch-reduction work in principle.

## Break-Even Math

Goal 1559 showed graph executable update/replay can save time when replayed many times:

| diagnostic target pairs | direct us/replay | graph-update us/replay | saving us/replay |
|---:|---:|---:|---:|
| 4 | 11.745760 | 10.160321 | 1.585439 |
| 16 | 17.316112 | 15.289255 | 2.026857 |

Goal 1560 showed the production per-call candidate regressed long cases:

| candidates | control total ms | graph candidate total ms | regression us |
|---:|---:|---:|---:|
| 65537 | 0.285391 | 0.328192 | 42.801 |
| 131072 | 0.308394 | 0.345594 | 37.200 |

Using the diagnostic per-replay savings as a rough lower-bound model, the graph path would need approximately:

| case | regression us to amortize | representative saving us/replay | rough break-even replays |
|---|---:|---:|---:|
| 65537-like | 42.801 | 1.585439 | 27.0 |
| 131072-like | 37.200 | 2.026857 | 18.4 |

This is why the per-call path failed: one collect-k call does not replay the updated graph enough times to amortize graph capture/update overhead.

## Recommended Next Diagnostic

Only run a persistent-cache diagnostic if we can model repeated compatible calls. The diagnostic should:

- Capture and instantiate graph executables once for a fixed collect-k topology.
- Replay or update them across at least 20 repeated compatible calls.
- Compare against the direct current path for the same repeated-call package.
- Preserve row parity, emitted count, and overflow behavior.
- Keep the path diagnostic-only unless the repeated-call package beats the accepted current stack.

If the project target remains one-shot collect-k calls, skip persistent graph work and move directly to kernel fusion.

## Stop Conditions

Stop graph replay work if any of these are true:

- The user-facing workloads do not issue repeated compatible collect-k calls.
- A persistent-cache diagnostic cannot beat the direct path after 20 or more compatible calls.
- Persistent graph state makes fallback, thread safety, or workspace lifetime unclear.
- The optimization would require a public speedup claim broader than the measured repeated-call scope.

## Claim Boundary

This is a direction and break-even analysis only. It does not change runtime behavior, does not publish a user-visible feature, and does not authorize public speedup wording.
