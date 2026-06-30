# Goal1994 AABB Pair Payload Adapter

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

Goal1993 moved the polygon extent continuation from an app-local CuPy RawKernel
into a reusable `aabb_pair_overlap_summary_2d_partner_columns` helper. One
small design debt remained: the example still had a local function that converted
the identity-preserving pair payload table into CuPy columns.

Goal1994 promotes that handoff into the public partner adapter.

## What Changed

The partner adapter now exposes:

```text
aabb_pair_payload_to_partner_columns(...)
```

It accepts caller-supplied arrays for:

```text
left_index, right_index,
left_min_x, left_min_y, left_max_x, left_max_y, left_area,
right_min_x, right_min_y, right_max_x, right_max_y, right_area
```

and returns Torch or CuPy partner-owned columns plus metadata describing the
generic AABB pair-payload contract. The polygon control example now calls this
public adapter before `aabb_pair_overlap_summary_2d_partner_columns`; the
example-local `_pair_extent_partner_columns` helper is gone.

## Boundary

This is still a generic 2D AABB pair payload and summary contract. It does not claim arbitrary polygon clipping, exact GIS topology, or a broader RT-core polygon speedup. It also does not customize the native RTDL engine.

## Validation

Local validation passed:

```text
py -3 -m unittest tests.goal1994_aabb_pair_payload_adapter_test \
  tests.goal1993_aabb_pair_overlap_partner_summary_test \
  tests.goal1953_control_apps_cupy_rawkernel_v2_test

py -3 scripts\goal1908_v2_local_preflight.py
```
