# Gemini Review: Goal4414 V3.0 Midterm Review

**Verdict**: `accept-with-boundary`

## Answers to Review Questions

1. **Is M1-M17 still consistent with the Goal4392/4393 app-agnostic V3 boundary?**
   Yes. The work demonstrates disciplined adherence to the Goal4392/4393 constraints. The primitives (`PreparedRayBatch3D`, `grouped-union`, `hit-stream`) and native components lack app-specific names. The implementation is genuinely app-agnostic, validating against the established V3 IR boundaries.
2. **Are M10-M17 measurement windows and no-hidden-copy claims honest?**
   Yes. The measurement instrumentation is highly transparent. M11 correctly isolates the continuation window and proves that the 96-byte `HtoD` transfer is purely for launch parameters, safely below the 262,144-byte named column threshold. Similarly, M17 clearly delineates between the zero-copy prepare window, the hot path, and final scalar materialization. The explicitly `false` assertions for `public_claim_authorized` and the refusal to declare end-to-end zero-copy validate the honesty of these claims.
3. **Does M17 validly close the M16 ray-id host-bookkeeping debt?**
   Yes. By differentiating host-ray-id batches from device-only batches, M17 eliminates the prepare-time `DtoH` transfer for ray IDs entirely. The recorded 0 transfer calls/bytes in the prepare window empirically prove this debt is closed for hit-stream-safe paths.
4. **Is the fail-closed device-column grouped argmin boundary acceptable?**
   Yes. Forcing `require_host_ray_ids(...)` to fail closed for device-only batches is the correct engineering boundary. It prevents silent host fallbacks and makes the current architectural limitation explicit without blocking hit-stream progress.
5. **Is M18 device-side grouped contract the right next target?**
   Yes. With the hit-stream path now fully device-resident (from partner preparation through reduction), the host-indexed grouped argmin is the natural remaining bottleneck. A device-side grouped contract will unlock the same zero-hidden-copy capabilities for nearest-neighbor, DBSCAN, and RayJoin workloads.
6. **What must be fixed before continuing V3 implementation?**
   Nothing is broken that requires an immediate fix (`request-changes`). The project is cleared to continue toward M18, subject to the boundaries defined below.

## Blocking Findings
None. The engineering evidence matches the internal claims and safely respects the V3 consensus gates.

## Non-Blocking Findings
1. **Numba Validation Gap in Hit-Stream:** While Numba was validated in the M10/M11 grouped-stream path, M16 and M17 relied heavily on CuPy for partner device-ray generation and row reduction. Future work should maintain parity and ensure Numba is tested in the hit-stream row reduction path, or provide the necessary written omission justification.
2. **Milestone Documentation Drift:** The rapid progression from M8-M17 outpaced the original M2-M7 plan. Subsequent documentation updates should normalize these milestone labels to prevent confusion in the project history.

## Residual Risks
1. **Micro-evidence vs. Macro-performance:** The M10-M17 suite is excellent micro-evidence for system boundaries, but it does not automatically guarantee benchmark-app-scale performance wins. There is a risk that unpredicted overheads emerge when these primitives are composed in full workloads.
2. **Device-Side Grouped Contract Complexity:** M18's device-side grouped contract is a significantly harder synchronization problem than hit-stream reduction. This poses a timeline risk.

## Recommended Next Target
**M18 device-side grouped contract for prepared device-column ray batches.**

## Binding Boundaries
In accordance with Goal4392/4393 and the midterm review constraints, the following boundaries remain strictly in effect:
- **No public performance claims** or whole-app benchmark speedups are authorized.
- **No author-code parity claims.**
- **No automatic partner or backend selection** (explicit policy is required).
- **No end-to-end application zero-copy claims** (claims must be strictly bound to measured windows).
- **No claims that RT cores generally beat Embree or CUDA-core partners.**
- All new benchmark workloads must include the best practical partner and a Numba reference (unless formally justified).
