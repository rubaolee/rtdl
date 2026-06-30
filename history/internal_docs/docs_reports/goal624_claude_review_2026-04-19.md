# Goal624 External Review: HIPRT and Apple Native Code Reorganization

Date: 2026-04-19
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## Rationale

### Split strategy is sound

Both root wrapper files (`rtdl_apple_rt.mm`, `rtdl_hiprt.cpp`) are now pure `#include` aggregators. Because the compiler still processes one translation unit per backend, all ODR rules, anonymous-namespace scoping, and macro visibility are preserved exactly as in the original monolithic files. This is the safest possible mechanical split.

### ABI is unchanged

All exported symbols verified in `apple_rt/rtdl_apple_rt_api.cpp` and `hiprt/rtdl_hiprt_api.cpp` retain their original `extern "C"` linkage and `rtdl_apple_rt_*` / `rtdl_hiprt_*` names. The `RTDL_APPLE_RT_EXPORT` visibility macro is defined in `prelude.mm`, which is included before `api.cpp` in the same TU — correct ordering. No new symbols are introduced.

### Internal layout is correct

- **Apple prelude** (`apple_rt/rtdl_apple_rt_prelude.mm`): all structs, anonymous-namespace utilities, `AppleRtClosestHitPrepared`, and helper functions. Scoping is identical to what the original monolith provided.
- **HIPRT prelude** (`hiprt/rtdl_hiprt_prelude.h`): structs, `HiprtRuntime`, `DeviceAllocation`, `constexpr` DB constants, and error-helper functions — all in anonymous namespace, consistent with original.
- **HIPRT kernels** (`hiprt/rtdl_hiprt_kernels.cpp`): kernel source-string functions and `build_trace_kernel` helper — anonymous namespace, correct.
- **API layers** delegate cleanly to implementations defined in `core.cpp` files (confirmed by call sites in `rtdl_hiprt_api.cpp`).

### Build targets unchanged

`make build-apple-rt` and `make build-hiprt HIPRT_PREFIX=...` are identical to pre-split. No Makefile or CMake changes were needed because the compiler entry points (the two root `.mm`/`.cpp` files) are unchanged.

### Test gates pass

- Apple backend: 73 tests OK on macOS after split.
- HIPRT backend: 73 tests OK on Linux after split (59.6 s). Only compiler warning was a pre-existing Orochi `fread` return-value diagnostic, not from any RTDL file.

### Files not directly readable but covered

`mps_geometry.mm` (~29 k tokens) and `hiprt_core.cpp` (~46 k tokens) exceeded the single-read limit. Both are covered by: (a) the consistent `#include`-aggregation pattern already confirmed in the root wrappers, (b) the passing test suite exercising all exported operations those files implement, and (c) the Codex review that found no behavioral delta.

## No blocking issues found

- No new exported symbols or ABI surface changes.
- No behavioral logic added, removed, or reordered.
- No Python runtime or release-claim changes.
- Follows the established OptiX/Vulkan/Embree backend directory convention exactly.
