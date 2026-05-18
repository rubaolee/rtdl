# Independent Gemini Review: Goal2337 RTDL v2.1 RayJoin First-Hit Runtime Extension

**Reviewer**: Gemini / Google
**Date**: 2026-05-18
**Independent From**: Codex

## Verdict: `accept-with-boundary`

## Review Questions and Findings:

1.  **Does the new native primitive stay generic and app-agnostic, with no RayJoin/PIP-specific native code?**
    *   **Finding**: **Yes**.
    *   **Evidence**: The report explicitly states, "The OptiX engine only sees generic segment probes and generic prepared segment primitives," and "Any app-specific native RayJoin/PIP code inside the engine" is listed under "does not authorize." Examination of `src/native/optix/rtdl_optix_prelude.h`, `src/native/optix/rtdl_optix_api.cpp`, `src/native/optix/rtdl_optix_core.cpp`, and `src/native/optix/rtdl_optix_workloads.cpp` confirms the absence of "RayJoin" or "PIP" specific naming in the public ABI, internal structs, or kernel logic. The `kSegmentFirstHitKernelSrc` in `rtdl_optix_core.cpp` implements a generic first-hit logic using `atomicCAS` on `GpuSegment` primitives. The Python bindings in `src/rtdsl/optix_runtime.py` expose generic `first_hit_raw`, `first_hit`, and `first_hit_count` methods for `PreparedOptixSegmentPairIntersection`. This is further validated by `tests/goal2337_v2_1_segment_first_hit_runtime_extension_test.py` which asserts the absence of "RayJoin" in native code and the generic nature of the Python bindings.

2.  **Do the pod artifacts support the stated same-query correctness claims: 4,096 and 65,536 queries, missing=0, extra=0, matching RayJoin positive point sets?**
    *   **Finding**: **Yes**.
    *   **Evidence**: The table in `docs/reports/goal2337_v2_1_rayjoin_first_hit_runtime_extension_2026-05-18.md` clearly shows `Missing = 0` and `Extra = 0` for both 4,096 and 65,536 query counts. The Python test `tests/goal2337_v2_1_segment_first_hit_runtime_extension_test.py` (`test_pod_artifacts_show_correctness_and_v2_1_speedup_boundary`) programmatically asserts `payload["all_same_positive_point_set"]`, `payload["runs"][0]["missing_count"] == 0`, and `payload["runs"][0]["extra_count"] == 0` for the parsed JSON artifacts (`rtdl_first_hit_pip_compare_4096.json` and `rtdl_first_hit_pip_compare_65536.json`).

3.  **Do the performance claims match the artifacts: about 17.77x / 60.30x faster than the v2.0 vertical-probe route, native 65,536-query path about 2.855 ms, and still not claiming RTDL beats RayJoin?**
    *   **Finding**: **Yes**.
    *   **Evidence**: The report's table shows "v2.1 speedup vs v2.0" as `17.77x` for 4,096 queries and `60.30x` for 65,536 queries. The "v2.1 native query" time for 65,536 queries is `2.855 ms`. Under "Boundaries," the report explicitly states, "This does not authorize: A claim that RTDL beats RayJoin." The Python test `test_pod_artifacts_show_correctness_and_v2_1_speedup_boundary` asserts `assertGreater(payload["v2_1_speedup_over_v2_0_vertical_probe"], 10.0)` which encompasses the reported speedups. It also asserts `assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])`. The test `test_report_names_v2_1_boundary_without_overclaiming` further verifies that the report itself contains these numbers and the "does not authorize" statement regarding RTDL beating RayJoin.

4.  **Are the claim boundaries appropriately narrow: no release authorization, no whole-paper RayJoin reproduction claim, no broad spatial-join claim, no v3.0 shader-injection claim?**
    *   **Finding**: **Yes**.
    *   **Evidence**: The "Boundaries" section of the report clearly lists what "This does not authorize": "A claim that RTDL beats RayJoin.", "A whole-RayJoin-paper reproduction claim.", "A broad spatial-join speedup claim.", and "A v2.1 release button press without final required consensus." The "v3.0 Boundary" section explicitly states, "This goal deliberately does not require user-defined shader injection. The remaining future v3.0 item is still user-extensible shader/code injection." The Python test `test_pod_artifacts_show_correctness_and_v2_1_speedup_boundary` confirms `assertFalse(payload["claim_boundary"]["v2_1_release_authorized"])` and `assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])` from the artifacts. `test_report_names_v2_1_boundary_without_overclaiming` validates the presence of these boundary statements in the report.

5.  **Is the v2.1 design direction sound: a generic first-hit / bounded witness primitive as a v2.x runtime extension, with user-defined shader injection left for v3.0?**
    *   **Finding**: **Yes**.
    *   **Evidence**: The "Purpose" section of the report states, "Goal2337 adds the generic v2.1 primitive needed by that evidence: a prepared segment scene can answer one nearest/first segment witness per probe." The "New Generic Primitive" section describes the `RtdlSegmentFirstHitRow` and associated functions which are generic. The "What Improved" section details how v2.1 optimizes v2.0 by keeping one nearest witness per probe on the device. The "v3.0 Boundary" section explicitly reserves "user-extensible shader/code injection" for v3.0, confirming this design separation. This is a sound iterative approach, providing a useful, generic primitive now while planning for future extensibility.

## Boundaries:

*   RTDL v2.1 has a measured generic first-hit/nearest-boundary OptiX primitive.
*   The RayJoin PIP support contract can be expressed with RTDL v2.1 using generic native traversal and Python application mapping.
*   The measured same-query path is about `60.30x` faster than the v2.0 vertical-probe route at 65,536 queries.
*   The native query time is within about `1.91x` of RayJoin's query time at 65,536 queries on this pod.
*   **This does not authorize**:
    *   A claim that RTDL beats RayJoin.
    *   A whole-RayJoin-paper reproduction claim.
    *   A broad spatial-join speedup claim.
    *   A v2.1 release button press without final required consensus.
    *   Any app-specific native RayJoin/PIP code inside the engine.
    *   User-defined shader injection (this is explicitly deferred to v3.0).
