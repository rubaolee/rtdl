# Gemini Review Task: Goal2809 Hausdorff Warm/Tuned v2.5 Entrypoint

Please perform an independent read-only review of Goal2809.

## Files To Inspect

- `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_2026-05-31.md`
- `tests/goal2809_hausdorff_warm_tuned_entrypoint_test.py`
- `docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_pod/hausdorff_xhd_v25_warm_median_4096.json`
- `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `docs/research/future_version_to_do_list.md`

## Questions

1. Confirm whether Goal2809 fairly fixes the cold-start measurement flaw by warming RTDL and using repeated median timing for both the CuPy grouped-grid exact baseline and RTDL/OptiX exact path.
2. Confirm whether the pod artifact is exact (`matches_exact_baseline=true`, zero distance error), clean-provenance, and correctly reports the tuned 4096x4096 ratio as RTDL still slower than CuPy rather than as a speedup.
3. Confirm whether the adaptive defaults are generic and do not reintroduce Hausdorff-specific native ABI/custom engine behavior.
4. Confirm whether the report and artifact keep all public speedup, whole-app, broad RT-core, X-HD reproduction, and release-authorization claim flags closed.
5. Call out any stale wording, overclaim, missing evidence, or test/report mismatch.

## Expected Output

Write your review to:

`docs/reviews/goal2809_gemini_review_hausdorff_warm_tuned_entrypoint_2026-05-31.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is not a release review and should not be treated as v2.5 release consensus.
