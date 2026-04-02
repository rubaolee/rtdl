# Goal 15 Report: Native C/C++ + Embree vs RTDL + Embree

## Scope

Goal 15 compares:

- standalone native C++ executables using Embree
- the current RTDL + Embree local runtime

for the current comparison workloads:

- `lsi`
- `pip`

The current slice focuses on:

- correctness agreement
- host-path performance difference

It does **not** yet claim a fully independent native geometric algorithm stack, because the native executables currently call the same Embree C API implementation already exposed by RTDL.

## Result Summary

### LSI

- native pair count: `24,000`
- RTDL CPU pair count: `24,000`
- RTDL Embree pair count: `24,000`
- native vs RTDL CPU: `match`
- native vs RTDL Embree: `match`

Timing:

- native total seconds: `0.004039875`
- RTDL CPU total seconds: `0.0390471660066396`
- RTDL Embree total seconds: `0.030882917111739516`

### PIP

- native pair count: `120`
- RTDL CPU pair count: `120`
- RTDL Embree pair count: `120`
- native vs RTDL CPU: `match`
- native vs RTDL Embree: `match`

Timing:

- native total seconds: `0.000565042`
- RTDL CPU total seconds: `0.07858041697181761`
- RTDL Embree total seconds: `0.02115466701798141`

## Interpretation

The current comparison demonstrates:

- the native executable front ends agree with RTDL CPU and RTDL Embree on the tested fixtures
- the native executable front ends avoid a noticeable amount of Python/RTDL host overhead

The current comparison does **not** yet demonstrate:

- that a fully independent native geometric implementation would produce the same performance or behavior
- that the current native timings represent only Embree traversal cost

So the honest conclusion is:

- Goal 15 currently validates correctness parity for the tested fixtures
- and provides a first measurement of native-wrapper versus RTDL host-path overhead

## Main Artifacts

- native executables:
  - `apps/goal15_lsi_native.cpp`
  - `apps/goal15_pip_native.cpp`
- harness:
  - `scripts/goal15_compare_embree.py`
- test:
  - `tests/goal15_compare_test.py`
- generated JSON:
  - `build/goal15_compare/goal15_compare.json`
