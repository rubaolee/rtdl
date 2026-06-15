# Goal4405 V3.0 M10 Same-Stream Evidence Plan

Date: 2026-06-15

Status: candidate for 3-AI review and consensus.

## Purpose

M10 is a narrow evidence gate. It is not a benchmark-app speedup result and not a public performance claim.

M8 proved that the V3 harness can lower a generic aggregate frontier primitive to Embree and OptiX under the same contract. M9 proved that the OptiX grouped-stream path can hand device-resident columns to two explicit partners, CuPy and Numba, with matching signatures and a nontrivial predicated threshold case. M9 intentionally did not claim same-stream or true zero-copy because it did not capture CUDA event or transfer-counter evidence.

M10 closes that evidence gap for the existing grouped-stream RTDL OptiX plus partner route.

## Current Evidence Boundary

M9 artifacts:

- `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_2026-06-15.md`
- `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_512_2026-06-15.json`
- `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_8192_2026-06-15.json`
- `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_65536_2026-06-15.json`
- `docs/reports/goal4404_v3_0_m9_grouped_stream_partner_8192_threshold7_2026-06-15.json`

M9 established:

- explicit partner rows: CuPy and Numba;
- matching component-size signatures;
- device pointers for `point_ids`, `component_labels`, `is_core`, and `neighbor_counts`;
- `device_resident_ready=true`;
- `same_stream_ready=false`;
- `true_zero_copy_ready=false`;
- no public speedup claim.

## M10 Objective

Add a same-stream and no-hidden-copy evidence gate around the grouped-stream RTDL OptiX plus partner continuation path.

The gate must answer these questions with measured artifacts:

1. Did the native OptiX grouped-stream producer and partner continuation execute in an observed stream-ordered chain?
2. Did the continuation consume the native-produced device columns without hidden host materialization?
3. Do CuPy and Numba still produce matching validation signatures?
4. Does the evidence remain app-agnostic and explicit-partner, without automatic dispatch?
5. If same-stream or true-zero-copy evidence cannot be observed, does the payload fail closed instead of promoting wording?

## Scope Allowed By This Plan

M10 may implement:

- a V3 M10 evidence wrapper over the existing generic grouped-stream route;
- CUDA event or Nsight-compatible evidence records for the native RT phase, stream handoff, and partner continuation;
- transfer-counter or no-hidden-copy evidence records when actually observed;
- explicit CuPy and Numba partner rows;
- a nontrivial mixed-core predicate case, at minimum the M9 threshold-7 case;
- larger scale rows if the evidence remains sub-millisecond and too noisy;
- focused static and runtime tests for the evidence contract;
- pod execution on the RTX 4000 Ada pod.

M10 may not implement:

- app-specific public API names;
- app-specific native symbols;
- automatic backend or partner selection;
- raw arbitrary OptiX callback exposure as stable user API;
- public performance claims;
- same-stream or true-zero-copy promotion without hardware-observable evidence.

## Required Evidence

Each M10 row must include:

- `version` and `status` identifying M10;
- hardware label and driver/toolchain metadata;
- partner name, exactly `cupy` or `numba`;
- point count, radius, threshold, warmups, repeats, and route options;
- native RT grouped-union phase timing;
- partner continuation timing;
- validation timing;
- validation signature;
- device pointer records for all output columns used by the partner;
- explicit claim readiness fields;
- explicit claim boundary fields, all false.

Same-stream evidence is valid only if the row contains an observed `cuda_event_pair` or `nsight_stream_correlation` record that binds the native producer and partner consumer to a stream-ordered chain. If the native wrapper synchronizes internally, hides the stream handle, or destroys the stream before partner continuation can be ordered on it, `same_stream_ready` must remain false.

True-zero-copy evidence is valid only if the row records device-resident pointer identity plus transfer-counter or equivalent no-hidden-copy evidence, with `host_materialized=false` and `hidden_copy_observed=false`. Pointer identity alone is not enough.

