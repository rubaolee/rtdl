# Goal4381 RTNN Aggregate Large-Scale Evidence

Date: 2026-06-14

## Conclusion

RTNN is no longer a "no effect" row when we use the right RTDL contract. The old v2.14 row timed ranked-summary row materialization and Python-side aggregation on a 65,536-point input. This run uses native aggregate output on large RTNN-shaped point sets.

On exact same-contract aggregate rows, RTDL OptiX is 10.14x faster than RTDL Embree on the 1,048,576-point uniform input and 11.80x faster on the 262,144-point shell/surface-like input. On the best RTDL OptiX route with prepared query points, CUDA graph replay, and same-stream CuPy partner continuation, the measured per-repeat runtime is 89.85x faster than Embree on the 1M uniform input and 47.36x faster on the shell input, but that best route is float32 and has boundary-level deltas versus the exact float64 aggregate.

This preserves RTDL's architecture. The native engine exposes generic fixed-radius 3D ranked-summary aggregate primitives; the app composes prepared search, prepared query points, CUDA graph replay, and a CuPy same-stream partner continuation. No RTNN-specific native ABI was added.

## Dataset Status

The exact paper datasets are not present on the pod. The project manifest already names the intended paper-family sources as KITTI-derived point sets, Stanford 3D scan point sets, and N-body/Millennium-style snapshots, but their status is `planned` and no `RTDL_KITTI_SOURCE_ROOT` or equivalent source root is configured on this pod.

The public RTNN repository describes the runnable input format as one 3D point per CSV line and includes `samplepc.txt` as an example, but it does not ship the full paper dataset package in the repository front door. Therefore this evidence is large RTNN-shaped stress evidence, not a paper-exact dataset reproduction.

Sources checked:

- RTNN repository README: https://github.com/horizon-research/rtnn
- RTNN arXiv abstract: https://arxiv.org/abs/2201.01366

## What Changed

Added a native Embree aggregate route for the same fixed-radius ranked-summary contract:

- `rtdl_embree_fixed_radius_neighbors_3d_ranked_summary_aggregate_run`
- `PreparedEmbreeFixedRadiusNeighbors3D.aggregate_ranked_summary(...)`
- runner support for `--backend embree --result-mode ranked-summary-aggregate`

The Embree aggregate route no longer materializes one summary row per query before aggregating. It also reuses per-worker temporary buffers inside the native loop.

## Hardware And Inputs

Pod: NVIDIA RTX 4000 Ada Generation, driver 550.127.08.

Uniform input:

- Points/search: 1,048,576
- Queries: same point file
- Radius: 0.02
- K max: 50
- Query batch size: 65,536
- Exact bounded neighbor count: 37,037,834

Shell/surface-like input:

- Points/search: 262,144
- Queries: same point file
- Radius: 0.01
- K max: 50
- Query batch size: 65,536
- Exact bounded neighbor count: 2,502,058

## Performance Matrix

Times are median per repeat after one prepared search structure has been created. Load, pack, and prepare are shown separately because RTNN-style steady-state neighbor search should not hide them inside traversal time.

| Dataset | Path | Exactness | Query residency | Repeat | Median per repeat | Approx repeat total | Speedup vs Embree | Result check |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Uniform 1M | Embree native aggregate | exact float64 | host query batches | 3 | 1.5127s | 4.5381s | 1.00x | exact reference |
| Uniform 1M | OptiX native aggregate | exact float64 | query upload per repeat | 100 | 0.1492s | 14.9152s | 10.14x | same count/checksums; distance sum differs only at floating accumulation roundoff |
| Uniform 1M | OptiX prepared graph + same-stream CuPy | float32 best path | device-resident prepared queries | 100 | 0.0168s | 1.6836s | 89.85x | 15 bounded-neighbor delta out of 37,037,834 |
| Shell 262K | Embree native aggregate | exact float64 | host query batches | 5 | 0.1004s | 0.5022s | 1.00x | exact reference |
| Shell 262K | OptiX native aggregate | exact float64 | query upload per repeat | 100 | 0.0085s | 0.8509s | 11.80x | same count/checksums; distance sum differs only at floating accumulation roundoff |
| Shell 262K | OptiX prepared graph + same-stream CuPy | float32 best path | device-resident prepared queries | 100 | 0.0021s | 0.2121s | 47.36x | 2 bounded-neighbor delta out of 2,502,058 |

## Phase Reading

Uniform 1M exact Embree:

- Native traversal across 16 batches: 1.4871s
- End-to-end per-repeat wall across 16 batches: 1.5126s

Uniform 1M exact OptiX:

- Candidate count pass across 16 batches: 0.1354s
- Query upload across 16 batches: 0.0062s
- Row download: 0.00017s
- Exact refine: 0.00022s
- Median per-repeat wall: 0.1492s

The exact OptiX row is therefore not being dominated by Python aggregation or row materialization; it is dominated by the RT traversal/candidate-count pass, which is the intended hardware comparison.

The prepared graph + same-stream row removes per-repeat query upload and host summary materialization. Its phase subfields currently report the graph route as a graph replay path rather than a fully decomposed kernel timeline, so the trusted number is the measured per-repeat wall time plus the metadata proving `prepared_cuda_graph_replay=True`, `same_stream_partner_consumer=True`, and no partner fallback.

## Public Wording Boundary

Safe wording:

> On large RTNN-shaped fixed-radius ranked-summary aggregate inputs, RTDL OptiX is 10-12x faster than RTDL Embree for the exact float64 same-contract aggregate, and the best device-resident RTDL OptiX+CuPy graph route reaches 47-90x faster than Embree with float32 boundary-level deltas.

Do not say yet:

- Do not claim paper-exact RTNN reproduction. The paper datasets are not present on this pod.
- Do not mix the float32 prepared graph row into the exact float64 same-contract row.
- Do not claim RTDL beats the RTNN authors' implementation on paper datasets from this evidence alone.

## Artifacts

- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14/rtnn_uniform_1m_embree_aggregate_exact_repeat3.json`
- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14/rtnn_uniform_1m_optix_aggregate_exact_repeat100.json`
- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14/rtnn_uniform_1m_optix_best_prepared_graph_same_stream_repeat100.json`
- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14/rtnn_shell_262k_embree_aggregate_exact_repeat5.json`
- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14/rtnn_shell_262k_optix_aggregate_exact_repeat100.json`
- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14/rtnn_shell_262k_optix_best_prepared_graph_same_stream_repeat100.json`

