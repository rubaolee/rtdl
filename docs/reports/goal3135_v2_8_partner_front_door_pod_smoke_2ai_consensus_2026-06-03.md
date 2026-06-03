# Goal3135: 2-AI Consensus For Goal3132 v2.8 Partner Front Door Pod Smoke

Date: 2026-06-03

Status: accepted with performance-debt boundary

## Scope

Goal3132 validated the current v2.8 explicit partner-consumer front-door surface
on an RTX 4000 Ada pod:

- `segmented_count_i64` with CuPy
- `segmented_sum_f64` with CuPy
- `grouped_vector_sum_f64x2` with CuPy
- `grouped_argmin_f64` with Numba
- `grouped_argmax_f64` with Numba
- `grouped_topk_f64` with Torch
- `bounded_collect_finalize_i64` with Torch

All small functional cases matched the Goal3114 Python reference consumer and
kept claim flags false.

## Codex Verdict

Codex verdict: `accept-with-boundary`

The pod run closes the functional-smoke gap for the current v2.8 front-door
surface on a healthy RTX 4000 Ada stack. It also exposes an important
performance problem: the larger Numba grouped-arg path is slower than the
Python reference for the measured 65,536-row / 1,024-group probe.

## Gemini Verdict

Gemini review:

`docs/reviews/goal3134_gemini_review_goal3132_partner_front_door_pod_smoke_2026-06-03.md`

Gemini verdict: `accept-with-boundary`

Gemini accepted that Goal3132 fairly states pod functional-smoke success,
preserves the claim boundary, correctly classifies the larger Numba timing as
negative performance evidence / performance debt, and identifies the right next
engineering targets.

## Consensus

2-AI consensus result: `accept-with-boundary`

Goal3132 is accepted as pod functional-smoke evidence for the current v2.8
partner-front-door operation surface. It is not accepted as performance
readiness.

## Performance Boundary

The larger Numba probe is explicitly negative:

| Operation | Steady Seconds | Python Reference Seconds |
| --- | --- | ---: |
| `grouped_argmin_f64` | 0.312432, 0.216399, 0.216772 | 0.056126 |
| `grouped_argmax_f64` | 0.210361, 0.211569, 0.212234 | 0.055611 |

This blocks any speedup wording for the current grouped-arg front-door path.

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
- benchmark-app performance claims.

## Next Engineering Target

Diagnose and harden grouped-arg performance:

1. split kernel time, validation time, host compaction time, and front-door
   orchestration time;
2. test larger row/group regimes;
3. identify whether the grouped-arg path should remain a partner continuation
   or become a stronger generic native primitive in the v2.x line;
4. keep all claims blocked until same-contract evidence wins.
