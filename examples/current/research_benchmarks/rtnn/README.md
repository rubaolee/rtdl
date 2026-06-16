# RTNN Neighbor-Search Benchmark

This directory is the formal front door for the existing RTNN benchmark
campaign. It wraps the RTNN scripts and evidence into the research-benchmark
tree.

The ANN candidate-quality example is exposed only as a helper submode
because it shares top-k quality and candidate-threshold contracts. It is not
the benchmark identity.

The target paper family is RTNN-style hardware ray-tracing neighbor search. The
public RTNN implementation is treated as an optional diagnostic baseline because
its materialization pipeline is not the same as RTDL's ranked-summary contract.

## What This Benchmark Owns

| Contract | RTDL surface | Boundary |
| --- | --- | --- |
| ANN candidate quality | 2-D candidate-subset top-1 rerank and exact full-set comparison | not an ANN index or training phase |
| ANN candidate threshold | prepared fixed-radius candidate-coverage decision | not nearest-neighbor ranking |
| RTNN-shaped ranked summary | prepared 3-D fixed-radius bounded ranked-summary rows | not full RTNN paper reproduction |

## Local Commands

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode scope
PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode ann_cpu_quality --copies 1
PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode rtnn_known_results
PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode prepared_session_reuse_idiom --point-count 16 --radius 0.02 --k 8
RTDL_OPTIX_LIBRARY=build/librtdl_optix.so PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode prepared_optix_ranked_summary --point-count 65536 --radius 0.02 --k 50 --repeat 3 --query-batch-size 65536 --distribution uniform
RTDL_OPTIX_LIBRARY=build/librtdl_optix.so PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode prepared_ranked_summary_raw --backend optix --point-count 65536 --radius 0.02 --k 50 --repeat 3 --query-batch-size 65536 --distribution uniform
RTDL_EMBREE_LIBRARY=build/librtdl_embree.so PYTHONPATH=src:. python examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode prepared_ranked_summary_raw --backend embree --point-count 65536 --radius 0.02 --k 50 --repeat 3 --query-batch-size 65536 --distribution uniform
```

## GPU Evidence

The promoted benchmark reuses the completed Goal2388 pod evidence:

- RTDL prepared OptiX ranked-summary rows.
- CuPy CUDA-core all-pairs baseline for the same ranked-summary contract.
- Optional official RTNN rows on the same RTX A5000 pod.

The current app front door also exposes
`--mode prepared_optix_ranked_summary`, which runs the generic prepared
OptiX fixed-radius ranked-summary aggregate through the existing RTNN runner.
It generates a deterministic synthetic point set and returns pure JSON with the
runner progress captured in `runner_progress`. This is the command to use when
you want an executable current RTDL/OptiX ranked-summary app route, not just the
evidence summary.

For backend-to-backend comparison, use `--mode prepared_ranked_summary_raw` with
`--backend optix` or `--backend embree`. That mode keeps the output contract the
same on both sides: prepared 3-D fixed-radius bounded ranked-summary raw rows.
The runner payload includes `raw_ranked_summary_aggregate` with row-count,
bounded-neighbor, nearest/kth checksum, and distance-sum fields so comparison
reports can prove they timed equivalent work.

The `--mode prepared_session_reuse_idiom` command is a non-performance teaching
path. It invokes `get_or_prepare_explicit_session` twice against a caller-owned
`ExplicitPreparedSessionCache` and returns the visible `miss`/`put`/`hit` event
log. It does not run the OptiX benchmark path and does not authorize speedup,
general zero-copy/device-residency, or automatic partner/backend-selection claims.

Goal4381 adds the current large same-contract aggregate evidence: exact float64
RTDL/OptiX native aggregate is `10.14x` faster than exact Embree on the
1,048,576-point uniform row and `11.80x` faster on the 262,144-point shell row.
Goal4443 adds app-front-door resident graph-bridge evidence at 1,048,576 search
points with 65,536-query batches and repeat=1000: CuPy and Numba both validate
the same signature, use CUDA graph replay and same-stream partner reduction, and
measure about `5ms` hot median per batch. Exact float64 aggregate rows and
float32 graph-bridge rows must remain separate.

Goal4459 extends the resident graph-bridge evidence from the uniform M47 row to
a heavier clustered 1,048,576-point scene with 65,536-query batches and
repeat=1000. CuPy measures `130.079ms` hot median per batch and Numba measures
`131.442ms`; both rows preserve the same signature, use CUDA graph replay and
same-stream partner reduction, and pass the no-hidden-column-copy hot-window
gate. This is RTDL-internal app-bridge evidence, not a full RTNN paper row.

The important boundary is that RTDL exact aggregate and app graph-bridge rows
are RTDL-internal same-contract evidence; the official RTNN rows are diagnostic
unless a future goal proves output-contract equivalence.

## Engine Boundary

No ANN-specific or RTNN-specific native ABI is added. The native engine sees
generic fixed-radius neighbor, ranked-summary, prepared-search, and partner
top-k contracts. Candidate selection, approximation policy, external-code
adaptation, and paper-comparison interpretation stay in Python and reports.
