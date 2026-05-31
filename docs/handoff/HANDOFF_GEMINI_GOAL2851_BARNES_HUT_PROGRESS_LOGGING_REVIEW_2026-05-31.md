# Gemini Review Handoff: Goal2851 Barnes-Hut Harness Progress Logging

Please perform an independent read-only review of Goal2851 and write your
review to:

`docs/reviews/goal2852_gemini_review_goal2851_barnes_hut_progress_logging_2026-05-31.md`

## Context

Goal2847 showed the Barnes-Hut canonical harness could run quietly for about
342 seconds during the 8,192-body case. Goal2851 adds backend/repeat progress
logging while preserving suppressed per-case JSON output.

## Files To Inspect

- `scripts/goal2642_barnes_hut_embree_vs_optix_lowering_perf.py`
- `scripts/goal2803_barnes_hut_v25_consolidated_harness.py`
- `tests/goal2851_barnes_hut_harness_progress_logging_test.py`
- `docs/reports/goal2851_barnes_hut_harness_progress_logging_2026-05-31.md`

## Review Questions

1. Does the `progress_callback` preserve backward compatibility for existing
   `run_case(...)` callers?
2. Does Goal2803 route progress around the internal `stdout` redirection used
   to suppress per-case JSON?
3. Does the pod smoke evidence in the report support the claim that progress
   now appears before long sub-runs complete?
4. Does this packet avoid performance/release overclaims?
5. Any implementation or report issue that should be fixed before committing
   final consensus?

## Required Review Shape

Use one of the standard verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please state that this is an independent Gemini review distinct from Codex.
Do not edit source files other than writing the requested review document.
If you run tests, report the exact command and result.
