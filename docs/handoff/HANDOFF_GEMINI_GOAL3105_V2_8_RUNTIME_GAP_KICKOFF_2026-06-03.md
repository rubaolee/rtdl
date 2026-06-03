# Handoff - Gemini Review for Goal3105 v2.7 Closeout / v2.8 Runtime Gap Kickoff

Please perform a read-only/static review of Goal3105 and write your review to:

`docs/reviews/goal3106_gemini_review_goal3105_v2_8_runtime_gap_kickoff_2026-06-03.md`

Important: do not run shell commands. Use file reads only and write the review file. Claude is currently session-limited, so this review must clearly identify itself as Gemini/Antigravity and must not claim to be Claude.

## Context

The user asked to close v2.7 as an internal version and start v2.8.

Goal3105 does this by:

- marking v2.7 closed internally, not released;
- opening v2.8 as a benchmark-runtime engineering lane;
- adding a machine-readable ten-app runtime gap map;
- selecting the first v2.8 runtime target:
  `typed_device_resident_result_streams_and_grouped_continuation`.

This target must remain generic. It must not become RayJoin-specific, DBSCAN-specific, RayDB-specific, Hausdorff-specific, graph-specific, or app-specific native engine logic.

## Files to Inspect

- `docs/reports/goal3105_v2_7_internal_closeout_and_v2_8_runtime_gap_kickoff_2026-06-03.md`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `src/rtdsl/__init__.py`
- `tests/goal3105_v2_8_benchmark_runtime_gap_map_test.py`
- `docs/reports/goal3102_v2_7_post_semantic_search_current_closeout_2026-06-03.md`
- `docs/reports/goal3104_v2_7_post_d8_closeout_2ai_consensus_2026-06-03.md`

## Required Review Questions

1. Does Goal3105 correctly close v2.7 as an internal version without authorizing release or public claims?
2. Does the v2.8 gap map cover the ten promoted benchmark apps?
3. Is the first v2.8 runtime target genuinely generic and shared across multiple benchmark apps?
4. Does the design preserve explicit partner choice and avoid hidden dispatch or hidden partner selection?
5. Does the design avoid app-specific native engine logic?
6. Are the tests and validation strong enough for a kickoff/gap-map goal?

## Expected Verdict Vocabulary

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The likely correct verdict is `accept-with-boundary` if all claim boundaries hold.
