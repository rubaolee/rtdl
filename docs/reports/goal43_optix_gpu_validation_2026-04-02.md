# Goal 43 Report: OptiX GPU Validation Ladder

## Summary

Goal 43 expanded the first OptiX GPU bring-up on `192.168.1.20` into a small
multi-workload validation ladder using the C oracle as ground truth.

The host is a valid first OptiX machine:

- GPU: `NVIDIA GeForce GTX 1070`
- driver: `580.126.09`
- working OptiX runtime on the host: `9.0`

The validated execution path used:

- OptiX SDK headers pinned to `v9.0.0`
- `RTDL_OPTIX_PTX_COMPILER=nvcc`
- `RTDL_NVCC=/usr/bin/nvcc`

## Harness

New harness:

- [goal43_optix_validation.py](/Users/rl2025/rtdl_python_only/scripts/goal43_optix_validation.py)

New test:

- [goal43_optix_validation_test.py](/Users/rl2025/rtdl_python_only/tests/goal43_optix_validation_test.py)

The harness runs representative tiny authored cases across all six current
local workloads, plus two slightly larger derived cases for `lsi` and `pip`,
and compares:

- `run_cpu(...)`
- `run_optix(...)`

## Results on `192.168.1.20`

### Parity-clean

- `lsi` authored minimal: parity `true`
- `pip` authored minimal: parity `true`
- `ray_tri_hitcount` authored minimal: parity `true`
- `segment_polygon_hitcount` authored minimal: parity `true`
- `point_nearest_segment` authored minimal: parity `true`
- derived `lsi` tiled x8: parity `true`
- derived `pip` tiled x8: parity `true`

### Parity-failing

- `overlay` authored minimal: parity `false`

Exact observed mismatch:

- CPU:
  - `{'left_polygon_id': 300, 'right_polygon_id': 301, 'requires_lsi': 1, 'requires_pip': 0}`
- OptiX:
  - `{'left_polygon_id': 300, 'right_polygon_id': 301, 'requires_lsi': 1, 'requires_pip': 1}`

So the current first OptiX correctness bug after bring-up is:

- `overlay` containment composition is too aggressive on the authored minimal
  case

## Runtime lifecycle note

When the process exits normally after successful OptiX calls, the host can still
hit a post-success segmentation fault during teardown. This does not invalidate
the workload results already produced, but it does mean process cleanup is not
yet stable enough for large unattended validation suites.

Observed practical workaround during bring-up:

- use short-lived validation scripts
- for the tiny smoke scripts, force early process exit after printing results

This lifecycle bug remains open.

## Current boundary

What is now proven:

- RTDL OptiX executes real workloads on the GTX 1070 host
- the first GPU host is usable for continued backend development
- 7 of 8 current validation targets are parity-clean under the current
  bring-up configuration

What is not yet proven:

- stable default NVRTC PTX generation on this host
- correctness of `overlay`
- cleanup stability after normal interpreter shutdown
- any serious OptiX performance characterization

## Next goal

The next correct OptiX goal is:

- fix the `overlay` parity bug
- fix the post-success teardown segfault
- then rerun the Goal 43 ladder before attempting broader OptiX performance or
  larger data

## Deferred Claude audit plan

After the later OptiX fix round closed the two blocked issues above, a final
Claude audit is still required as a follow-up review artifact.

That deferred Claude audit should specifically check:

- the final `overlay` parity fix in
  `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`
- the shutdown-stability fix that prevents the post-success teardown crash
- the validated remote rerun showing all 8 Goal 43 targets parity-clean on
  `192.168.1.20`
- the current host/runtime boundary:
  - OptiX runtime `9.0`
  - SDK headers pinned to `v9.0.0`
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/bin/nvcc`

The deferred Claude audit should end with an explicit yes/no decision on
whether the corrected Goal 43 state is acceptable for continued OptiX
development before broader GPU testing begins.
