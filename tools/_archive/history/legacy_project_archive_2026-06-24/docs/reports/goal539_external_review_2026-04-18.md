# Goal 539 External Review: All OptiX Workload Correctness Under CUDA 12.2.2

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6

## Verdict: ACCEPT

## Summary

The all-current-OptiX workload correctness gate is sufficient. All 86 tests across 18 test modules passed after a correctness fix that was properly identified and resolved within the goal.

## Evidence Quality

The JSON evidence record (`goal539_all_optix_cuda122_correctness_2026-04-18.json`) is well-formed and records:
- `status: PASS`
- All 18 test module names
- Specific CUDA toolkit path (`/home/lestat/vendor/cuda-12.2.2/bin/nvcc`)
- GPU/driver/capability metadata (GTX 1070, driver 580.126.09, cc 6.1)

## Fix Assessment

The root-cause finding and fix are technically sound and independently confirmed in the source code.

**Before:** `g_frn` and `g_knn` were single shared `std::call_once` caches used by both 2D and 3D code paths. When the 2D path initialized first, the 3D path reused the wrong compiled kernel, producing zero-row output silently.

**After (verified in `rtdl_optix_core.cpp:1871–1874` and `rtdl_optix_workloads.cpp`):**
- `g_frn` / `g_frn3d` — separate `FrnCuFunction` statics, each with independent `init` flag
- `g_knn` / `g_knn3d` — separate `KnnCuFunction` statics, each with independent `init` flag
- Each 3D workload path calls `std::call_once` on its own cache, loads its own PTX module, and resolves its own kernel function (`fixed_radius_neighbors_3d`, `knn_rows_3d`)
- Launch sites use the correct `g_frn3d.fn` / `g_knn3d.fn` handles

The fix is minimal, structurally correct, and does not touch 2D paths.

## Scope Honesty

The report's "Honest Boundary" section correctly scopes the claim: this is a correctness pass for the current OptiX-supported workload families, not a performance claim, not an RT-core claim (GTX 1070 has none), and not a guarantee for future workloads without OptiX test coverage. This is appropriate framing.

## Coverage Assessment

The 18 test modules span the full breadth of current OptiX workload families: geometric hit queries (2D/3D), spatial neighbors (FRN/kNN in 2D and 3D), graph BFS and triangle-count, DB scan/aggregation, prepared and columnar dataset paths, Vulkan/OptiX parity, Embree interop, and legacy cold-start paths. This is comprehensive for the current surface.

## No Concerns

No correctness gaps, no suppressed failures, no scope inflation. The single failure found (3D zero-row bug) was a real regression uncovered by the broader test order, properly fixed, and re-verified to 86/86 pass.
