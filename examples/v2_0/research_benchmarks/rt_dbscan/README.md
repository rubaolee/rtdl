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
| `rtdl_cpu_rows` | Generic RTDL 3-D fixed-radius neighbor rows, then Python component labels | Same row contract without GPU |
| `partner_spatial_bucket_3d` | Generic partner 3-D spatial-bucket radius-graph components | Current best full DBSCAN continuation |
| `partner_cupy_grid_components_3d` | Generic CuPy device-grid radius-graph components | Strong CUDA-core baseline; no RT cores |
| `optix_core_flags_cupy_grid_components_3d` | OptiX-backend per-query fixed-radius summaries feed CuPy device-grid component continuation | Hybrid uniform-cell CUDA summaries plus CUDA-core continuation; no neighbor-row materialization |
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

## Claim Boundary

- This study can show whether RTDL exposes the right generic primitives for
  RT-DBSCAN-style applications.
- It cannot claim paper reproduction, paper-level speedups, or broad DBSCAN
  acceleration until the benchmark uses representative datasets, OptiX hardware
  timing, and external review.
- The main runtime gaps are explicit: first-class 3-D fixed-radius threshold
  device columns and a reusable device-resident radius-graph component
  continuation that can combine with OptiX output without row materialization.
