# Goal1887 Gemini Review: Goal1886 Segment/Polygon Prepared Reuse (2026-05-13)

## Verdict: accept-with-boundary

### Architecture Boundary

The native engine boundary remains app-agnostic, as the native contract is `generic_ray_primitive_witness_pairs`. The segment/polygon hitcount and road-hazard priority semantics are maintained within Python/PyTorch/CuPy, and no native ABI changes are introduced. This aligns with the expected architectural separation.

### Prepared Reuse API Safety

The prepared partner reuse API appears safe based on the review. Specifically:
- `prepare_segment_polygon_anyhit_optix_partner_device_scene(...)` correctly prepares a reusable triangle scene.
- `allocate_segment_polygon_witness_partner_device_output_columns(...)` handles the allocation of reusable partner-owned witness outputs.
- Python-side witness output length guards are in place to reject incorrectly sized buffers before native entry, enhancing safety.

### Pod Timing Interpretation and Claim Boundaries

The provided pod timing evidence shows significant performance improvements for Goal1886 prepared partner reuse at 2048 rows compared to the v1.8 prepared native row path:
- CuPy: ~3.34x faster (0.001079589 s vs 0.003603125 s).
- Torch: ~4.53x faster (0.000795269 s vs 0.003603125 s).

At 512 rows, CuPy is slightly slower, while Torch remains faster.

The claims derived from these timings are appropriately bounded. The improvements are specific to the segment/polygon hitcount partner-device path with prepared-scene and reusable-witness-output support at particular row counts. The report explicitly avoids authorizing whole-app speedup, broad RT-core speedup, package-install, or v2.0 release readiness, which correctly limits the scope of the performance claims.
