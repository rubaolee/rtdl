# Goal 43 Report: OptiX GPU Validation Ladder

## Summary

Goal 43 expanded the first OptiX GPU bring-up on `192.168.1.20` into a small
multi-workload validation ladder using the C oracle as ground truth.

This report records the initial Goal 43 pre-fix state. Later fixes for
`overlay` parity and teardown stability are captured in:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal43_claude_audit_2026-04-02.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal46_optix_county_zipcode_parity_2026-04-02.md`

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

### Initial parity-clean

- `lsi` authored minimal: parity `true`
- `pip` authored minimal: parity `true`
- `ray_tri_hitcount` authored minimal: parity `true`
- `segment_polygon_hitcount` authored minimal: parity `true`
- `point_nearest_segment` authored minimal: parity `true`
- derived `lsi` tiled x8: parity `true`
- derived `pip` tiled x8: parity `true`

### Initial parity-failing

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

## Later Claude audit result

The deferred Claude audit for this Goal 43 corrected state later completed in:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal43_claude_audit_2026-04-02.md`

That later audit ended with:

- Claude: `APPROVE`
- accepted `overlay` parity fix
- accepted shutdown-stability fix
- confirmed the validated rerun remained `8/8` parity-clean on `192.168.1.20`
- accepted continued OptiX development on the trusted `nvcc` PTX path
