# Handoff: Gemini Review For Goal3132 v2.8 Partner Front Door Pod Smoke

Please review Goal3132 and write the review to:

`docs/reviews/goal3134_gemini_review_goal3132_partner_front_door_pod_smoke_2026-06-03.md`

## Scope

Goal3132 validates the v2.8 explicit partner-consumer front door on an RTX 4000
Ada pod.

The small functional cases all passed against the Goal3114 Python reference:

- `segmented_count_i64` with CuPy
- `segmented_sum_f64` with CuPy
- `grouped_vector_sum_f64x2` with CuPy
- `grouped_argmin_f64` with Numba
- `grouped_argmax_f64` with Numba
- `grouped_topk_f64` with Torch
- `bounded_collect_finalize_i64` with Torch

The larger Numba timing probe was negative:

- `grouped_argmin_f64`: steady about 0.216-0.312 s vs Python reference 0.056 s
- `grouped_argmax_f64`: steady about 0.210-0.212 s vs Python reference 0.056 s

The report treats this as performance debt, not speedup evidence.

## Files To Inspect

- `docs/reports/goal3132_v2_8_partner_front_door_pod_smoke_2026-06-03.md`
- `docs/reports/goal3132_pod_artifacts/v2_8_partner_front_door_pod_smoke_2026-06-03.json`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`

## Review Questions

1. Does Goal3132 fairly state that pod functional smoke passed for the current
   v2.8 front-door surface?
2. Does it correctly preserve the claim boundary?
3. Is the larger Numba grouped-arg timing correctly classified as negative
   performance evidence / performance debt?
4. Are the next engineering targets the right ones?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Include findings by severity, claim boundary, files inspected, and
next steps.
