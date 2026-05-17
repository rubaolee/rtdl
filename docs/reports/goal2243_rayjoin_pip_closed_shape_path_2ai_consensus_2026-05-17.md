# Goal2243: RayJoin PIP Closed-Shape Path 2-AI Consensus

Status: accepted.

## Evidence

- Codex implementation/report:
  `docs/reports/goal2241_rayjoin_same_query_pip_closed_shape_path_2026-05-17.md`
- Gemini review:
  `docs/reviews/goal2242_gemini_review_goal2241_rayjoin_pip_closed_shape_path_2026-05-17.md`
- Tests:
  `tests/goal2192_rayjoin_same_query_stream_adapter_test.py`
  `tests/goal2241_rayjoin_same_query_pip_closed_shape_path_test.py`

## Consensus

Codex and Gemini agree that the RayJoin same-query PIP/OptiX runner now uses the
generic closed-shape membership primitive:

```text
closed_shape_membership_2d_optix
```

The runner preserves the RayJoin-facing row contract in Python by mapping
`shape_id` to `polygon_id` and `membership` to `contains`. This is the correct
boundary: the native engine keeps generic closed-shape vocabulary, while
RayJoin-specific naming remains in the application harness.

## Boundary

This consensus accepts only the wiring change. It does not authorize:

- full RayJoin reproduction,
- paper-scale performance claims,
- v2.0 release readiness,
- or broad PIP/RayJoin speedup claims.

Pod timing from a pushed commit is still required before recording a measured
performance conclusion for this path.
