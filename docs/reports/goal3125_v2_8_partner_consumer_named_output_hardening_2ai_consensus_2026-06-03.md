# Goal3125: 2-AI Consensus For Goal3123 v2.8 Partner-Consumer Named Output Hardening

Date: 2026-06-03

Status: accepted with local-smoke boundary

## Scope

Goal3123 hardened the v2.8 explicit partner-consumer front door so actual
partner execution and the Goal3114 Python reference consumer expose the same
named output shape for the CuPy-covered reduction operations:

- `segmented_count_i64` -> `{"counts": ...}`
- `segmented_sum_f64` -> `{"sums": ...}`
- `grouped_vector_sum_f64x2` -> `{"sum_x": ..., "sum_y": ...}`

It also recorded local Linux CuPy smoke evidence for all three operations.

## Codex Verdict

Codex verdict: `accept-with-boundary`

The code change is narrow, user-facing, and app-agnostic. It does not add a new
native primitive or change partner-selection policy. It makes the v2.8 bridge
easier to validate because actual partner outputs and reference outputs now use
matching named columns for the scalar reductions.

## Gemini Verdict

Gemini review:

`docs/reviews/goal3124_gemini_review_goal3123_partner_consumer_named_output_hardening_2026-06-03.md`

Gemini verdict: `accept`

Gemini accepted that:

- the output-schema hardening is correct and narrowly scoped,
- the actual and reference output shapes now match for the three covered
  operations,
- the local Linux CuPy smoke results are honestly bounded as functional smoke,
- the next-step boundary for grouped argmin/argmax/top-k and bounded collect is
  correct.

## Consensus

2-AI consensus result: `accept-with-boundary`

Goal3123 is accepted as v2.8 front-door hardening and local functional smoke.
The stricter consensus verdict keeps the hardware/performance/release boundary
explicitly blocked.

## Validation Evidence

Windows:

```text
Ran 26 tests in 0.014s
OK
```

Local Linux:

```text
Ran 26 tests in 0.006s
OK
[goal3123] passed cases segmented_count_i64, segmented_sum_f64, grouped_vector_sum_f64x2
```

## Still Not Authorized

This consensus does not authorize:

- a v2.8 release,
- public speedup wording,
- broad RT-core wording,
- true-zero-copy wording,
- hidden dispatch,
- automatic partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- benchmark-app performance claims,
- treating the GTX 1070 local Linux host as release-grade performance evidence.

## Next Step

Move to a suitable CUDA pod or host for the remaining partner-front-door
operations:

- `grouped_argmin_f64`
- `grouped_argmax_f64`
- `grouped_topk_f64`
- `bounded_collect_finalize_i64`

Those checks should compare against the Goal3114 Python reference consumer and
keep timing/performance claims separate from correctness.
