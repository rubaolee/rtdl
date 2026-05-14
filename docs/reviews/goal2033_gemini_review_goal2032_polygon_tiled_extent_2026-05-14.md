# Goal2033 Gemini Review of Goal2032 Polygon Tiled Extent

Date: 2026-05-14
Verdict: accept-with-boundary

## Review Summary

The Goal2032 implementation successfully addresses the out-of-memory (OOM) issue encountered in Goal2030 for polygon extent candidate discovery at higher scales (e.g., 16k copies) by replacing the dense all-pairs approach with a tiled/bounded candidate discovery method. The relevant code (`examples/rtdl_control_apps_cupy_rawkernel.py`), test suite (`tests/goal2032_polygon_tiled_extent_candidate_discovery_test.py`), and associated reports (`docs/reports/goal2032_polygon_tiled_extent_candidate_discovery_2026-05-14.md`, `docs/reports/goal2032_polygon_tiled_extent_candidate_discovery_2026-05-14.json`) provide consistent and verifiable evidence.

## Verification Points

1.  **CuPy extent candidate discovery is now tiled/bounded instead of dense all-pairs:**
    *   The `_cupy_extent_candidate_indices` function in `rtdl_control_apps_cupy_rawkernel.py` explicitly implements a tiled approach, configurable by `RTDL_CUPY_EXTENT_TILE_ROWS`.
    *   The unit tests confirm the presence of this tiling logic and the absence of the previous dense all-pairs pattern.
    *   The markdown report clearly states the replacement of the dense prepass with tiled candidate discovery.

2.  **16k/32k/64k pod evidence and ratios are accurately quoted:**
    *   Both the markdown and JSON reports present detailed performance metrics, including median times and ratios, for 16,384, 32,768, and 65,536 copies for both polygon pair overlap and Jaccard similarity.
    *   Unit tests validate that these quoted ratios adhere to specified thresholds.

3.  **Oracle parity is preserved:**
    *   The pod artifact JSON files (verified by `test_pod_artifacts_preserve_oracle_parity`) consistently show `all_match_v1_8_python_rtdl_oracle: true`.
    *   The markdown report explicitly confirms that "both polygon rows complete and preserve oracle parity" with the new tiling method.

4.  **Claim boundaries remain honest (`development evidence`, no v2.0 release authorization, not absolutely fair):**
    *   All relevant documents (code, markdown report, JSON report) explicitly state that this work represents "development evidence, not v2.0 release authorization" and that the comparisons are "not absolutely fair" due to the difference in implementation (v1.8 Python+RTDL vs. v2 Python+CuPy RawKernel+RTDL).
    *   The JSON report and its corresponding tests also clearly mark `release_authorized`, `whole_app_speedup_claim_authorized`, and `source_commit_exact` as `false`.

## Missing Information

*   Direct inspection of commit `cc212c0c` was not possible due to tool limitations. However, the comprehensive and consistent details across the provided files (code, tests, and reports) strongly corroborate the described changes.

## Conclusion

The Goal2032 work successfully mitigates the identified memory scaling issue for polygon extent candidate discovery by introducing a tiled approach while maintaining correctness and clearly delineating the scope and limitations of the claims. The evidence provided is robust and consistent.
