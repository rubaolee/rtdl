# Goal 204: KNN Rows Truth Path

Date: 2026-04-10
Status: planned

## Goal

Build the first executable truth path for `knn_rows`.

This goal covers:

- pure-Python reference execution
- deterministic authored and fixture cases
- a tiny public-facing dataset fixture and loader
- baseline-runner support for `cpu_python_reference`

## Why this goal exists

Goal 203 stopped at DSL/lowering only.

The next honest step is not native closure. It is a trustworthy reference path
that proves the workload contract, row semantics, and dataset wiring before we
claim CPU/oracle or Embree support.

## Required result

This goal is complete when:

- `knn_rows_cpu(...)` exists as a pure-Python truth path
- `run_cpu_python_reference(...)` can execute the new workload
- deterministic authored and fixture cases exist
- the baseline runner can execute the workload on `cpu_python_reference`
- a tiny public fixture exists for bounded external-facing validation
- bounded tests prove ranking, ordering, short-result behavior, and dataset wiring

## Non-goals

This goal does not:

- add native CPU/oracle support
- add Embree support
- add OptiX or Vulkan support
- claim benchmark-grade performance
