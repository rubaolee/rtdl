# Goal3131: 2-AI Consensus For Goal3129 v2.8 Torch Grouped-Arg Front Door Local Smoke

Date: 2026-06-03

Status: accepted with local-smoke and Numba-specific boundary

## Scope

Goal3129 validated the remaining v2.8 explicit partner-consumer front-door
grouped-arg operations through a healthy local Torch CUDA partner:

- `grouped_argmin_f64`
- `grouped_argmax_f64`

Both matched the Goal3114 Python reference consumer and kept claim flags false.

## Codex Verdict

Codex verdict: `accept-with-boundary`

Torch functional smoke closes local correctness coverage for the grouped-arg
front-door path through at least one healthy explicit partner. Numba-specific
evidence remains open because the local Numba CUDA stack independently fails
even a trivial kernel.

## Gemini Verdict

Gemini review:

`docs/reviews/goal3130_gemini_review_goal3129_torch_grouped_arg_front_door_local_smoke_2026-06-03.md`

Gemini verdict: `accept-with-boundary`

Gemini accepted that:

- the Torch smoke substantiates local functional parity for `grouped_argmin_f64`
  and `grouped_argmax_f64`;
- the current local coverage table is accurate and bounded;
- Numba-specific validation should remain open despite Torch passing;
- the claim boundaries are correct.

## Consensus

2-AI consensus result: `accept-with-boundary`

Goal3129 is accepted as local functional smoke. It completes local functional
coverage of the currently supported v2.8 partner-front-door operations through
at least one healthy explicit partner.

## Current Local Functional Coverage

| Operation | Local Partner Smoke | Status |
| --- | --- | --- |
| `segmented_count_i64` | CuPy | passed |
| `segmented_sum_f64` | CuPy | passed |
| `grouped_vector_sum_f64x2` | CuPy | passed |
| `grouped_argmin_f64` | Torch | passed |
| `grouped_argmax_f64` | Torch | passed |
| `grouped_topk_f64` | Torch | passed |
| `bounded_collect_finalize_i64` | Torch | passed |

## Still Open

The remaining v2.8 validation gap is partner-specific, not operation-surface
functional coverage:

- Numba-specific grouped argmin/argmax validation needs a healthy CUDA stack.
- Timing and performance evidence need pod-class hardware and larger stream
  sizes.
- All public/release claim boundaries remain blocked.

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

The next meaningful work requires pod-class hardware:

1. Numba-specific grouped argmin/argmax validation on a healthy CUDA stack,
2. timing/performance separation for the front-door operations,
3. larger stream-size validation that resembles benchmark-app continuations,
4. continued claim-boundary enforcement.
