# Handoff: Claude Review For Goal2800 RTNN Live Ranked-Summary Harness

Please perform an independent read-only Claude review of Goal2800 and write the review to:

`docs/reviews/goal2800_claude_review_rtnn_live_ranked_summary_harness_2026-05-31.md`

## Context

Goal2800 adds a current live v2.5 harness for the RTNN benchmark-app row.

The harness runs:

- RTDL/OptiX exact fixed-radius 3-D ranked-summary rows;
- the stronger same-contract CuPy grid CUDA-core opponent;
- deterministic 65,536-point uniform, clustered, and shell distributions.

The important boundary is that the CuPy grid opponent is faster in the first pod artifact. This goal must not be framed as an RTDL speedup claim. It is a live evidence and contract-truth goal.

## Files To Inspect

- `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`
- `tests/goal2800_rtnn_v25_live_ranked_summary_harness_test.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2800_rtnn_v2_5_live_ranked_summary_harness_2026-05-31.md`
- `docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536.json`
- `docs/reports/goal2800_pod_artifacts/rtnn_v25_live_ranked_summary_65536.stdout`

## Review Questions

1. Does the harness correctly exercise the current RTDL/OptiX ranked-summary route and the CuPy grid opponent?
2. Is the tiny candidate-count tolerance for float32 boundary differences honest and sufficiently bounded?
3. Does the report accurately reflect that CuPy grid is faster on the first artifact?
4. Does the manifest update avoid overclaiming Triton, public speedup, RTNN paper reproduction, or native app customization?
5. Are app-specific RTNN policies kept outside the native engine contract?
6. Is a clean-from-Git rerun still correctly identified as pending before final evidence closure?

## Required Review Format

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please include:

- a short verdict summary;
- file-grounded findings if any;
- boundary notes for public claims;
- whether the review is an independent Claude review distinct from Codex.
