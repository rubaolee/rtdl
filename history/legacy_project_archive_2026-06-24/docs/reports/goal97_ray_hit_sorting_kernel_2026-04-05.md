# Goal 97 Report: Ray-Hit Sorting Kernel

Date: 2026-04-05
Status: available-backend parity closure complete

## Objective

Use RTDL to implement and validate a non-join integer-sorting test based on
geometric hit counts.

## Implemented shape

Workload family:

- `lsi`

Accepted implemented geometry:

- build segment for value `x_i`:
  - `(x_i, 0)` to `(x_i, x_i + 1)`
- probe segment for value `x_i`:
  - `(0, x_i + 0.5)` to `(F, x_i + 0.5)`

This gives the exact hit-count law for nonnegative integers:

- `hit_count(x_i) = number of values x_j such that x_j >= x_i`

## Added files

- example/helpers:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_goal97_ray_hit_sorting.py`
- demo script:
  - `/Users/rl2025/rtdl_python_only/scripts/goal97_ray_hit_sorting_demo.py`
- test suite:
  - `/Users/rl2025/rtdl_python_only/tests/goal97_ray_hit_sorting_test.py`

## Verification

The RTDL-derived ordering is checked against:

- direct formula-based hit counts
- stable Python `sorted(...)`
- a separate quicksort-style reference implementation

Duplicates are handled explicitly with:

- `original_index` as a deterministic tie-breaker

## Local validation

Passed:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile \
  examples/rtdl_goal97_ray_hit_sorting.py \
  scripts/goal97_ray_hit_sorting_demo.py \
  tests/goal97_ray_hit_sorting_test.py
```

Passed:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal97_ray_hit_sorting_test
```

Result on this Mac:

- `11` tests
- `OK`
- `4` skipped

Current skips:

- native oracle on this Mac because of the known local `geos_c` link issue
- hardware backends when unavailable in the current environment

## Linux backend validation

Goal 97 was then transferred to Linux and executed on the available backend
stack.

Passed:

```bash
cd /home/lestat/work/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal97_ray_hit_sorting_test
```

Result on Linux:

- `11` tests
- `OK`

Verified small accepted case:

- `cpu_python_reference`
- `cpu`
- `embree`
- `vulkan`
- `optix`

All five produced the same hit counts and the same ascending/descending stable
sorted outputs for the accepted small duplicate-containing case:

- values:
  - `(3, 1, 4, 1, 5, 0, 2, 5)`
- hit counts:
  - `(4, 7, 3, 7, 2, 8, 5, 2)`
- ascending:
  - `(0, 1, 1, 2, 3, 4, 5, 5)`
- descending:
  - `(5, 5, 4, 3, 2, 1, 1, 0)`

## Backend note

Goal 97 exposed a real OptiX `lsi` backend defect: the OptiX `lsi` kernel
source depended on `stdint.h` in the NVRTC compile path. On the Linux host,
that caused the first OptiX Goal 97 run to fail even though OptiX itself was
otherwise installed.

That defect was repaired in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`

The fix removed the device-kernel dependency on `stdint.h` for the `lsi`
kernel and restored OptiX execution for this RTDL slice.

## Current position

Goal 97 now exists as a real RTDL capability slice with available-backend
closure:

- non-join
- integer-only
- duplicate-safe
- backend-portable in execution on the available Linux stack
- independently verifiable with ordinary sorting references
- useful as a test of user-authored RTDL programs outside the main spatial-join
  storyline

This is a correctness/demo goal, not a performance goal.
