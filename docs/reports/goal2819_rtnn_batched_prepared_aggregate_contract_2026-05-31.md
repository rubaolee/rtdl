# Goal2819 Batched Prepared Aggregate Contract

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2819 starts the next generic small-row amortization target identified by
Goal2818. The new contract batches multiple fixed-radius ranked-summary
aggregate requests over the same prepared search handle and the same resident
prepared-query handle.

This is not an RTNN-native shortcut. The public/native vocabulary is still
fixed-radius neighbors, prepared query points, ranked summaries, and aggregate
requests. The intended reusable benefit is one native crossing, one resident
query/search setup, and one aggregate result download for several summary
requests, instead of treating every tiny summary as a standalone host call.

## Code Changes

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added `aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix`, which batches `(radius, k_max)` requests over resident query/search handles. Small rows use the current block-partial aggregate path; larger rows fall back to the direct aggregate path. |
| `src/native/optix/rtdl_optix_api.cpp` / `src/native/optix/rtdl_optix_prelude.h` | Added `rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch`. |
| `src/rtdsl/optix_runtime.py` | Added `PreparedOptixFixedRadiusNeighbors3D.aggregate_ranked_summary_prepared_queries_batch(...)` and batch phase labels for direct and block-partial aggregate modes. |
| `scripts/goal2348_rtnn_v2_2_external_runner.py` | Added controlled runner mode `ranked-summary-aggregate-prepared-query-batch-float32` with explicit `--aggregate-request-count`. |
| `tests/goal2819_rtnn_batched_prepared_aggregate_contract_test.py` | Guards generic naming, ABI wiring, Python runtime validation, runner exposure, and claim boundary. |

## Pod Evidence

Clean-from-Git pod:

```text
commit: 0cb57ed07e396dff487acb9c5aefe346af36fc35
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
OptiX build: pass
focused tests: 19 passed
```

Artifacts:

- `docs/reports/goal2819_rtnn_batched_prepared_aggregate_contract_pod/rtnn_batched_prepared_aggregate_uniform_32768_req4.json`
- `docs/reports/goal2819_rtnn_batched_prepared_aggregate_contract_pod/rtnn_batched_prepared_aggregate_uniform_65536_req4.json`
- `docs/reports/goal2819_rtnn_batched_prepared_aggregate_contract_pod/goal2819_summary.json`

## Measurement Results

The pod probe uses four identical aggregate requests over the same resident
query/search handles. The batch API returns the same first aggregate as the
single prepared-query path in both rows.

| Points | Single median (s) | Batch total median (s) | Batch per request (s) | Per-request change |
| ---: | ---: | ---: | ---: | ---: |
| 32768 | 0.000070732 | 0.000191492 | 0.000047873 | 1.477x faster |
| 65536 | 0.000127490 | 0.000379212 | 0.000094803 | 1.345x faster |

The phase label for both batch rows is
`prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_block_partials`,
so the batch path is using the same current-best block-partial strategy rather
than regressing to the older direct aggregate path.

## Interpretation

The per-request amortized timing must not be compared to a single CuPy call as
if it were a one-request API. The correct claim is narrower: RTDL now has a
generic mechanism to amortize repeated small aggregate requests over resident
inputs. This is a useful v2.5 runtime primitive for apps that naturally issue
several summary requests over the same prepared inputs, such as multiple radii,
threshold sweeps, parameter probes, or chained summaries.

It does not close the single-request 32K uniform miss from Goal2818. That row
still needs either a lower-overhead single-request path or a claim boundary that
keeps it classified as a sparse small-row overhead case.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- No native app-specific engine customization is introduced.
- No single-request speedup claim is authorized by the amortized batch result.

Goal2819 is accepted as a generic small-row amortization primitive with clean
pod evidence. It is not a public performance or release claim.
