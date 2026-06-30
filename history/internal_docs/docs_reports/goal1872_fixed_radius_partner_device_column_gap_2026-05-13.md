# Goal1872 - Fixed-Radius Partner Device-Column Gap

Status: partially-narrowed

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

The current fixed-radius native OptiX path is host-packed:

- `prepare_optix_fixed_radius_count_threshold_2d(search_points, max_radius=...)`
- `PreparedOptixFixedRadiusCountThreshold2D.run(query_points, radius=..., threshold=...)`
- `PreparedOptixFixedRadiusCountThreshold2D.count_threshold_reached(...)`

Those APIs accept Python/packed point records and call native OptiX through
`PackedPoints`. They do not yet expose a caller-owned Torch/CuPy CUDA column
descriptor path.

Goal1873 narrows the gap by adding a partner-reference/conformance path:

- `fixed_radius_count_threshold_2d_partner_columns(...)`
- `service_coverage_gap_flags_partner_columns(...)`
- `event_hotspot_flags_partner_columns(...)`

Those functions operate on caller-owned PyTorch/CuPy point columns, but they do
not call the native RTDL engine. They are protocol reference work, not RT-core
evidence.

Goal1875 narrows the native gap further by adding an OptiX fixed-radius
device-column bridge:

- `fixed_radius_count_threshold_2d_optix_partner_device_columns(...)`
- `rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns`
- `rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns`

That bridge is accepted only for the generic fixed-radius count-threshold
subpath. App-level `service_coverage_gaps` and `event_hotspot_screening`
adapters, timing rows, and external review still remain before those apps can
be accepted as v2.0 performance evidence.

## Required v2.0 Contract

Before `service_coverage_gaps` or `event_hotspot_screening` can become native
Python+partner+RTDL app rows with RT-core timing evidence, RTDL still needs a
fixed-radius native device-column bridge with:

- caller-owned query point CUDA columns;
- caller-owned search point CUDA columns or a prepared device-column scene;
- documented stream/lifetime rules;
- partner-owned output columns for either per-query counts or threshold flags;
- Torch reference behavior and CuPy conformance;
- fail-closed metadata that keeps native engine semantics generic:
  `generic_fixed_radius_count_threshold_2d`;
- pod smoke and same-contract timing artifacts.

## Boundary

This goal prevents overclaiming: `service_coverage_gaps` and
`event_hotspot_screening` have a partner reference path after Goal1873 and a
generic OptiX fixed-radius device-column bridge after Goal1875, but they remain
blocked as app-level RT-core v2.0 timing rows until their app adapters, timing
artifacts, and external reviews exist.

No v2.0 release wording, whole-app speedup wording, broad RT-core speedup
wording, or package-install claim is authorized.
