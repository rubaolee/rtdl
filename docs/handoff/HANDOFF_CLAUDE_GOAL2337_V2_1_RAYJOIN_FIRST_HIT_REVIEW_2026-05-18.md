# Claude Handoff: Review Goal2337/Goal2338 RTDL v2.1 RayJoin First-Hit Runtime Extension

Please perform an independent Claude review and write it to:

`docs/reviews/goal2339_claude_review_goal2337_v2_1_rayjoin_first_hit_2026-05-18.md`

## Context

Goal2337 adds a generic RTDL v2.1 OptiX prepared segment first-hit primitive to close the RayJoin PIP performance gap found in Goal2335. It must stay app-agnostic: RayJoin/PIP logic belongs only in Python runner/report/test, not native engine code.

Goal2338 is a Gemini review that accepted the direction with boundary, but it reviewed an earlier conservative artifact refresh. The final clean committed artifacts are stronger:

- 4,096 queries: RayJoin positives = RTDL positives = 3,374, missing=0, extra=0, v2.1 native query 0.796 ms, v2.1 total validation 1.363 ms, 19.37x faster than v2.0 vertical-probe route.
- 65,536 queries: RayJoin positives = RTDL positives = 53,372, missing=0, extra=0, v2.1 native query 2.654 ms, v2.1 total validation 10.073 ms, 72.93x faster than v2.0 vertical-probe route, native query 1.78x slower than RayJoin query.

## Files To Inspect

- `docs/reports/goal2337_v2_1_rayjoin_first_hit_runtime_extension_2026-05-18.md`
- `docs/reviews/goal2338_gemini_review_goal2337_v2_1_rayjoin_first_hit_2026-05-18.md`
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

1. Is the new primitive generic and app-agnostic, with no RayJoin/PIP-specific native engine code?
2. Do the final clean pod artifacts support the same-query correctness and performance claims above?
3. Is the performance conclusion fair: v2.1 is a major improvement over v2.0 and is close enough to RayJoin to call this RayJoin-level RTDL evidence, while still not claiming RTDL beats RayJoin?
4. Are the boundaries clear: no whole-paper RayJoin reproduction, no broad spatial-join claim, no v2.1 release button without final consensus, user-defined shader injection still v3.0?
5. Are there any blockers before treating Goal2337 as the v2.1 RayJoin first-hit milestone?

Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`.
