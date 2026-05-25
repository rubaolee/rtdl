# RTDL v2.x Research Benchmarks

This directory is for serious application studies, not first-run examples. Each
subdirectory shows how a user can write a real RTDL v2.x program, compare it
with external baselines, and keep the performance claim boundary precise.

The benchmark apps are reconstruction instruments. A study can intentionally
cover only part of a paper or application when that slice is enough to expose a
missing RTDL primitive, memory contract, partner boundary, prepared execution
model, or result contract. The success condition is the language/runtime design
pressure extracted from the app, not full paper-system reproduction.

Run commands from the repository root with source-tree usage:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/<study>/<script>.py
```

On Windows PowerShell, use:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\research_benchmarks\<study>\<script>.py
```

## Studies

| Directory | Purpose | Start here |
| --- | --- | --- |
| `hausdorff_xhd/` | Exact and RT-assisted Hausdorff distance study informed by X-HD techniques; includes current scale-aware grouped traversal defaults | `hausdorff_xhd/README.md` |
| `spatial_rayjoin/` | RayJoin-style spatial join workloads with current first-hit/nearest-boundary evidence | `spatial_rayjoin/README.md` |
| `rt_dbscan/` | RT-DBSCAN-style 3-D density clustering study over generic fixed-radius/component contracts | `rt_dbscan/README.md` |
| `robot_collision/` | Robot-collision-style static-scene plus batched transformed query-geometry study; CPU reference only in Goal2480 | `robot_collision/README.md` |
| `raydb_style/` | RayDB-style columnar grouped aggregate contract study; CPU reference plus Embree/OptiX count-sum parity over existing generic columnar payloads | `raydb_style/README.md` |
| `barnes_hut/` | RT-BarnesHut-style hierarchical N-body reconstruction study; includes bucketized Morton/DFS aggregate tree rows, hierarchical opening frontier, local exact CPU baseline, and guarded OptiX/paper-code boundaries | `barnes_hut/README.md` |
| `librts_spatial_index/` | LibRTS-style mutable spatial-index study for PPoPP 2025 point/range query semantics, WKT fixture interchange, and first authors-code OptiX evidence | `librts_spatial_index/README.md` |
| `rtnn/` | RTNN-style neighbor-search study over candidate quality, prepared fixed-radius ranked summaries, CuPy baseline rows, and optional public RTNN diagnostics | `rtnn/README.md` |
| `triangle_counting/` | Closed bounded RT-Graph/SIGMETRICS 2025 triangle-counting benchmark; paper-dataset evidence exists, with largest-dataset scalability accepted as a segmented/streamed-lowering follow-up | `triangle_counting/README.md` |
| `gpu_rmq/` | Demoted GPU-RMQ-style RMQ research/learner app over exact CPU oracle, hierarchy-style local contract, paper-style generic closest-hit RT lowering, and generic grouped candidate argmin; Goal2612 shows the current RTDL design is not benchmark-competitive against direct CUDA sparse-query code | `gpu_rmq/README.md` |

## How To Read Results

- Treat these as reproducible research harnesses, not universal speedup claims.
- CPU-only commands are useful for correctness and contract checks.
- OptiX timing needs a CUDA-capable machine with `librtdl_optix` built and
  `RTDL_OPTIX_LIBRARY` set when the library is outside the default path.
- A result can show an RTDL program is useful for a workload without claiming
  that every phase is RT-core accelerated.
- Public performance language should cite the exact script, dataset, backend,
  method, commit, and hardware.

## Recommended Flow

1. Run the CPU reference command in the study README.
2. Run the Embree command to check the same RTDL contract on the CPU RT backend.
3. On an NVIDIA pod or workstation, build OptiX and run the OptiX command.
4. Compare JSON fields such as `parity_vs_cpu_python_reference`,
   `matches_exact_reference`, `elapsed_sec`, `rt_core_accelerated`, and
   `claim_boundary`.

The benchmark directories intentionally keep paper-inspired work separate from
the ordinary learner examples so new users can learn RTDL without being pulled
into historical performance debates.

For the post-robot-collision benchmark-app selection rule and RayDB scoping
boundary, see
[`Goal2492 Benchmark-App Reconstruction Principle`](../../../docs/reports/goal2492_benchmark_app_reconstruction_principle_and_raydb_scope_2026-05-22.md).
