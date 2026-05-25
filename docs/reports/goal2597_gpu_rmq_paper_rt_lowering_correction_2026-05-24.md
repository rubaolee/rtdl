# Goal2597 GPU-RMQ Paper RT Lowering Correction

Date: 2026-05-24

Status: local contract correction complete; native OptiX evidence still pending.

## Correction

The GPU-RMQ benchmark cannot be closed as a CuPy-only hierarchy benchmark. That
would test a CUDA partner baseline, not RTDL's purpose. The benchmark must use
the paper's RT idea where the RMQ-relevant subpath is expressed as ray tracing:

- encode array values or block-summary values as triangle x/t distance;
- encode query interval membership in the triangle y/z footprint;
- issue +x rays for same-block, left-partial, right-partial, and full-block
  phases;
- use generic closest-hit rows to recover the minimum candidate;
- decode primitive ids to RMQ indices in Python app code.

## Implemented Local Surface

`examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py` now
contains:

- `build_paper_rt_rmq_scene`: app-side construction of paper-style 3-D
  triangles for element and block-summary phases;
- `paper_rt_lowered_rmq`: app-side RMQ scheduling over generic
  `ray_triangle_closest_hit`;
- `paper_rt_lowering_reference` CLI mode.

`src/rtdsl/generic_primitives.py` now exposes
`run_generic_ray_triangle_closest_hit` for app-name-free ray/triangle closest-hit
rows. CPU is available for contract checks. Embree can be used where the native
3-D closest-hit library is built. Native OptiX closest-hit is intentionally
marked not ready instead of faking an RT-core result through CuPy.

## Boundary

This keeps the RTDL engine app-agnostic. The native engine receives only generic
rays and triangles and returns generic closest-hit rows. RMQ-specific block
construction, phase scheduling, tie-breaking policy, and primitive-id decoding
remain in Python app code.

A tiny app-side x offset preserves the benchmark's leftmost-tie RMQ contract
without changing value ordering. This is needed for deterministic tests on
datasets with repeated values; paper random-float workloads normally avoid this
tie case.

## Evidence

Local commands run:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py --mode paper_rt_lowering_reference --dataset random --value-count 64 --query-count 32 --max-width 16 --block-size 8
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py --mode paper_rt_lowering_reference --dataset repeated --value-count 257 --query-count 73 --max-width 64 --block-size 16 --no-sample
PYTHONPATH=src:. python3 - <<'PY'
from examples.v2_0.research_benchmarks.gpu_rmq import rtdl_gpu_rmq_benchmark_app as app
for dataset in ('random','repeated','sawtooth','descending_blocks'):
    for block in (2,4,8,16,31):
        payload = app.run_app(
            'paper_rt_lowering_reference',
            dataset=dataset,
            value_count=97,
            query_count=97,
            seed=123,
            max_width=97,
            block_size=block,
            sample=False,
        )
        assert payload['matches_cpu_reference'], (dataset, block)
print('all_ok')
PY
```

Result: all local correctness checks matched the CPU leftmost-argmin oracle.

Regression checks run after the implementation:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2595_gpu_rmq_author_runner_test -v
python3 -m py_compile src/rtdsl/generic_primitives.py src/rtdsl/__init__.py examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py scripts/goal2595_gpu_rmq_author_runner.py
```

Result: 14 tests passed; syntax checks passed.

## Remaining Work

The source tree now has a generic native OptiX `ray_triangle_closest_hit_3d`
ABI/runtime path with primitive id and hit distance output. The remaining gate
is NVIDIA validation: build the OptiX backend on a suitable pod, run this app's
`paper_rt_lowering_reference` path with `--rt-backend optix`, compare against the
authors' code and CUDA/CuPy baselines, and only then consider RT-core performance
wording.
