# Goal 6 Spec

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-6-python-simulator
Repo: /Users/rl2025/rtdl_python_only
Baseline Commit: 3569438d984d695795eb9c1903f728b03a065dd1

## Goal

Add a Python-based RT simulator for the currently supported RTDL workloads so
that RTDL programs can run end to end on this Mac without GPU execution.

## In Scope

- Execute the currently supported workload surface:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`
- Run compiled RTDL kernels against Python-side input data.
- Produce actual result records, not only plans and generated skeletons.
- Reuse the current CPU reference semantics as the execution truth.
- Keep the interface clean enough that users can run RTDL kernels directly from
  Python.
- Add tests, examples, and docs for the simulator.

## Out of Scope

- Performance optimization
- GPU execution
- New workloads
- New precision machinery beyond current `float_approx`
- Numerical robustness beyond the current reference implementations

## Proposed Design

Add a small execution layer that:

1. compiles a kernel
2. validates that provided inputs match the kernel contract
3. converts Python-side records into reference geometry objects
4. dispatches to the correct CPU reference implementation
5. returns materialized result rows

## Target API

The expected user-facing shape is a function in RTDL such as:

- `rt.run_cpu(kernel_fn, **inputs)`

Possible supporting helpers:

- dataset/record normalization from dictionaries or dataclass objects
- `CompiledKernel` execution helpers if helpful

## Success Criteria

- A user can execute each currently supported RTDL workload on CPU.
- Results are returned as concrete rows for all four workload families.
- Invalid/missing inputs fail with clear errors.
- Tests cover both happy paths and validation failures.
- Demo/docs show that RTDL now has a runnable local execution mode.
