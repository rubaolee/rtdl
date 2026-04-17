# Goal 40 Native CPU Oracle

Date: 2026-04-02

## Goal

Replace the slow Python `run_cpu(...)` simulator with a native C/C++ oracle that preserves the old simulator semantics and remains the project ground-truth reference path.

## Why This Goal Exists

The Python reference simulator is semantically useful but too slow for larger validation runs. The project needs a native oracle that:

- preserves the existing `reference.py` semantics,
- keeps double-precision behavior,
- remains suitable as the correctness oracle,
- and scales materially better than the old Python nested loops.

## Scope

This goal includes:

- a new standalone native oracle library with no Embree dependency
- a Python ctypes runtime wrapper for that oracle
- switching `run_cpu(...)` to the native oracle path
- retaining the old Python reference path for regression checking
- parity tests against the old Python simulator semantics

This goal does not include:

- deleting the old Python reference implementation
- claiming the default dict-return CPU path is now optimal for all output-heavy cases
- replacing the Embree backend

## Acceptance

Goal 40 is accepted if:

- `run_cpu(...)` uses a native oracle path,
- the old Python semantics remain available for parity checks,
- targeted simulator and Embree parity tests pass,
- and the repository records the honest performance boundary of the first slice.
