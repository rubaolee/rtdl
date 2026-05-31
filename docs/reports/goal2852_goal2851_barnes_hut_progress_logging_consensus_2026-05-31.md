# Goal2852 Consensus: Goal2851 Barnes-Hut Harness Progress Logging

Date: 2026-05-31

Consensus verdict: **accept-with-boundary**

Participants:

- Codex: implemented the progress callback and pod smoke validation.
- Gemini: independent external review in
  `docs/reviews/goal2852_gemini_review_goal2851_barnes_hut_progress_logging_2026-05-31.md`.

## Accepted Scope

Goal2851 is accepted as an observability fix for long-running Barnes-Hut pod
harness runs. The accepted change:

- adds an optional `progress_callback` to the underlying Barnes-Hut Embree vs
  OptiX `run_case(...)` helper,
- preserves backward compatibility because the callback defaults to `None`,
- routes Goal2803 progress through `sys.__stdout__` with a `stderr` fallback so
  progress remains visible while per-case JSON is suppressed,
- validates the behavior with local static tests and an RTX A5000 pod smoke.

## Boundary

This consensus does not authorize:

- performance claims,
- public speedup wording,
- release readiness,
- changes to Barnes-Hut JSON semantics.

The change is only an operational progress-logging improvement.

## Final Position

Goal2851 can be used to keep future long Barnes-Hut harness runs from going
silent during expensive backend/repeat sub-runs. It is not a benchmark result
and not release evidence by itself.
