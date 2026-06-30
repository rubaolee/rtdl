# Goal1845 OptiX Partner Witness Output Contract

Date: 2026-05-13
Status: `accept-with-boundary`

## Purpose

Goal1845 starts the correct next step after Goal1843/Goal1844: preserve hit
identity at the partner-owned output boundary instead of trying to reconstruct
identity from one boolean any-hit flag per ray.

## Change

Added a narrow OptiX prepared any-hit ABI:

```text
rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses
```

The contract writes two partner-owned CUDA `uint32` output columns:

- `witness_ray_ids`
- `witness_primitive_ids`

Each output row corresponds to one input ray. `witness_primitive_ids` uses
`0xFFFFFFFF` as the no-hit sentinel.

Python exposes this through:

```python
rt.pack_optix_ray_any_hit_2d_device_witness_outputs(...)
scene.write_device_any_hit_witnesses(...)
```

The validator requires both output columns to be one-dimensional contiguous
`uint32` buffers on the same CUDA device as the partner-owned ray columns.

## Boundary

This is a first-hit witness contract. It preserves identity for the first
any-hit primitive selected by OptiX, but it is not the full multi-hit
segment/polygon row collector required to exactly reproduce
`segment_polygon_anyhit_rows`.

This means the path is suitable for the next app-level adapter experiment, but
the full rows contract still needs a bounded all-witness output design before
RTDL can claim an app-level v2.0 replacement for every
`segment_polygon_anyhit_rows` row.

## Release State

v2.0 release readiness remains `needs-more-evidence`.

No pod validation was run for Goal1845. The local tests validate the ABI surface,
Python packet validation, and claim boundaries. Hardware evidence must still be
collected on an NVIDIA pod before this contract can be counted as execution
evidence.
