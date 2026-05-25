# GPU-RMQ-Style Range Minimum Query Research App

This directory starts the RTDL benchmark-app track for:

- Lara Kreis, Justus Henneberg, Valentin Henkys, Felix Schuhknecht, and Bertil
  Schmidt, **GPU-RMQ: Accelerating Range Minimum Queries on Modern GPUs**,
  arXiv:2604.01811.

The app is now a **research/learner app**, not a promoted benchmark app. Goal2612
added the missing generic device-resident grouped candidate argmin/finalize
primitive and compared RTDL against a direct CUDA sparse-query baseline on an
RTX 3090 pod. RTDL stayed 14-65x slower than direct CUDA query kernels depending
on the workload, so benchmark promotion is rejected for the current design.

The app remains valuable because it documents a real RTDL boundary: Python can
express the paper-style hierarchy and RT lowering, and the native engine can
stay app-agnostic, but the current Python+partner+RTDL data path is not the
right performance shape for RMQ.

## Contract

For an array `A` and inclusive query interval `[left, right]`, return:

- `query_id`;
- `left`;
- `right`;
- the leftmost minimum index in the interval;
- the minimum value.

Tie-breaking is intentionally fixed to the leftmost minimum so CPU, partner, and
future RTDL paths have a strict equality oracle.

## Why This Was Studied

The earlier RTXRMQ paper maps RMQ to ray-triangle closest-hit. GPU-RMQ is more
interesting for RTDL v2.x because it is not only a closest-hit trick: it is a
hierarchical/hybrid approach that uses compact summaries and selects between
CUDA-core-style scans and RT-core-style traversal at different levels.

That made it useful for testing RTDL's Python+partner+RTDL architecture:

- Python owns dataset generation, query contracts, and scheduling policy.
- A partner such as CuPy owns hierarchy construction and scan-heavy work.
- RTDL should only own generic RT primitives if a subpath benefits from
  traversal or closest-hit behavior.
- The native engine must not contain RMQ-specific or GPU-RMQ-specific logic.
- Goal2612 showed that this architecture is not yet benchmark-competitive for
  RMQ without a stronger device-resident continuation mechanism.

## Local Commands

Run from the repository root:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py --mode scope
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py --mode compare_local --dataset random --value-count 4096 --query-count 1024 --max-width 256
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py --mode paper_rt_lowering_reference --dataset repeated --value-count 4096 --query-count 1024 --max-width 256 --block-size 64
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py --mode author_style_compare_local --value-count 4096 --query-count 1024 --author-lr -6 --no-sample
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py --mode local_hierarchical --dataset sawtooth --value-count 262144 --query-count 65536 --max-width 4096 --block-size 64 --no-sample
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\research_benchmarks\gpu_rmq\rtdl_gpu_rmq_benchmark_app.py --mode compare_local
```

## Current Modes

| Mode | Purpose |
| --- | --- |
| `scope` | Emit benchmark boundary and paper relationship. |
| `command_plan` | Emit local and future pod command plan. |
| `author_code_plan` | Emit the lakreis/GPU-RMQ build/run/comparison plan. |
| `author_time_csv` | Parse a `--save-time` CSV emitted by the authors' binary. |
| `author_input_cpu_reference` | Replay authors' saved array/query binaries through the RTDL CPU oracle. |
| `author_style_compare_local` | Run a local distribution-level analogue of the authors' `lr` workload classes. |
| `cpu_reference` | Exact leftmost-argmin CPU oracle. |
| `local_hierarchical` | Exact dependency-light hierarchy path using block summaries plus sparse table over block minima. |
| `compare_local` | Compare local hierarchy path against the CPU oracle. |
| `paper_rt_lowering_reference` | Lower RMQ into paper-style 3-D ray/triangle geometry and run generic RTDL `ray_triangle_closest_hit` rows. |

The `paper_rt_lowering_reference` mode is the RTDL-relevant path. It encodes
array values as triangle x/t distance, maps query intervals to +x rays, and
decodes closest-hit primitive ids back into RMQ argmin rows in Python. A tiny
app-side x offset preserves leftmost tie-breaking without changing value order.
The native engine sees only generic rays and triangles; it does not know RMQ.
Current local execution proves the contract with the CPU generic closest-hit
backend. Goal2599 also built and validated the native OptiX generic
closest-hit path on an NVIDIA RTX A5000 pod, including this RMQ lowering. That
validation authorizes correctness readiness for the generic primitive path, not
RT-core speedup wording.

## Authors Code

The authors' repository is:

- <https://github.com/lakreis/GPU-RMQ>

Inspected HEAD during front-door creation:

```text
86fed1c170b7e41e8ec44e461f7220f87f492893
```

The authors' binary shape is:

```bash
./rtxrmq <n> <q> <lr> <alg>
```

Important algorithm IDs from the README:

| Algorithm | Meaning |
| ---: | --- |
| `1` | CPU HRMQ |
| `2` | full GPU scan |
| `5` | RTXRMQ |
| `16` | GPU-RMQ CL |
| `18` | GPU-RMQ CL in OptiX with RT |
| `19` | GPU-RMQ CL in CUDA |
| `20` | GPU-RMQ VL |
| `21` | GPU-RMQ CL in OptiX without RT |
| `24` | GPU-RMQ CL multi load |

The repository does not ship fixed dataset files. It generates arrays and
queries from `n`, `q`, `lr`, and `--seed`. If exact same-input replay is needed,
use the authors' `--save-input-data` option after patching their hardcoded
`directory_save_aux_data` path in `src/main.cu` to a pod-local directory, then
run:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py \
  --mode author_input_cpu_reference \
  --author-array-bin /path/to/array_n-..._seed-....bin \
  --author-query-bin /path/to/queries_n-..._q-..._lr-..._seed-..._trivCheck-..._randTrivCheck-....bin \
  --author-index-width 32
```

The paper scripts use `q=2^26`, array sizes around `2^20` to `2^31`, and range
distributions `-1`, `-2`, `-3`, and `-6`.

The reusable authors-code runner packet is:

```bash
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action plan
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action clone
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action patch-aux-dir
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action build --optix-home "$OPTIX_HOME"
PYTHONPATH=src:. python3 scripts/goal2595_gpu_rmq_author_runner.py --action run-matrix --lr -3 --lr -6 --alg 2 --alg 5 --alg 16 --alg 20
```

Use `--dry-run` on any runner action to print commands without executing them.

## Promotion Decision

Promotion is rejected for the current RTDL line. Keep this directory as a
research/learner app and design-pressure artifact.

Goal2612 evidence:

- the generic grouped candidate argmin/finalize primitive worked on OptiX;
- all rows matched the CPU reference;
- direct CUDA sparse-query code remained 14-65x faster than RTDL query time;
- author-code comparison is no longer a promotion requirement for this app;
- no public speedup wording is authorized.

Future reconsideration requires a generic device-resident partner/runtime
continuation path, not RMQ-specific native code.
