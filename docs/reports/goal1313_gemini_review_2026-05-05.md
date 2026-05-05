# Goal1313 Gemini Review: Native Jaccard Device-Level Plan

Date: 2026-05-05
Reviewer: Gemini CLI

## Verdict

**PASS**

The plan presented in `goal1313_v1_5_native_jaccard_device_plan_2026-05-05.md` is architecturally sound and strictly adheres to the safety and genericness mandates of the v1.5 release cycle. It successfully balances the need for native acceleration with the requirement for fail-closed correctness and transparent performance diagnostics.

## Findings

### 1. Diagnostic Preservation and Public Wording
The plan correctly keeps `polygon_set_jaccard` in the `diagnostic_blocked` state. By ensuring `V1_5_BOUNDED_COLLECTION_PUBLIC_WORDING_ALLOWED = False` in the contract and explicitly blocking public wording in the migration inventory, the plan avoids any premature or overclaimed speedup statements. The documentation of the OptiX-slower-than-Embree behavior (Goal1312) is a critical transparency measure that is well-integrated.

### 2. Generic Native ABI
The proposed native functions (`rtdl_optix_collect_polygon_pair_candidates_bounded` and `rtdl_native_reduce_polygon_pair_exact_area_summary`) are appropriately named and designed to be app-agnostic. They focus on the underlying primitives (candidate collection and area reduction) rather than the high-level Jaccard application, which prevents the introduction of restrictive "app shortcuts" in the native layer.

### 3. Fail-Closed and Guarded Reduction
The fail-closed mechanism is robustly defined. The Python-layer implementation in `generic_polygon_primitives.py` already demonstrates the required behavior by raising `RuntimeError` before reduction can occur on overflow. The plan to move this enforcement into the native device-level collector is the correct next step for hardening the pipeline.

### 4. Backend Freezing
The plan and the implementation in `generic_polygon_primitives.py` correctly identify and freeze the Vulkan, HIPRT, and Apple RT backends. The use of `FROZEN_BEFORE_V2_1_POLYGON_BACKENDS` ensures that development effort remains focused on the primary v1.5 targets (Embree and OptiX).

### 5. Next Slice Prioritization
Prioritizing the OptiX native bounded collection is the correct strategic choice. Given that OptiX is currently the performance laggard in the Jaccard diagnostic tests despite having hardware RT cores, identifying and optimizing the bottleneck in candidate collection on NVIDIA hardware is the highest-value remaining task for the v1.5/v2.0 transition.

## Risks

- **Native Implementation Complexity:** Implementing a fail-closed bounded collection on the device (especially in OptiX) may introduce subtle race conditions or performance regressions if the atomic counting and overflow detection are not carefully handled.
- **Contract Parity:** Ensuring that Embree and OptiX provide identical "complete candidate coverage" guarantees at the native level may be difficult if their underlying RT traversal behaviors differ significantly.

## Required Fixes

None. The plan is comprehensive and aligned with existing project standards.

## Conclusion

The v1.5 Native Jaccard Device-Level Plan is ready for implementation. It establishes a clear path for moving logic to the native layer while maintaining the high bar for correctness and diagnostic transparency required for the current release stage.
