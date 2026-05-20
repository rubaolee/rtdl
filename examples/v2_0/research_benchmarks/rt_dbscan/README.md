# RT-DBSCAN-Style Study

This directory is the RTDL benchmark-app campaign inspired by:

- Vani Nagarajan and Milind Kulkarni, "RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware," IPDPS 2023.
- DOI: `10.1109/IPDPS54959.2023.00100`
- arXiv: <https://arxiv.org/abs/2303.09655>

The goal is not to clone the paper implementation. The goal is to test whether
RTDL can express the same application shape with generic runtime contracts:

```text
3-D fixed-radius neighbor search -> core-point threshold -> radius-graph components
```

No DBSCAN-specific native ABI is added.

## File

| File | Role |
| --- | --- |
| `rtdl_rt_dbscan_benchmark_app.py` | CLI and Python API for RT-DBSCAN-style 3-D clustering experiments |

## Modes

| Mode | Meaning | RTDL/partner role |
| --- | --- | --- |
| `cpu_reference` | Exact CPU spatial-bucket DBSCAN reference | Correctness oracle |
| `planned_rt_dbscan` | Explicit benchmark-app plan that chooses a measured mode and records why | Plan/explain pattern; not a hidden runtime dispatcher |
| `rtdl_cpu_rows` | Generic RTDL 3-D fixed-radius neighbor rows, then Python component labels | Same row contract without GPU |
| `partner_spatial_bucket_3d` | Generic partner 3-D spatial-bucket radius-graph components | Current best full DBSCAN continuation |
| `partner_cupy_grid_components_3d` | Generic CuPy device-grid radius-graph components | Strong CUDA-core baseline; no RT cores |
| `partner_cupy_prepared_grid_components_3d` | Prepared generic CuPy device-grid radius-graph components | Fair prepared CUDA-core baseline for repeat probes |
| `partner_cupy_prepared_adjacency_components_3d` | Prepared generic CuPy directed radius-graph adjacency stream plus grouped union continuation | Contract prototype for avoiding repeated distance checks after adjacency materialization; no RT cores |
| `optix_core_flags_cupy_grid_components_3d` | OptiX-backend per-query fixed-radius summaries feed CuPy device-grid component continuation | Hybrid uniform-cell CUDA summaries plus CUDA-core continuation; no neighbor-row materialization |
| `optix_rt_core_flags_cupy_grid_components_3d` | OptiX RT count-threshold device columns feed CuPy device-grid component continuation | True RT traversal core flags plus CUDA-core continuation; no neighbor-row materialization |
| `optix_rt_core_flags_cupy_prepared_grid_components_3d` | OptiX RT count-threshold device columns feed a prepared CuPy device-grid component continuation | Same generic contract with reusable grid/order/workspace state for steady-state probes |
| `optix_rt_core_adjacency_cupy_components_3d` | OptiX RT writes a generic directed fixed-radius adjacency stream, then CuPy labels components | First generic RT-produced continuation stream; no DBSCAN-native engine code |
| `optix_rt_core_chunked_adjacency_cupy_components_3d` | OptiX RT writes bounded generic directed fixed-radius adjacency chunks, then CuPy labels components | Memory-bounded stream variant; does not hold the whole edge table at once |
| `optix_rt_core_grouped_stream_cupy_components_3d` | OptiX RT applies generic predicate-grouped union and fallback-candidate capture during traversal, then CuPy labels components | Over-budget dense-stream variant; avoids materializing a full neighbor-index table |
| `optix_rt_core_flags_cupy_microcell_graph_components_3d` | OptiX RT count-threshold device columns feed a clique-safe CuPy microcell component continuation | Experimental all-core fast path; falls back to the CuPy device grid when any point is non-core |
| `partner_core_flags_3d` | Generic partner 3-D fixed-radius core flags only | Core-point phase, not full DBSCAN |
| `optix_prepared_rows` | Prepared OptiX-backend 3-D fixed-radius neighbor rows, then Python component labels | Prepared uniform-cell CUDA path; materializes rows |

## First Correctness Run

Run from the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode cpu_reference --dataset tiny --include-rows
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\research_benchmarks\rt_dbscan\rtdl_rt_dbscan_benchmark_app.py --mode cpu_reference --dataset tiny --include-rows
```

Then compare the generic RTDL row contract:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode rtdl_cpu_rows --dataset tiny --include-rows
```

## Partner Run

