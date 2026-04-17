# Goal 198: Fixed-Radius Neighbors Truth Path

Date: 2026-04-10
Status: planned

## Goal

Build the first executable truth path for `fixed_radius_neighbors`.

This goal covers:

- pure-Python reference execution
- deterministic authored and fixture cases
- a tiny public-facing dataset fixture and loader
- baseline-runner support for `cpu_python_reference`

## Why this goal exists

Goal 197 stopped at DSL surface only.

The next honest step is not native closure. It is a trustworthy reference path
that proves the workload contract, row semantics, and dataset wiring before we
claim CPU/oracle or Embree support.

## Required result

This goal is complete when:

- `fixed_radius_neighbors_cpu(...)` exists as a pure-Python truth path
- `run_cpu_python_reference(...)` can execute the new workload
- deterministic authored and fixture cases exist
- the baseline runner can execute the workload on `cpu_python_reference`
- a tiny public fixture exists for bounded external-facing validation
- bounded tests prove ordering, truncation, and dataset wiring

## Non-goals

This goal does not:

- add lowering support
- add native CPU/oracle support
- add Embree support
- add OptiX or Vulkan support
- claim benchmark-grade performance
