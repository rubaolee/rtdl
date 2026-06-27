# Goal2303 2-AI Consensus: Bounded Closed-Shape Point Probe

Date: 2026-05-17

## Inputs

- Codex implementation/report:
  `docs/reports/goal2301_bounded_closed_shape_point_probe_2026-05-17.md`
- Gemini independent review:
  `docs/reviews/goal2302_gemini_review_goal2301_bounded_closed_shape_probe_2026-05-17.md`
- Gemini clean-artifact follow-up review:
  `docs/reviews/goal2304_gemini_followup_goal2301_clean_artifact_refresh_2026-05-17.md`
- Pod artifacts:
  `docs/reports/goal2301_bounded_point_probe_baseline_current_pod_2026-05-17.json`
  and
  `docs/reports/goal2301_bounded_point_probe_candidate_pod_2026-05-17.json`

## Verdict

`accept-with-boundary`

Codex and Gemini agree that Goal2301 is accepted for the measured
RayJoin-exported 100,000-query PIP-style stream. Gemini's follow-up review
keeps the same `accept-with-boundary` verdict after the clean committed
candidate artifact refresh:

- The native change remains app-agnostic and changes only the generic
  point/closed-shape membership probe geometry.
- The bounded probe preserves the expected exact positive count `8686`.
- Positive-row return improves from `0.051157122 s` to `0.023158047 s`
  median (`2.209x`).
- Scalar count improves from `0.037854942 s` to `0.009362523 s` median
  (`4.043x`).
- The two smaller probe variants are correctly rejected because they returned
  zero positives.

## Boundary

The accepted claim is intentionally narrow:

- The fixed `0.5` half-length is validated on the current RayJoin-exported
  coordinate scale only.
- Broader coordinate scales need either additional evidence, a configurable
  query extent, or a derived extent rule.
- This does not authorize a RayJoin paper reproduction claim.
- This does not authorize an RTDL-beats-RayJoin claim.
- This does not authorize broad whole-app speedup, true zero-copy, or v2.0
  release readiness claims.

## Follow-Up

Future work should study an app-agnostic way to parameterize or derive the
bounded point-probe extent for closed-shape membership across coordinate
systems. That work should remain in generic point/closed-shape terminology and
should not introduce app-specific native ABI names.