On a CUDA machine with CuPy or PyTorch installed:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_spatial_bucket_3d --dataset clustered3d --point-count 4096 --partner cupy --no-validation
```

The current partner path returns exact labels, but its sparse bucket index is
still host-built. Treat it as a correct transitional continuation, not as a true
zero-copy claim.

For the fair CUDA-core baseline, use the device-grid mode:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_cupy_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This path builds and probes the grid on the CUDA device with CuPy raw kernels.
It is intentionally not an RT-core claim; it is the baseline RTDL must compare
against before saying the RT path is useful.

For repeated-run fairness, also measure the prepared CuPy baseline:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_cupy_prepared_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

The one-shot CLI still includes preparation time. The repeat probe prepares the
CuPy grid once and is the fair baseline for steady-state comparisons against
the prepared RT bridge.

For the generic adjacency-stream prototype, use:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_cupy_prepared_adjacency_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This path materializes a device-resident directed fixed-radius adjacency stream
once, then labels components from that stream. It is a contract prototype for
the next continuation primitive, not an RT-core speedup claim.

## Hybrid OptiX + Partner Run

The current strongest bridge mode uses the OptiX backend's prepared uniform-cell
CUDA path to compute per-query fixed-radius summary rows, then hands core
flags/counts to the CuPy device-grid continuation:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_core_flags_cupy_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This avoids materializing every neighbor row. It still materializes one summary
row per point and copies those summaries into CuPy, so it is a bridge step, not
the final paper-style device-output continuation. It is not an RT-core claim.

For the true RT-core count-threshold bridge, use:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_flags_cupy_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This path writes threshold-capped neighbor counts and core flags directly into
CuPy device columns from a generic prepared 3-D fixed-radius RT traversal. It
still uses the CuPy device-grid continuation to label components, so it is an
RTDL composition primitive rather than a DBSCAN-specific native engine.

For a prepared continuation variant, use:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_flags_cupy_prepared_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

The one-shot app mode prepares the CuPy grid inside the call, so its public
elapsed time is not a pure steady-state speedup. The repeat probe
`scripts/goal2403_rt_dbscan_repeat_probe.py` is the fair way to measure reuse:
it prepares the OptiX scene, CuPy point columns, cell ids, sorted order,
unique-cell ranges, and output workspaces once, then repeats only the generic
RT count-threshold pass and component-label continuation.

Programmatic users can prepare the same generic composite directly:

```python
with rt.prepare_optix_cupy_radius_graph_components_3d(points, radius=radius) as prepared:
    result = rt.radius_graph_components_3d_optix_cupy_prepared_partner_columns(
        prepared,
        min_neighbors=min_neighbors,
        return_metadata=True,
    )
```

This is still not a DBSCAN-specific primitive. It is a prepared fixed-radius
graph-component contract over a 3-D point set: OptiX writes threshold-capped
core/count columns, then CuPy labels generic radius-graph components.

For the generic RT-produced adjacency-stream path, use:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_adjacency_cupy_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This path first asks the prepared OptiX scene for exact fixed-radius degree
counts, builds a device offset column, then asks OptiX to fill a caller-owned
CuPy `neighbor_indices` stream. CuPy consumes that stream for grouped union and
labels. The contract is generic radius-graph adjacency, not DBSCAN-specific
native code. It is also memory bounded: dense inputs can create very large
directed edge streams, so use the prepared-grid mode when a dataset does not
need materialized edges.

For a memory-bounded variant of the same contract, use:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_chunked_adjacency_cupy_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This path counts all degrees once, then fills and consumes adjacency chunks.
It is designed for dense rows where a single giant `neighbor_indices` array is
the wrong memory contract. It captures one core-neighbor candidate per border
point during the chunked union pass, so final labels can be assigned without a
second RT adjacency fill.

Advanced users can also bound each adjacency chunk by directed-edge count:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_chunked_adjacency_cupy_components_3d --dataset clustered3d --point-count 32768 --chunk-adjacency-edge-budget 8000000 --no-validation
```

The chunk planner first counts exact fixed-radius degrees, then chooses chunk
ranges that obey both `max_chunk_points` and the requested directed-edge budget.
This is a memory-control knob, not a speedup claim.

