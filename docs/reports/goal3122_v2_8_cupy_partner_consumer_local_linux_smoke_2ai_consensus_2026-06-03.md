# Goal3122: 2-AI Consensus For Goal3120 v2.8 CuPy Partner-Consumer Local Linux Smoke

Date: 2026-06-03

Status: accepted with local-smoke boundary

## Scope

Goal3120 documented a functional smoke of the Goal3117 explicit
partner-consumer front door on the local Linux validation host:

- host: `192.168.1.20`
- checkout: `/home/lestat/work/rtdl_codex_local_check`
- commit: `f367f23d`
- GPU: `NVIDIA GeForce GTX 1070`
- CuPy: `14.0.1`
- operation: `segmented_sum_f64`
- partner: explicit `cupy`
- result: actual `[4.0, 10.0, 3.0]` matched Python reference
- claim flags remained false

## Codex Verdict

Codex verdict: `accept-with-boundary`

The smoke is useful functional evidence that the explicit v2.8
partner-consumer front door can execute caller-supplied CuPy columns for
`segmented_sum_f64`. It does not authorize performance, release, broad
RT-core, or true-zero-copy wording.

## Gemini Verdict

Gemini review:

`docs/reviews/goal3121_gemini_review_goal3120_cupy_partner_consumer_local_linux_smoke_2026-06-03.md`

Gemini verdict: `accept`

Gemini accepted that Goal3120 honestly describes a functional smoke rather than
release/performance evidence, substantiates explicit CuPy partner-column
execution for `segmented_sum_f64`, and keeps the claim boundary aligned with the
Goal3117 front door and Goal3119 consensus.

## Consensus

2-AI consensus result: `accept-with-boundary`

Goal3120 is accepted as local functional smoke evidence for one CuPy
partner-consumer operation. It remains bounded to that exact operation and host.

## Still Not Authorized

This consensus does not authorize:

- a v2.8 release,
- public speedup wording,
- whole-app benchmark claims,
- broad RT-core wording,
- true-zero-copy wording,
- hidden dispatch,
- automatic partner selection,
- app-specific native-engine behavior,
- user-defined shader injection,
- treating the GTX 1070 local Linux host as release-grade performance evidence.

## Next Step

Widen the operation coverage for the explicit partner-consumer front door:

1. test every CuPy-supported operation available on the local Linux host,
2. compare each result against the Goal3114 Python reference consumer,
3. keep timing and release claims blocked,
4. move grouped argmin/argmax/top-k/bounded-collect hardware checks to a pod or
   host with the selected partner stack installed.
