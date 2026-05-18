# Gemini Handoff: Review Goal2337 RTDL v2.1 RayJoin First-Hit Runtime Extension

Please perform an independent Gemini review of Goal2337 and write the review to:

`docs/reviews/goal2338_gemini_review_goal2337_v2_1_rayjoin_first_hit_2026-05-18.md`

## Files To Inspect

- `docs/reports/goal2337_v2_1_rayjoin_first_hit_runtime_extension_2026-05-18.md`
- `docs/reports/goal2337_v2_1_rayjoin_first_hit_pod/rtdl_first_hit_pip_compare_4096.json`
- `docs/reports/goal2337_v2_1_rayjoin_first_hit_pod/rtdl_first_hit_pip_compare_65536.json`
- `tests/goal2337_v2_1_segment_first_hit_runtime_extension_test.py`
- `scripts/goal2337_rayjoin_pip_first_hit_comparison.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`

## Review Questions

1. Does the new native primitive stay generic and app-agnostic, with no RayJoin/PIP-specific native code?
2. Do the pod artifacts support the stated same-query correctness claims: 4,096 and 65,536 queries, missing=0, extra=0, matching RayJoin positive point sets?
3. Do the performance claims match the artifacts: about 17.77x / 60.30x faster than the v2.0 vertical-probe route, native 65,536-query path about 2.855 ms, and still not claiming RTDL beats RayJoin?
4. Are the claim boundaries appropriately narrow: no release authorization, no whole-paper RayJoin reproduction claim, no broad spatial-join claim, no v3.0 shader-injection claim?
5. Is the v2.1 design direction sound: a generic first-hit / bounded witness primitive as a v2.x runtime extension, with user-defined shader injection left for v3.0?

## Required Review Shape

- State reviewer as Gemini / Google, independent from Codex.
- Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`.
- If accepted with boundary, list the boundaries precisely.
- Do not modify source code; write only the review file above.
