# Benchmark App Walkthrough

Status: current v3.0 source-tree tutorial.

Goal: see a complete Python+RTDL+CuPy/Numba benchmark-app shape.

This tutorial uses the RT-DBSCAN-style app because it shows the full learning
ladder:

```text
CPU oracle -> RTDL row contract -> CuPy continuation -> Numba continuation
-> optional OptiX RT-core bridge
```

The app is inspired by RT-DBSCAN, but the engine still exposes generic
fixed-radius and grouped-stream contracts. No DBSCAN-specific native ABI is
added.

## 1. Start With The CPU Oracle

Linux/macOS:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode cpu_reference --dataset tiny --include-rows
```

Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\current\research_benchmarks\rt_dbscan\rtdl_rt_dbscan_benchmark_app.py --mode cpu_reference --dataset tiny --include-rows
```

The CPU oracle tells you what the app is supposed to compute.

## 2. Run The RTDL CPU Row Contract

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode rtdl_cpu_rows --dataset tiny --include-rows
```

This is still not a GPU performance run. It teaches the typed row contract.

## 3. Run A CuPy Partner Continuation

CUDA machine only:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_cupy_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

CuPy is the CUDA-array baseline and can use RawKernel code. That is useful for
performance comparison, but it means the app author owns that custom code.

## 4. Run A Numba Partner Continuation

CUDA machine only:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_numba_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

Numba is the Python-source partner reference. It is useful when the user wants
custom GPU logic without writing CuPy RawKernel code.

## 5. Run The Prepared Numba Route

CUDA machine only:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_numba_prepared_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

Prepared routes are better for repeated workloads because setup can be reused.

## 6. Optional OptiX RT-Core Bridge

OptiX machine only:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode optix_rt_core_flags_numba_prepared_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
```

This route asks OptiX to produce threshold-capped fixed-radius core flags, then
uses the selected partner to continue component labeling. It is the benchmark
shape a user should study when learning how Python, RTDL, RT cores, and a
partner fit together.

## What You Should Notice

- The app names DBSCAN concepts in Python.
- The RTDL engine sees generic fixed-radius and grouped-stream contracts.
- CuPy and Numba are explicit choices, not hidden dispatch.
- Correctness starts with a CPU oracle.
- Performance claims require command, hardware, dataset, backend, partner, and
  validation details.

## Next

Read the full benchmark app reference:

- [RT-DBSCAN-Style Study](../../examples/current/research_benchmarks/rt_dbscan/README.md)
- [Benchmark Partner Reference Matrix](../../docs/learn/benchmark_partner_reference_matrix.md)
