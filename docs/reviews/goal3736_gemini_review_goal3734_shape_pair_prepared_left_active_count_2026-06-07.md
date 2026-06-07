# Independent Gemini Review for Goal3734 Shape-Pair Prepared-Left Active Count

**Verdict**: accept

**Date**: 2026-06-07

## Scope

Goal3734 adds a generic prepared-left route for shape-pair active-count queries.
The intended purpose is to remove repeated left-side closed-shape upload from
the RayJoin overlay active-count hot path while keeping native engine vocabulary
generic and app-agnostic.

## Questions Answered

### 1. Does the native implementation remain app-agnostic, or did app/RayJoin logic leak into the engine ABI or implementation?

The native implementation (`src/native/optix/rtdl_optix_workloads.cpp`, `src/native/optix/rtdl_optix_api.cpp`, `src/native/optix/rtdl_optix_prelude.h`) remains app-agnostic. The new functions and data structures refer to generic concepts like "shape-pair relation" and "active count," without any specific "RayJoin" or app-specific logic leaking into the engine ABI or implementation. RayJoin interpretation is explicitly confined to the Python application layer, as confirmed by the `native_engine_boundary` fields in the reports.

### 2. Does the prepared-left route actually reuse left polygon refs, vertices, and bounds from a prepared native handle rather than uploading them in the hot query?

Yes, the prepared-left route successfully reuses left polygon references, vertices, and bounds from a prepared native handle. The native `PreparedShapePairRelationLeftSet` stores these as device pointers, and the hot query path (`count_shape_pair_relation_active_device_with_prepared_left_optix`) directly uses these pre-uploaded device buffers. This is evidenced by `left_prepare: 0.0` and `left_upload: 0.0` in the `a5000_overlay_direct_summary.json` artifact, indicating no preparation or upload during the hot query path.

### 3. Are the Python runtime bindings and lifecycle ownership sound enough for this internal performance route?

Yes, the Python runtime bindings and lifecycle ownership appear sound. The `PreparedOptixShapePairRelationLeftSet` class in `rtdsl/optix_runtime.py` correctly wraps the native handle, provides context manager support (`__enter__`, `__exit__`), and explicit `close()` and `__del__` methods, ensuring proper resource allocation and deallocation. The application layer (`RayJoinOptixShapePairActiveCountPackedLeftShapes` in `rtdl_rayjoin_v2_spatial_join_app.py`) correctly utilizes these mechanisms for lifecycle management.

### 4. Does the RayJoin app adoption correctly keep RayJoin interpretation at the Python app layer?

Yes, the RayJoin app adoption correctly keeps RayJoin interpretation at the Python app layer. The Python application (`rtdl_rayjoin_v2_spatial_join_app.py`) is responsible for orchestrating the calls to the generic native shape-pair relation primitives, preparing the input data, and interpreting the results within the RayJoin context. The native interface itself remains generic, and all RayJoin-specific policies and interpretations are maintained within Python, as explicitly stated in the reports and comments within the Python app file.

### 5. Do the A5000 artifacts support the narrow internal conclusion: active-count hot path left upload is removed, overlay active-count improves to about `0.00316s`, and the safe mixed composite reaches about `345.9x` vs all-CuPy on the measured 4096-chain slice?

Yes, the A5000 artifacts fully support the narrow internal conclusions.
- The `goal3734_shape_pair_prepared_left_active_count_a5000_overlay_direct_summary.json` explicitly shows `native_phase_timings.left_upload: 0.0` and `phases_sec.prepared_query_sec: 0.0031651603057980537`.
- The `goal3734_shape_pair_prepared_left_active_count_a5000_safe_mixed_summary.json` shows the overlay active-count `recommended_route.hot_median_sec` at `0.0031609972938895226` and a composite speedup of `345.9410837045122x` vs. all-CuPy for the 4096-chain slice. All these figures directly match the stated conclusion.

### 6. Do the reports/artifacts avoid overclaiming public RayJoin, paper reproduction, release, broad RT-core, true-zero-copy, or whole-app speedup claims?

Yes, the reports and artifacts meticulously avoid overclaiming. The `docs/reports/goal3734_shape_pair_prepared_left_active_count_2026-06-07.md` includes a clear "Boundary" section. Both JSON artifacts (`overlay_direct_summary.json` and `safe_mixed_summary.json`) contain `claim_boundary` fields with all relevant authorization flags (e.g., `public_speedup_claim_authorized`, `paper_scale_perf_claim_authorized`, `release_authorized`, `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `whole_app_speedup_claim_authorized`) explicitly set to `false`. They consistently emphasize that this is internal engineering evidence.

## Boundary Acknowledgement

This is internal engineering evidence only. It must not authorize a public
release, public RayJoin beat claim, paper-reproduction claim, broad RT-core
claim, true-zero-copy claim, or whole-app speedup claim.