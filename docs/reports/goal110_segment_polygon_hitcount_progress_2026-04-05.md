# Goal 110 Segment-Polygon-Hitcount Progress

Date: 2026-04-05
Author: Codex
Status: in_progress

## What is finished

The Goal 110 family-selection phase is complete and the initial workload
closure work has started.

The current implemented progress is:

- the v0.2 flagship family is now fixed as `segment_polygon_hitcount`
- the semantic contract is now explicit in tests:
  - endpoint inside polygon counts as a hit
  - boundary touch counts as a hit
  - edge crossing counts as a hit
  - zero-hit segments remain in the output with `hit_count = 0`
  - overlapping polygons count independently
- one deterministic derived dataset now exists:
  - `derived/br_county_subset_segment_polygon_tiled_x4`
- the baseline runner now supports:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  - `both` (current legacy CPU/Embree parity mode)
- one user-facing example now exists:
  - `examples/rtdl_segment_polygon_hitcount.py`
  - validated from a plain repo checkout with no manual `PYTHONPATH`

## Local validation

Validated locally on this Mac:

- `tests.goal110_segment_polygon_hitcount_semantics_test`
- `tests.goal110_baseline_runner_backend_test`
- `tests.goal10_workloads_test`

Observed result:

- `9` tests
- `OK`
- `2` skipped

Example validation:

- `python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --dataset authored_segment_polygon_minimal`
- `python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --dataset derived/br_county_subset_segment_polygon_tiled_x4`

Known local environment note:

- the native CPU oracle still emits the existing local Mac `geos_c` linker
  noise before skipped tests
- this is not a new Goal 110 regression

## Derived-case evidence

The new derived case currently produces, under the Python reference path:

- rows: `40`
- total hit count: `44`
- nonzero rows: `40`

So the derived case is larger than the basic fixture and already produces a
nontrivial hit-count surface.

## What is still open

Goal 110 is **not closed yet**.

Still required:

- primary backend closure on Embree
- primary backend closure on OptiX
- prepared-path checks on authored and fixture-backed cases
- one final significance proof satisfying the Goal 110 acceptance rule
- one final release-facing report for the closed family package

## Current position

Goal 110 has moved past planning and now has:

- chosen workload family
- explicit semantics
- deterministic authored / fixture / derived cases
- harness support
- user-facing example

The remaining work is backend closure, not scope definition.
