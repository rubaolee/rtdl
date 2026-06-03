# Goal3107: 2-AI Consensus For Goal3105 v2.8 Runtime Gap Kickoff

Date: 2026-06-03

Status: accepted with boundary.

## Inputs

- Codex implementation/report:
  - `docs/reports/goal3105_v2_7_internal_closeout_and_v2_8_runtime_gap_kickoff_2026-06-03.md`
- Gemini review:
  - `docs/reviews/goal3106_gemini_review_goal3105_v2_8_runtime_gap_kickoff_2026-06-03.md`
- Claude attempt:
  - A Claude review was attempted first through the standard handoff, but the Claude CLI returned a session-limit message. No Claude verdict is counted for this goal.

## Consensus Verdict

Goal3105 is accepted as the v2.7 internal closeout and v2.8 benchmark-runtime
gap-map kickoff.

Codex and Gemini agree that:

- v2.7 is correctly closed as an internal version, not a release.
- The v2.8 gap map covers the ten promoted benchmark apps.
- The first v2.8 runtime target,
  `typed_device_resident_result_streams_and_grouped_continuation`, is generic
  and shared across nine benchmark apps.
- The target does not authorize RayJoin-specific, DBSCAN-specific,
  RayDB-specific, Hausdorff-specific, graph-specific, or other app-specific
  native engine logic.
- Partner choice remains explicit; no hidden dispatch or hidden partner
  selection is authorized.
- v3.0 user-defined shader injection remains outside this v2.8 kickoff.

## Validation

Codex validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3105_v2_8_benchmark_runtime_gap_map_test tests.goal3102_v2_7_post_semantic_search_current_closeout_test tests.goal3099_v2_7_semantic_search_preview_test

Ran 14 tests in 0.052s

OK
```

Syntax validation:

```text
py -3 -m py_compile src\rtdsl\v2_8_benchmark_runtime_gap.py src\rtdsl\__init__.py tests\goal3105_v2_8_benchmark_runtime_gap_map_test.py
```

Result: pass.

Gemini performed a static file review and returned `accept-with-boundary`.

## Claim Boundary

This consensus does not authorize a v2.8 release tag, public speedup wording,
whole-app speedup wording, broad RT-core wording, true-zero-copy wording,
paper-reproduction claims, hidden auto-dispatch, hidden partner selection,
automatic partner choice, app-specific native engine behavior, or v3.0
user-defined shader injection.
