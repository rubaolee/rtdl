# Claude Recorded Review: Phoenix V3 M41 Local CUDA Smoke

Date: 2026-06-23
Raw review:
`docs/reviews/claude_phoenix_v3_m41_grouped_reduction_local_cuda_smoke_review_2026-06-23.raw.md`

Verdict: `accept_with_caveats_before_paid_pod`

## Meaning

Claude accepted the small local CUDA smoke as genuine execution/contract
evidence. It closed the earlier P0 that no real CUDA execution existed.

Claude did not authorize paid POD. The reason is the CPU-hot inversion at the
small scale: the productized CUDA runner was slower than CPU NumPy on the hot
path. Claude required a serious-scale free local run before any paid POD
request.

## Accepted

- P1.1 allclose correctness gate: closed.
- P1.2 adapter row/group count exposure: closed.
- local CUDA execution: real and valid as a contract gate.
- claim boundaries: strict.

## Required Next Step From Claude

Run a serious-scale free local run:

```text
row_count >= 262144
group_count = 1024
warmup = 2
repeat = 5
no --allow-non-serious-local-smoke
```

If CPU-hot inversion remains, paid POD should stay blocked.

## Non-Authorization Block

This recorded review does not authorize release, all-app POD spend, paid focused
POD spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy
claims, or broad V3-over-V2 claims.
