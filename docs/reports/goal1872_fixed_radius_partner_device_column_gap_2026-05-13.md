# Goal1872 - Fixed-Radius Partner Device-Column Gap

Status: needs-implementation

Date: 2026-05-13

## Scope

Goal1872 records the next v2.0 implementation blocker after the
segment/polygon and road-hazard partner rows.

The apps:

- `service_coverage_gaps`
- `event_hotspot_screening`

are built on the generic fixed-radius count-threshold primitive, not on the
ray/triangle any-hit witness contract used by Goals1850-1869.

## Current State

The current fixed-radius OptiX path is host-packed:

- `prepare_optix_fixed_radius_count_threshold_2d(search_points, max_radius=...)`
- `PreparedOptixFixedRadiusCountThreshold2D.run(query_points, radius=..., threshold=...)`
- `PreparedOptixFixedRadiusCountThreshold2D.count_threshold_reached(...)`

Those APIs accept Python/packed point records and call native OptiX through
`PackedPoints`. They do not yet expose a caller-owned Torch/CuPy CUDA column
descriptor path.

## Required v2.0 Contract

Before `service_coverage_gaps` or `event_hotspot_screening` can become true
Python+partner+RTDL app rows, RTDL needs a fixed-radius partner contract with:

- caller-owned query point CUDA columns;
- caller-owned search point CUDA columns or a prepared device-column scene;
- documented stream/lifetime rules;
- partner-owned output columns for either per-query counts or threshold flags;
- Torch reference behavior and CuPy conformance;
- fail-closed metadata that keeps native engine semantics generic:
  `generic_fixed_radius_count_threshold_2d`;
- pod smoke and same-contract timing artifacts.

## Boundary

This goal does not add implementation code. It prevents overclaiming:
`service_coverage_gaps` and `event_hotspot_screening` remain blocked for v2.0
partner-device timing until the fixed-radius device-column contract exists and
is validated on NVIDIA hardware.

No v2.0 release wording, whole-app speedup wording, broad RT-core speedup
wording, or package-install claim is authorized.
