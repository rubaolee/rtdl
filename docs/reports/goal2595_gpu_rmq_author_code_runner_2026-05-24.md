# Goal2595 GPU-RMQ Authors-Code Runner

Date: 2026-05-24

Status: local runner packet and benchmark plumbing. This is not pod evidence,
not a full GPU-RMQ reproduction, and not public speedup wording.

## Purpose

Goal2595 turns the lakreis/GPU-RMQ authors repository into a repeatable future
pod comparison target for the RTDL GPU-RMQ benchmark app.

The authors repository is:

- `https://github.com/lakreis/GPU-RMQ`
- inspected commit: `86fed1c170b7e41e8ec44e461f7220f87f492893`

The repository does not ship fixed static datasets. It generates arrays and
queries from `n`, `q`, `lr`, and `--seed`. The right comparison policy is
therefore:

- compare using the authors' workload parameters and seeds;
- use `--save-time` CSV for timing rows;
- use `--save-input-data` only when same-input replay is required;
- replay saved input binaries through RTDL's `author_input_cpu_reference` mode.

## Added Surfaces

- `examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py`
  now includes `author_style_compare_local`, `author_code_plan`,
  `author_time_csv`, and `author_input_cpu_reference` modes.
- `scripts/goal2595_gpu_rmq_author_runner.py` provides `plan`, `clone`,
  `patch-aux-dir`, `build`, and `run-matrix` actions.
- Tests cover command construction, authors CSV parsing, saved-input binary
  replay, and local author-style parity against the CPU oracle.

## Pod Command Shape

From the repo root:

```bash
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action plan
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action clone
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action patch-aux-dir
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action build --optix-home "$OPTIX_HOME"
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action run-matrix --lr -3 --lr -6 --alg 2 --alg 5 --alg 16 --alg 20
```

Use `--dry-run` to print commands without executing.

## Boundary

This runner does not add RTDL native engine functionality. It exists to make
future evidence collection reproducible. The authors build may require CUDA
12.9+, OptiX 8, OpenMP, and the HRMQ library under `hrmq/`, as stated by the
authors README.
