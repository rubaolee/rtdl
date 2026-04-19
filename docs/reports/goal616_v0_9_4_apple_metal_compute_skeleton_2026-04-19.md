# Goal616: v0.9.4 Apple Metal Compute Runtime Skeleton

Date: 2026-04-19

Status: accepted with 2-AI consensus (Codex + Gemini 2.5 Flash bounded review).

## Scope

Goal616 implements the foundational Apple Metal compute path required by the v0.9.4 Apple graph/DB plan.

This goal does not mark any graph or DB workload as Apple native, Apple GPU-backed, or Apple native-assisted. It only proves that the existing Apple backend library can also compile and dispatch a Metal compute kernel, exchange buffers with Python, and return deterministic results.

## Implemented Surface

Native entry point:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `rtdl_apple_rt_run_u32_add_compute(...)`

Python wrapper:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `apple_rt_compute_u32_add(left, right)`

Public export:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`

Test:

- `/Users/rl2025/rtdl_python_only/tests/goal616_apple_rt_compute_skeleton_test.py`

## What The Kernel Proves

The kernel is intentionally minimal:

```text
uint32 left[i] + uint32 right[i] -> uint32 out[i]
```

It validates the pieces needed by later v0.9.4 DB/graph work:

- Metal default device acquisition.
- Metal command queue creation.
- Runtime Metal shader compilation.
- Compute pipeline creation.
- Shared buffer upload and readback.
- Dispatch over `thread_position_in_grid`.
- Threadgroup width bounded to at least 1 and at most the pipeline's `maxTotalThreadsPerThreadgroup`.
- Error propagation to the Python ctypes wrapper.
- Native allocation and release through the existing Apple RT free path.

## Validation

Build:

```bash
make build-apple-rt
```

Result: passed.

Direct Goal616 tests:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal616_apple_rt_compute_skeleton_test -v
```

Result:

```text
Ran 5 tests in 0.283s
OK
```

Focused Apple regression suite:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal616_apple_rt_compute_skeleton_test tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal603_apple_rt_native_contract_test -v
```

Result:

```text
Ran 20 tests in 0.102s
OK
```

Python syntax check:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal616_apple_rt_compute_skeleton_test.py
```

Result: passed.

## Honesty Boundary

This is an Apple GPU compute skeleton, not an Apple MPS RT graph/DB implementation.

The current graph/DB rows remain compatibility-only until later goals implement and validate their lowering:

- Goal617: `conjunctive_scan`
- Goal618: `grouped_count` and `grouped_sum`
- Goal619: `bfs_discover`
- Goal620: `triangle_match`

No performance claim is made for Goal616. Its value is architectural readiness and correctness of the command/buffer path.

## Codex Verdict

Accept as the implementation half of Goal616.

Reason: the native and Python paths are narrow, deterministic, locally tested, and do not overclaim workload coverage. Goal616 should be called closed only after external AI review accepts the same boundary.

## External Review

External review record:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal616_external_review_2026-04-19.md`

Gemini 2.5 Flash returned `ACCEPT` on a bounded evidence review. Goal616 is accepted as a compute-skeleton gate only; it does not close graph/DB native Apple support.