For the generic grouped-stream continuation path, use:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_grouped_stream_cupy_components_3d --dataset clustered3d --point-count 65536 --no-validation
```

This path keeps the native ABI generic: OptiX receives caller-owned predicate,
parent, and fallback-candidate device columns, then applies fixed-radius hit
traversal to update those columns without creating a giant neighbor-index
array. The core predicate is built from threshold-capped counts at
`min_neighbors`, not exact full degree counts. Goal2457 made this the explicit
continuation-plan branch when the full stream no longer fits the directed-edge
budget. Full adjacency remains the preferred branch when it fits; chunked
adjacency remains available as a manual memory-control diagnostic.

For the experimental all-core microcell continuation, use:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_flags_cupy_microcell_graph_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This path keeps the same RT core-flag phase, then tries a generic microcell
component continuation. The microcells are small enough that each occupied
microcell is internally connected. If any point is non-core, the adapter falls
back to the CuPy device-grid continuation and records the fallback in metadata.

## OptiX Run

On an NVIDIA machine with `librtdl_optix` built:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_prepared_rows --dataset clustered3d --point-count 4096 --no-validation
```

This is the current prepared OptiX-backend row path. It is useful evidence that
RTDL can drive the generic 3-D fixed-radius contract needed by DBSCAN, but it is
not the RT-core paper path and it still materializes neighbor rows before
cluster expansion. The paper-facing target is stronger: device-resident core
flags from a true RT traversal path and device-resident grouped/union
continuation.

## Datasets

The built-in datasets are synthetic stressors:

| Dataset | Purpose |
| --- | --- |
| `tiny` | Small exact two-cluster correctness fixture |
| `clustered3d` | Clustered 3-D density workload |
| `road3d` | Road/trajectory-like narrow 3-D manifold |
| `ngsim_dense` | Dense compact 3-D workload inspired by the paper's dense-data discussion |

They are not substitutes for the paper's 3DRoad, Porto, 3DIono, or NGSIM data.
Any paper-scale claim needs a separate reviewed run with recorded data sources.

## Explicit Plan Mode

The benchmark also exposes:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode planned_rt_dbscan --dataset clustered3d --point-count 131072 --no-validation
```

This explicit benchmark-app plan is not a hidden dispatcher. It records an
`execution_plan` in the JSON metadata, including the selected mode and reason.
After the Goal2425 prepared-baseline fairness pass and the Goal2427 pod smoke,
the evidence-bounded policy is:

- compact `ngsim_dense` rows use the prepared pure-CuPy continuation;
- `road3d` rows below the measured 524k crossover use the prepared pure-CuPy
  continuation;
- `clustered3d` rows below the measured 65k crossover use the prepared
  pure-CuPy continuation;
- larger clustered rows and larger road-shaped rows use the prepared RT-count
  plus prepared CuPy-grid bridge.

The plan mode is a learner-visible pattern for choosing between generic RTDL
contracts and partner continuations. It is not a release claim and not a
paper-reproduction claim.

## Explicit Continuation Plan Mode

The benchmark also exposes a second explicit plan for the adjacency-continuation
contract added after Goals 2431/2433/2435:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode planned_rt_dbscan_continuation --dataset clustered3d --point-count 32768 --no-validation
```

This is also a plan/explain path, not hidden dispatch. It records:

- the estimated directed fixed-radius adjacency edge count;
- the explicit edge budget;
- whether the full stream fits that budget;
- the selected generic contract;
- the evidence goals used for the decision.

Current policy:

- `tiny` stays on the CPU reference fixture;
- if the estimated full directed adjacency stream fits the budget, use
  `optix_rt_core_adjacency_cupy_components_3d`;
- if the stream exceeds the budget, use
  `optix_rt_core_chunked_adjacency_cupy_components_3d`.

Goal2452 raised the default directed-edge budget to 160,000,000 after pod
evidence showed that the full adjacency stream is much faster than chunking for
the 32,768-point clustered row when it fits GPU memory. Pass a smaller
`--adjacency-edge-budget`, such as `64000000`, when you specifically want to
force the chunked memory-bounded branch for comparison.

This planner is for continuation experiments where exact adjacency is required.
It does not replace the one-shot `planned_rt_dbscan` policy, and it does not
authorize a paper-level speedup or release claim.

## Claim Boundary

- This study can show whether RTDL exposes the right generic primitives for
  RT-DBSCAN-style applications.
- It cannot claim paper reproduction, paper-level speedups, or broad DBSCAN
  acceleration until the benchmark uses representative datasets, OptiX hardware
  timing, and external review.
- The main runtime gap is explicit: a reusable device-resident radius-graph
  component continuation that can combine with OptiX output without redoing
  candidate-pair traversal in the partner continuation.
