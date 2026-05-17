# Goal2307 2-AI Consensus: Current RayJoin-Style Table After Bounded Probe

Date: 2026-05-17

## Inputs

- Codex report:
  `docs/reports/goal2305_rayjoin_current_prepared_comparison_after_bounded_probe_2026-05-17.md`
- Gemini independent review:
  `docs/reviews/goal2306_gemini_review_goal2305_current_rayjoin_table_2026-05-17.md`
- Pod artifact:
  `docs/reports/goal2305_rayjoin_current_prepared_comparison_after_bounded_probe_pod_2026-05-17.json`

## Verdict

`accept-with-boundary`

Codex and Gemini agree that Goal2305 accurately refreshes the current
RayJoin-style prepared comparison after the bounded closed-shape point-probe
change:

- LSI raw rows: `0.008976681 s`, exact expected count `8921`.
- LSI scalar count: `0.008994997 s`, exact expected count `8921`.
- PIP positive rows: `0.023158047 s`, exact expected count `8686`.
- PIP scalar count: `0.009362523 s`, exact expected count `8686`.

## Boundary

The report is a current RTDL internal comparison refresh only. It does not
authorize:

- RayJoin paper reproduction claims.
- RTDL-beats-RayJoin claims.
- Broad whole-app speedup claims.
- True zero-copy claims.
- v2.0 release readiness claims.

The bounded probe half-length remains validated only on the current
RayJoin-exported coordinate scale.

