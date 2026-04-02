### Resolved Findings

1. **Payload-register mismatches:** fixed. In `src/native/rtdl_optix.cpp`, the current pipelines use `numPayloadValues=4` in the previously blocked paths, matching the kernel `optixTrace` and payload accessor usage.
2. **Overlay containment fallback:** fixed. The CPU-side supplement now checks all vertices of the left polygon against the right polygon and vice versa, replacing the earlier first-vertex-only shortcut.
3. **macOS build/load artifact mismatch:** fixed. The `Makefile` now emits `.dylib` on Darwin, while `optix_runtime.py` uses the same platform-based suffix logic to discover the library.

### Remaining Findings

- **Packed-type interoperability mismatch:** `src/rtdsl/__init__.py` exports only Embree-backed `pack_*` helpers and `Packed*` classes, while `src/rtdsl/optix_runtime.py` relies on its own module-local `Packed*` classes for `isinstance(...)` checks. That means pre-packed geometry produced through the top-level namespace does not interoperate cleanly with `run_optix(...)`.
- **Overlay scalability concern:** the overlay CPU fallback remains pairwise and expensive. Gemini treated this as a remaining concern for large-scale readiness, though not a reappearance of the original first-vertex bug.

### Merge Readiness

**NO-MERGE**

The original three blocked issues were materially fixed, but the revised external OptiX workspace still has an interoperability blocker around packed geometry types and therefore is not yet ready to port into the controlled repository.

### Final Verdict

Claude's revision improved the external OptiX prototype materially and cleared the original blocked findings. However, Gemini still judges the workspace not ready for merge into the controlled repository because the public packed-geometry surface is not yet backend-agnostic.
