# Iteration 4 Implementation Report

Date: `2026-03-31`
Author: `Codex`

## What Was Implemented

The first Goal 15 implementation slice is now present:

- native `lsi` executable:
  - [goal15_lsi_native.cpp](/Users/rl2025/rtdl_python_only/apps/goal15_lsi_native.cpp)
- native `pip` executable:
  - [goal15_pip_native.cpp](/Users/rl2025/rtdl_python_only/apps/goal15_pip_native.cpp)
- comparison harness:
  - [goal15_compare_embree.py](/Users/rl2025/rtdl_python_only/scripts/goal15_compare_embree.py)
- regression test:
  - [goal15_compare_test.py](/Users/rl2025/rtdl_python_only/tests/goal15_compare_test.py)
- build entry:
  - [Makefile](/Users/rl2025/rtdl_python_only/Makefile)

## Scope Boundary

This slice does **not** attempt to create a fully independent geometric algorithm stack.

Instead, it creates:

- standalone C++ front ends with no RTDL DSL involvement
- direct invocation of the native Embree C API already exposed by `src/native/rtdl_embree.cpp`
- the same synthetic inputs pre-generated once for both native and RTDL paths

That means the current Goal 15 result isolates:

- RTDL/Python host-path overhead

more than it isolates:

- differences in native geometric implementation

This is an intentional and honest boundary for the first comparison slice.

## Correctness Results

The current small/medium deterministic fixtures produce non-empty outputs.

### LSI

- native pair count: `24,000`
- RTDL CPU pair count: `24,000`
- RTDL Embree pair count: `24,000`
- native vs RTDL CPU: `match`
- native vs RTDL Embree: `match`

### PIP

- native pair count: `120`
- RTDL CPU pair count: `120`
- RTDL Embree pair count: `120`
- native vs RTDL CPU: `match`
- native vs RTDL Embree: `match`

## Timing Results

Measured wall-clock results from the comparison harness:

### LSI

- native total seconds: `0.004039875`
- RTDL CPU total seconds: `0.0390471660066396`
- RTDL Embree total seconds: `0.030882917111739516`

### PIP

- native total seconds: `0.000565042`
- RTDL CPU total seconds: `0.07858041697181761`
- RTDL Embree total seconds: `0.02115466701798141`

## Important Interpretation

These timings should currently be interpreted as:

- **native executable path vs RTDL host path**

not as:

- a pure algorithmic comparison between two fully independent Embree implementations

That is because the native executables currently call the same underlying C++ Embree implementation already used by RTDL's local backend.

## Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal15_compare_test`
- `PYTHONPATH=src:. python3 scripts/goal15_compare_embree.py`

## Review Ask To Claude

Claude should now review:

- whether the current slice satisfies the revised Goal 15 plan honestly
- whether the boundary is documented clearly enough
- whether the correctness/performance claims are appropriately limited
- and whether this first Goal 15 slice can be accepted
