# Goal2821 Heterogeneous Batched Aggregate Requests

Date: 2026-05-31

Verdict: accept-with-boundary.

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

## Pod Evidence

Artifacts are saved under
`docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_pod/`.

The pod compared one heterogeneous four-request batch against four sequential
single aggregate calls over the same prepared search/query handles. Requests:

| Request | Radius | k_max |
| ---: | ---: | ---: |
| 1 | 0.01 | 8 |
| 2 | 0.02 | 16 |
| 3 | 0.03 | 32 |
| 4 | 0.04 | 50 |

Results:

| Points | Batch median sec | Sequential total median sec | Batch per request sec | Sequential per request sec | Batch improvement |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32768 | 0.000300650 | 0.000348964 | 0.000075163 | 0.000087241 | 1.161x |
| 65536 | 0.000899193 | 0.002244465 | 0.000224798 | 0.000561116 | 2.496x |

Environment:

- GPU: NVIDIA RTX A5000, driver 570.211.01.
- Source commit: `17302d0f02bc0630cd7f4993309727d1bd47ebb7`.
- Source dirty state: `[]`.
- Focused tests: 12 passed.

Correctness:

- Batch aggregate results exactly matched the four sequential single aggregate
  calls for both rows.
- The phase label stayed on the current-best block-partial batch path:
  `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_block_partials`.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- No single-request speedup claim is authorized by a batched parameter sweep.
- This is internal amortization evidence for heterogeneous prepared aggregate
  sweeps, not a paper/release/public performance claim.

## Interpretation

This is the useful version of Goal2819's batch idea. It shows the batch API is
not merely repeating one request four times: users can sweep radius and `k_max`
without rebuilding the prepared search/query handles, and the batched call keeps
the result exact against the equivalent sequential calls. The effect grows with
the amount of work per sweep: 32K shows a modest 1.16x amortization win, while
65K shows a stronger 2.50x win because the four-request sequential path pays
more repeated runtime overhead.

This still does not solve single-request launch overhead. It strengthens the
v2.5 design story for real workloads that naturally issue several summaries
over the same resident data.
