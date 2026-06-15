# Goal4417 V3.0 M20 Device-Continuation Contract

## M20 conclusion

M20 converts the M18/M19 lesson into a reusable V3 rule:

**prepared native output -> partner device continuation -> explicit finalize**

This is the right contract for benchmark apps where RT traversal alone is not the whole application. The native backend may produce device-resident rows, columns, flags, or partial summaries; a partner may continue on those device outputs; and host materialization must be a named finalization phase outside the hot device window.

This is an internal readiness/audit milestone, not a public benchmark result. It authorizes **no public speedup claim**, no RT-core speedup claim, no whole-app speedup claim, no true-zero-copy public claim, no automatic partner selection claim, and no paper/author parity claim.

## State Summary

M20 audits **10/10 promoted benchmark apps**.

| State | Count | Meaning |
|---|---:|---|
| clean_device_continuation_evidence_ready | 1 | We have measured evidence for prepared native output feeding same-stream partner device continuation without hot-window result materialization. |
| primitive_only_no_partner_needed | 4 | The current fair benchmark contract is a primitive/native result row; partner logic is not part of the measured RT hot path. |
| needs_fused_or_prepared_device_continuation_bridge | 4 | The app needs a prepared/fused device-continuation bridge before public whole-app or paper-style claims. |
| currently_not_a_rt_core_claim_target | 1 | The current row is useful RTDL evidence but not a meaningful RT-core acceleration claim target. |

## App Audit Matrix

| Benchmark app | M20 state | Current best contract | Partner position | Next action |
|---|---|---|---|---|
| Hausdorff XHD | needs_fused_or_prepared_device_continuation_bridge | Typed nearest-witness stream plus grouped max-distance continuation | Numba exact continuation is the likely reference; CuPy should remain the best CUDA-core comparison row | Turn nearest-witness output into a prepared device payload plus ordered max-reduction finalize window |
| Spatial RayJoin | needs_fused_or_prepared_device_continuation_bridge | Scalar LSI/PIP rows plus overlay decomposition with device-column point-location work | LSI/PIP scalar-count rows need no hidden partner; overlay still needs fused/prepared point-location and compose continuation | Build reusable overlay-style point-location continuation before public overlay wording |
| RT-DBSCAN | needs_fused_or_prepared_device_continuation_bridge | Fixed-radius core flags plus explicit component-label continuation | Numba is required for reference component labeling; CuPy should remain the best CUDA-core row | Connect fixed-radius outputs to same-stream component labeling with transfer-counter evidence |
| Robot Collision | primitive_only_no_partner_needed | Prepared grouped segment any-hit flags | Primitive-only unless collision-response logic becomes part of the measured contract | Refresh same-contract OptiX/Embree measurement and keep response logic outside the RT hot row |
| Contact Manifold | primitive_only_no_partner_needed | Generic AABB broadphase collect-k candidates | Primitive-only broadphase; exact manifold interpretation remains app logic after candidate output | Refresh large prepared broadphase measurement and explain candidate compactness/materialization cost |
| RayDB Style | primitive_only_no_partner_needed | Prepared ray-triangle grouped i64 native reduction | Native grouped reduction is preferred; partner rows only for intentionally unfused variants | Rerun prepared grouped reduction and preserve primitive-first wording |
| Barnes-Hut | needs_fused_or_prepared_device_continuation_bridge | Prepared fixed-radius node-coverage threshold decision | Numba exact-force remains a separated reference path, not hidden inside RT-core timing | Separate coverage decision, device-side ranked summary, and exact-force finalize windows |
| libRTS Spatial Index | primitive_only_no_partner_needed | Generic prepared AABB index query 2D all-ops | Primitive-only all-ops row; no partner is needed for the current comparison contract | Refresh prepared all-ops OptiX/Embree evidence at human-scale query sizes |
| RTNN | clean_device_continuation_evidence_ready | Prepared fixed-radius ranked-summary graph partial rows plus same-stream device reduction | CuPy is the best CUDA-core partner row; Numba is the no-C++ reference row after CUDA 12.4 NVVM alignment | Carry M19 into the benchmark matrix, while keeping public speedup and paper-parity wording disabled |
| Triangle Counting | currently_not_a_rt_core_claim_target | RT-2A1 generic ray/triangle any-hit summary | Primitive-only summary row; graph counting semantics remain outside current RT hot-window evidence | Refresh primitive summary row and avoid whole-graph acceleration claims |

## Contract Rules

The app-agnostic M20 contract has four phases:

| Phase | Required property | Measurement rule | Materialization rule |
|---|---|---|---|
| prepared_native_producer | Native scene/query/output state is prepared or explicitly resident before the hot window | Prepare timing is recorded separately when it performs initial uploads or graph build | No result materialization is allowed in the hot continuation window |
| device_payload_handoff | Native output is represented as typed device payload columns or partial rows | Payload pointer, size, stream/order token, and ownership metadata are explicit | Host row materialization before partner handoff blocks the clean-device state |
| ordered_partner_device_continuation | Partner continuation runs on the same stream or waits on an explicit producer event | Transfer counter must show no named-column H2D, no D2H, no D2D, and no unknown copies | Partner may produce device summaries, flags, compact rows, or grouped aggregates |
| explicit_finalize | Validation or user-facing materialization is a named finalization phase after the hot window | Finalize timing is reported separately from native traversal plus partner device continuation | Finalize may copy compact summaries to host but must not be counted as hot zero-copy evidence |

## Interpretation

The immediate V3 value is not "every benchmark is now fast." The value is that the system now has a testable rule for where RTDL ends and partner logic begins:

- If the benchmark is primitive-shaped, compare the primitive directly and do not invent partner work.
- If the benchmark needs app logic after traversal, keep that logic explicit, timed, and device-resident where possible.
- If a partner is required, report both the best practical partner row and a Numba no-C++ reference row unless there is a written reason not to.
- If host materialization happens before partner continuation, that row cannot be called clean device continuation.

M20 therefore says which apps are ready as primitive rows, which app has measured clean device-continuation evidence, and which apps still carry real V3 bridge debt.

## Evidence Basis

M18 proved a generic prepared grouped-argmin handoff shape with CuPy and Numba partner rows. M19 proved the ranked-summary continuation shape on the pod with CuPy and Numba, hot-window transfer counters, CUDA graph replay, and materialization after the device window. M20 does not add a new performance number; it consolidates those patterns into a reusable benchmark-audit contract.
