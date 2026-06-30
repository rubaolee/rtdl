# Goal580: Gemini Flash External Review - v0.9.1 Apple RT Pre-Release Gate

Date: 2026-04-18
Reviewer: Gemini Flash
Verdict: **ACCEPT**

## Summary

The v0.9.1 Apple RT candidate gate is accepted. The implementation of the Apple RT backend correctly introduces the 3D `ray_triangle_closest_hit` primitive for macOS Apple Silicon, and the supporting documentation maintains a high standard of honesty regarding its current scope and limitations.

## Evidence Verified

1.  **Code Correctness**:
    -   `src/native/rtdl_apple_rt.mm` provides a functional Metal/MPS implementation using `@autoreleasepool` and `MPSRayIntersector`.
    -   `src/rtdsl/apple_rt_runtime.py` correctly wraps the native library via `ctypes` and provides the expected `run_apple_rt` entry point.
    -   `tests/goal578_apple_rt_backend_test.py` covers versioning, context probing, and result parity against the CPU reference.
    -   `src/rtdsl/__init__.py` properly exports the new Apple RT symbols.

2.  **Doc Consistency**:
    -   `README.md` and `docs/README.md` have been updated to include Apple RT in the "Backend Names In Plain English" and "OS Support At A Glance" sections.
    -   A `grep` of public documentation confirms 94 references to the new version and backend, matching the evidence report.
    -   The numbering issue in `docs/README.md` identified in previous reviews has been fixed.

3.  **Build and Flow**:
    -   `Makefile` contains the necessary `build-apple-rt` target.
    -   The candidate correctly preserves `v0.9.0` as the last released tag while staging `v0.9.1` work.

## Honesty-Boundary Notes

-   **Backend Depth**: Apple RT support is currently limited to 3D `ray_triangle_closest_hit`. It does not yet support the broader 18-workload matrix available on Linux/HIPRT.
-   **Platform Constraint**: This backend is explicitly restricted to Apple Silicon macOS; no cross-platform or Intel-Mac claims are made.
-   **Performance Claims**: The documentation correctly states that no hardware speedup claims or RT-core acceleration evidence are provided for this slice.
-   **API Deprecation**: The implementation uses `MPSRayIntersector`, which is documented as deprecated by Apple. While functional on current SDKs, this is a known residual limitation correctly noted in the gate report.

## Blockers

None.
