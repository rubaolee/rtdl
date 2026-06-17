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

Goal4460 closes the app-bridge shell distribution gap. The generic M19
ranked-summary graph bridge now accepts `uniform`, `clustered`, and `shell`;
the M64 shell row uses the same 1,048,576-point / 65,536-query / repeat=1000
contract and measures `38.588ms` CuPy hot median per batch and `39.267ms`
Numba hot median per batch. This keeps shell as RTDL-internal distribution
evidence, not a synthetic substitute for an official RTNN paper dataset.

Goal4498 defines the RTNN paper dataset target matrix: `KITTI-1M`,
`KITTI-6M`, `KITTI-12M`, `KITTI-25M`, `Bunny-360K`, `Dragon-3.6M`,
`Buddha-4.6M`, `NBody-9M`, and `NBody-10M`. These labels are not yet
acquired as exact repo inputs. Use `rtnn_paper_dataset_targets()` when planning
paper-dataset work, and do not report bounded KITTI packages or synthetic
uniform/shell/clustered rows as paper reproduction.

Goal4499 adds the KITTI bounded-family recipe gate. Use
`write_kitti_paper_family_recipe_manifest()` or
`plan_kitti_paper_family_recipe()` after `RTDL_KITTI_SOURCE_ROOT` points at a
KITTI raw/Velodyne source tree. A ready recipe may feed same-contract author
RTNN, RTDL OptiX, and Embree/CPU comparison, but it remains
`bounded_family_recipe_not_exact_paper_recipe` until the paper's exact KITTI
frame ids and merge/truncation rule are frozen.

Goal4500 adds the same-input RTDL gate for that recipe. Use
`write_kitti_paper_family_recipe_csv()` to export the same bounded KITTI CSV,
then run the exact float64 ranked-summary aggregate contract on RTDL OptiX and
RTDL Embree. This runs the RTDL side of the same-input comparison; count,
nearest-id checksum, and distance-sum signatures match, while a tie-sensitive
kth-id checksum caveat remains. Author RTNN still needs a follow-on
adapter/build run on the same CSV before any author-vs-RTDL wording.

The important boundary is that RTDL exact aggregate and app graph-bridge rows
are RTDL-internal same-contract evidence; the official RTNN rows are diagnostic
unless a future goal proves output-contract equivalence.

## Engine Boundary

No ANN-specific or RTNN-specific native ABI is added. The native engine sees
generic fixed-radius neighbor, ranked-summary, prepared-search, and partner
top-k contracts. Candidate selection, approximation policy, external-code
adaptation, and paper-comparison interpretation stay in Python and reports.
