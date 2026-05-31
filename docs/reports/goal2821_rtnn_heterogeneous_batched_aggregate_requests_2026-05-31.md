# Goal2821 Heterogeneous Batched Aggregate Requests

Date: 2026-05-31

Verdict: implementation-pending-pod-evidence.

Goal2821 hardens the Goal2819 batched prepared-query aggregate contract for a
more realistic user shape: a parameter sweep over the same resident
query/search handles. Goal2819 measured four identical aggregate requests.
Goal2821 lets the benchmark runner send explicit per-request radius and `k_max`
values to the existing generic native batch ABI.

This is still app-agnostic. The vocabulary is fixed-radius neighbors, prepared
query points, ranked summaries, aggregate requests, radius multipliers, and
`k_max` values. It does not introduce an RTNN-native branch.

## Change

`scripts/goal2348_rtnn_v2_2_external_runner.py` now accepts:

- `--aggregate-radius-multipliers`, a comma-separated list of per-request
  multipliers applied to `--radius`.
- `--aggregate-k-values`, a comma-separated list of per-request `k_max` values.

Both lists must match `--aggregate-request-count` when supplied. The prepared
OptiX handle uses the maximum requested radius as its `max_radius`, so a sweep
like `0.5x, 1.0x, 1.5x, 2.0x` remains valid without rebuilding the search
handle.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- No single-request speedup claim is authorized by a batched parameter sweep.
- Pod evidence is required before claiming the heterogeneous sweep behaves or
  amortizes as intended.
