# Hausdorff / X-HD-Style Study

This directory shows how a v2.x user can implement Hausdorff distance with
RTDL plus partner code, then compare that program with CPU, CUDA, and CuPy
baselines. The current RTDL/OptiX path is informed by
X-HD-style ideas: threshold search, witness extraction, grouping, and reducing
the amount of pairwise work that must survive to the continuation phase.

The study is deliberately honest: it does not claim that every Hausdorff input
beats every CUDA implementation. It gives a concrete language/runtime program,
correctness checks, and reproducible commands for the exact claim being tested.

## Files

| File | Role |
| --- | --- |
| `rtdl_hausdorff_distance_app.py` | Small release-facing Hausdorff application over RTDL nearest rows |
| `rtdl_hausdorff_v2_function.py` | Main function and CLI for one-method exact/RT-assisted runs |
| `rtdl_hausdorff_v2_language_lab.py` | Multi-method comparison harness with metadata and correctness checks |
| `rtdl_hausdorff_v2_user_benchmark.py` | Helper code for OpenMP, CUDA C++, CuPy RawKernel, and RTDL partner baselines |

## What The Program Computes

Given two non-empty 2D point sets `A` and `B`, the exact undirected Hausdorff
distance is:

```text
max(max_{a in A} min_{b in B} distance(a,b),
    max_{b in B} min_{a in A} distance(b,a))
```

The exact benchmark paths return:

- `distance`: the Hausdorff value.
- `direction`: whether the witness comes from `A -> B` or `B -> A`.
- `source_index` and `target_index`: the witness point pair.
- `elapsed_sec`: wall-clock time for the measured method.

## First Correctness Run

Use a small CPU/CuPy-friendly run first:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py --points-a 256 --points-b 256 --method cupy_rawkernel --compare
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\research_benchmarks\hausdorff_xhd\rtdl_hausdorff_v2_function.py --points-a 256 --points-b 256 --method cupy_rawkernel --compare
```

If CuPy is not installed, use the portable RTDL/user path or the small app:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

## One-Method Runs

Run exact CUDA/CuPy-style baselines:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py --points-a 8192 --points-b 8192 --method cupy_rawkernel --compare --json-out scratch/hausdorff_cupy.json
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py --points-a 8192 --points-b 8192 --method cupy_grouped_grid_rawkernel --compare --json-out scratch/hausdorff_cupy_grid.json
```

Run the RTDL v2.x user CUDA continuation path:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py --points-a 8192 --points-b 8192 --method rtdl_v2_user_cuda --compare --json-out scratch/hausdorff_rtdl_user_cuda.json
```

Run an RTDL/OptiX witness path on an NVIDIA machine:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py --points-a 8192 --points-b 8192 --method rtdl_rt_grouped_seeded_pruned_nearest_witness --rt-backend optix --compare --json-out scratch/hausdorff_rtdl_optix.json
```

Grouped RT witness methods choose a scale-aware target group size by default:
small point sets keep 64 target points per group, while larger X-HD-style rows
use coarser powers of two up to 8192. Use `--target-points-per-group` when you
need an exact reproduction of a published sweep, and `--seed-sample-count` to
control the sample pass used by `rtdl_rt_grouped_seeded_pruned_nearest_witness`.

## Multi-Method Lab

The lab script runs several methods and records metadata that says whether the
method uses RTDL, a partner library, RT cores, and exact output.

Small local run:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py --points-a 1024 --points-b 1024 --method cupy_rawkernel --method rtdl_v2_user_cuda --json-out scratch/hausdorff_lab_local.json
```

OptiX pod/workstation run:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py --points-a 16384 --points-b 16384 --method cupy_grouped_grid_rawkernel --method rtdl_rt_grouped_reduced_nearest_witness --method rtdl_rt_grouped_adaptive_nearest_witness --json-out scratch/hausdorff_lab_optix.json
```

## Method Guide

| Method | Uses RTDL | Uses partner | Uses RT cores | Exact value | Purpose |
| --- | --- | --- | --- | --- | --- |
| `openmp_cpu` | no | no | no | yes | Multi-threaded CPU baseline |
| `cuda_cpp` | no | no | no | yes | Standalone CUDA C++ baseline |
| `cupy_rawkernel` | no | CuPy | no | yes | CUDA-core RawKernel baseline |
| `cupy_grouped_grid_rawkernel` | no | CuPy | no | yes | CUDA-core baseline with grid/group structure |
| `rtdl_v2_user_cuda` | yes | CuPy | no | yes | RTDL rows/columns plus user continuation |
| `rtdl_rt_threshold_search` | yes | no | yes on OptiX | no, interval | Radius decision search, useful for seeding |
| `rtdl_rt_nearest_witness` | yes | no | yes on OptiX | yes | RTDL/OptiX nearest witness extraction |
| `rtdl_rt_grouped_nearest_witness` | yes | no | yes on OptiX | yes | X-HD-style grouped witness traversal |
| `rtdl_rt_grouped_reduced_nearest_witness` | yes | no | yes on OptiX | yes | Grouped traversal plus device-side max-distance reduction |
| `rtdl_rt_grouped_seeded_pruned_nearest_witness` | yes | no | yes on OptiX | yes | X-HD-style seed lower bound, threshold flags, and exact unsafe-subset reduction |
| `rtdl_rt_grouped_adaptive_nearest_witness` | yes | no | yes on OptiX | yes | Adaptive grouped traversal with shrinking active work |

## Interpreting JSON

Check these fields before quoting a result:

- `primary.distance` or `results.<method>.distance_for_compare`: measured value.
- `matches_primary` or `matches_exact_reference`: correctness against the
  exact reference used by the run.
- `metadata.uses_rt_cores`: whether the method intends to use OptiX RT cores.
- `metadata.exact_value`: whether the method returns an exact Hausdorff value
  or a threshold interval.
- `elapsed_sec`: timing for that method on that machine.

## Claim Boundary

- `rtdl_v2_user_cuda` is an RTDL v2.x program, but it is CUDA-core partner
  continuation, not RT-core acceleration.
- `rtdl_rt_threshold_search` uses RTDL/OptiX traversal but returns a bounded
  interval, not the exact Hausdorff value.
- Exact RTDL/OptiX Hausdorff claims should use an exact witness method such as
  `rtdl_rt_grouped_seeded_pruned_nearest_witness`,
  `rtdl_rt_grouped_reduced_nearest_witness`, or
  `rtdl_rt_grouped_adaptive_nearest_witness`, cite the dataset and hardware,
  and include correctness evidence.
- Do not use this directory to claim that RTDL universally beats X-HD or every
  optimized CUDA implementation.

## Typical Workflow For A New Dataset

1. Convert the two point sets to contiguous `Nx2` numeric arrays.
2. Start with `cupy_rawkernel` or `openmp_cpu` to get a trusted exact value.
3. Run `rtdl_v2_user_cuda` to check the Python+partner+RTDL contract.
4. On OptiX hardware, run one exact RT witness method.
5. Compare distance, witness indices, elapsed time, method metadata, commit,
   and hardware before writing any performance conclusion.
