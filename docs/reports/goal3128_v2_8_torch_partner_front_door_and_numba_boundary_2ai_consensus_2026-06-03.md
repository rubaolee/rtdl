# Goal3128: 2-AI Consensus For Goal3126 v2.8 Torch Partner Front Door And Numba Boundary

Date: 2026-06-03

Status: accepted with local-smoke and Numba-boundary limits

## Scope

Goal3126 continued the v2.8 explicit partner-consumer front-door validation
lane:

- normalized `bounded_collect_finalize_i64` bridge output to the canonical
  protocol columns `group_ids`, `item_ids`, and `row_offsets`;
- added a dependency-free regression test preventing auxiliary `counts` from
  leaking through that bridge;
- ran local Linux Torch CUDA smoke for `grouped_topk_f64` and
  `bounded_collect_finalize_i64`;
- recorded that the local Linux Numba CUDA stack fails even a trivial kernel and
  therefore cannot validate grouped argmin/argmax on this host.

## Codex Verdict

Codex verdict: `accept-with-boundary`

The bounded-collect normalization is correct relative to the canonical
continuation protocol, and Torch functional parity is locally demonstrated for
two more v2.8 partner-front-door operations. The local Numba failure is outside
RTDL because a minimal independent Numba kernel also destroys the CUDA context.

## Gemini Verdict

Gemini review:

`docs/reviews/goal3127_gemini_review_goal3126_torch_partner_front_door_and_numba_boundary_2026-06-03.md`

Gemini verdict: `accept-with-boundary`

Gemini accepted that:

- filtering bounded-collect output to `group_ids`, `item_ids`, and
  `row_offsets` is correct relative to the canonical protocol;
- the Torch smoke substantiates local functional parity for `grouped_topk_f64`
  and `bounded_collect_finalize_i64`;
- the Numba CUDA context failure is correctly classified as a local host/Numba
  stack boundary, not an RTDL grouped-arg verdict;
- the claim boundaries are correct.

## Consensus

2-AI consensus result: `accept-with-boundary`

Goal3126 is accepted as local functional smoke and bridge-schema hardening.

## Validation Evidence

Windows:

```text
Ran 27 tests in 0.014s
OK
```

Local Linux Torch:

```text
Ran 27 tests in 0.009s
OK
[goal3126-torch] passed grouped_topk_f64, bounded_collect_finalize_i64
```

Local Linux Numba boundary:

```text
numba.cuda.cudadrv.driver.CudaAPIError: [709] Call to cuCtxSynchronize results in CUDA_ERROR_CONTEXT_IS_DESTROYED
```

This Numba failure occurred for a trivial independent CUDA kernel and for the
grouped-arg smoke, so it is recorded as an environment boundary.

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

The next useful validation requires a pod or comparable CUDA host with a healthy
selected partner stack:

- `grouped_argmin_f64`
- `grouped_argmax_f64`

Both should be run through the explicit v2.8 partner-consumer front door and
compared against the Goal3114 Python reference consumer.