## Acceptance Criteria

M10 passes only if all of the following hold:

1. The payload contains exactly two partner rows, CuPy and Numba.
2. Both rows run the same contract, same scale, same threshold, and same route options.
3. Both rows produce matching validation signatures.
4. Both rows record complete V3 phase timings.
5. `device_resident_ready=true` remains supported by pointer and lifetime evidence.
6. `same_stream_ready=true` appears only with observed CUDA event or Nsight stream-ordering evidence.
7. `true_zero_copy_ready=true` appears only with observed transfer-counter or no-hidden-copy evidence.
8. If criteria 6 or 7 cannot be satisfied, the result is `partial_or_blocked` and readiness stays false.
9. `public_claim_authorized=false` in every row and in the top-level payload.
10. Local focused tests and pod runtime validation pass.

## Fail-Closed Rules

M10 must fail closed in these cases:

- no observable CUDA stream handle or event chain is available from the native grouped-stream wrapper;
- partner continuation cannot be attached to the same stream or an observed event-wait chain;
- transfer counters or equivalent no-hidden-copy evidence cannot be collected;
- validation signatures diverge between CuPy and Numba;
- any host materialization occurs before the partner continuation phase;
- any implementation requires app-specific names or app-specific native logic.

Failing closed is an acceptable M10 result. Faking readiness is not.

## Implementation Direction

Start from the M9 route:

- `src/rtdsl/v3_0_m9_grouped_stream_partner.py`
- `scripts/v3_0_m9_grouped_stream_partner_measure.py`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/optix_runtime.py`

Inspect the grouped-union native ABI variants that already expose execution options and telemetry:

- `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_execution_options`
- `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_execution_options`
- `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_extended_telemetry_and_execution_options`
- corresponding self-range execution-option variants

Preferred route:

1. Add a V3 M10 wrapper that reuses M9's data generation, partner selection, validation, and Numba CUDA compatibility setup.
2. Thread an observed stream/event evidence object through the native RT phase and partner continuation where the existing ABI permits it.
3. For CuPy, use an explicit CuPy stream if it can be bound to the native stream/event chain.
4. For Numba, use an explicit Numba stream or external stream adapter only if the CUDA runtime proves it is valid on the pod.
5. Record blocked evidence instead of promotion if either partner cannot participate in a real stream-ordered chain.
6. Keep the API and native symbol names generic: fixed-radius candidate/union, component union, grouped stream, partner continuation, and evidence.

## Public Wording Boundary

Allowed after M10 passes:

- "RTDL has an internal V3 evidence gate showing the grouped-stream OptiX plus explicit partner path can be run with observed stream-ordering/no-hidden-copy evidence on the tested pod."

Allowed after M10 partially fails:

- "RTDL has device-resident grouped-stream partner evidence, but same-stream or true-zero-copy wording remains blocked until stream and transfer evidence is observable."

Not allowed:

- RTDL is faster than hand-written CUDA/OptiX because of M10.
- RTDL has no data movement in all partner paths.
- RTDL has true zero-copy unless transfer/no-hidden-copy evidence is present.
- RTDL has same-stream continuation if the native wrapper synchronizes internally or hides the stream.
- V3.0 is release-ready because M10 passed.

## Review Questions

The 3-AI review should answer:

1. Is this the correct next gate after M9?
2. Are the acceptance criteria strict enough to prevent false same-stream or zero-copy claims?
3. Is the scope still app-agnostic and compatible with the V3.0 design?
4. Are CuPy and Numba both required in the right way?
5. Is a fail-closed result acceptable if the current V2/V3 wrapper cannot expose stream evidence?
6. What wording, if any, may be used after M10?

## Decision Requested

Use exactly one verdict:

- `VERDICT: ACCEPT`
- `VERDICT: ACCEPT_WITH_GATES`
- `VERDICT: REQUEST_CHANGES`

Any `REQUEST_CHANGES` blocks M10 implementation.
