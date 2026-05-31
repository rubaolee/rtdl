# Goal2819 Batched Prepared Aggregate Contract

Date: 2026-05-31

Verdict: implementation-pending-pod-evidence.

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
| `src/native/optix/rtdl_optix_workloads.cpp` | Added `aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix`, which launches direct float32 aggregate kernels for a batch of `(radius, k_max)` requests and downloads one aggregate array. |
| `src/native/optix/rtdl_optix_api.cpp` / `src/native/optix/rtdl_optix_prelude.h` | Added `rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch`. |
| `src/rtdsl/optix_runtime.py` | Added `PreparedOptixFixedRadiusNeighbors3D.aggregate_ranked_summary_prepared_queries_batch(...)` and phase label `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_direct`. |
| `scripts/goal2348_rtnn_v2_2_external_runner.py` | Added controlled runner mode `ranked-summary-aggregate-prepared-query-batch-float32` with explicit `--aggregate-request-count`. |
| `tests/goal2819_rtnn_batched_prepared_aggregate_contract_test.py` | Guards generic naming, ABI wiring, Python runtime validation, runner exposure, and claim boundary. |

## Intended Measurement

The first pod measurement should be conservative:

1. Rebuild OptiX from clean Git.
2. Verify the batch API returns the same aggregate as the single prepared-query
   path for identical `(radius, k_max)` requests.
3. Measure 32K and 65K uniform rows with `aggregate_request_count > 1`, then
   report both total batch time and per-request amortized time.

The per-request amortized timing must not be compared to a single CuPy call as
if it were a one-request API. The correct claim is narrower: RTDL now has a
generic mechanism to amortize repeated small aggregate requests over resident
inputs. Whether that closes the 32K uniform single-request miss remains a pod
measurement question.

## Claim Boundary

- No public RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No v2.5 release claim is authorized.
- No native app-specific engine customization is introduced.
- No pod performance claim is authorized until clean pod artifacts exist.

Goal2819 is an implementation step toward a generic runtime primitive. It is
not yet a performance conclusion.
