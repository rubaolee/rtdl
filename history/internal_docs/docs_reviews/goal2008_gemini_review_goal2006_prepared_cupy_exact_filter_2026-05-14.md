# Goal2008 Gemini Review: Goal2006 Prepared CuPy Exact Filter Reuse

Date: 2026-05-14

Verdict: accept

## Summary of Review

The Goal2006 changes, primarily implemented in `src/rtdsl/partner_adapters.py`, correctly integrate an on-device CuPy RawKernel for exact segment/triangle filtering within a prepared scene context. This addresses a correctness gap and enhances performance for the CuPy prepared path. The associated scripts and documentation accurately reflect these changes and adhere to strict claim boundaries.

## Verification Points

1.  **The native engine remains app-agnostic and candidate-only.**
    *   **Verified.** The `native_engine_row_contract` metadata consistently indicates `generic_ray_primitive_candidate_witness_pairs`, confirming the native engine's app-agnostic output. Application-specific logic is confined to the partner layer.
2.  **The prepared-scene wrapper does not make native OptiX app-specific.**
    *   **Verified.** The `_PartnerPreparedTriangleScene` wrapper, introduced in `src/rtdsl/partner_adapters.py`, stores generic `polygon_triangle_columns` and `polygon_triangle_aabbs`. Its purpose is to retain geometry for partner-side processing without introducing app-specific logic into native OptiX calls.
3.  **The CuPy prepared path has enough retained geometry to exact-filter generic candidates on device before counting.**
    *   **Verified.** The `_PartnerPreparedTriangleScene` retains necessary `polygon_triangle_columns` and `polygon_triangle_aabbs`. The `_cupy_segment_triangle_exact_witness_filter_kernel` (a CuPy RawKernel) is specifically used in `_cupy_exact_segment_triangle_witness_pairs` to perform on-device exact filtering of candidates before unique-pair counting in `segment_polygon_hitcount_optix_prepared_partner_device_count_columns`.
4.  **The road-hazard scripts now use `float32` ray columns for the OptiX device-column ABI.**
    *   **Verified.** Both `scripts/goal1868_road_hazard_partner_priority_flags_pod_smoke.py` and `scripts/goal1869_road_hazard_v2_partner_perf.py` explicitly define ray columns (`ox`, `oy`, `dx`, `dy`, `tmax`) using `runtime["float32"]`, aligning with the OptiX device-column ABI.
5.  **The pod artifact supports only the narrow same-contract claim: prepared CuPy road-hazard priority flags at count 2048 passed parity and beat v1.8 prepared native rows by a small margin.**
    *   **Verified.** The reports `docs/reports/goal1889_road_hazard_prepared_partner_reuse_2026-05-13.md` and `docs/reports/goal2006_prepared_cupy_exact_filter_reuse_2026-05-14.md`, along with the artifact `docs/reports/goal2006_pod_smoke/road_hazard_prepared_cupy_exact_filter_2048.json`, confirm strict priority-flag parity. The artifact shows the Goal2006 prepared CuPy path achieving a median speedup of approximately 1.08x compared to the v1.8 prepared native rows at a count of 2048, which constitutes a small but measurable margin.
6.  **The report does not overclaim v2.0 release readiness, broad RT-core speedup, package-install readiness, or general whole-app speedup.**
    *   **Verified.** All relevant reports and the pod artifact's `claim_boundary` section explicitly disallow these overclaims, maintaining a narrow, fact-based scope for the reported improvements.

## Conclusion

The Goal2006 changes are well-implemented, thoroughly tested, and clearly documented. The introduction of on-device CuPy exact filtering for prepared scenes correctly extends existing patterns while maintaining architectural boundaries. The performance claims are modest and well-supported by evidence.
