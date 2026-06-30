# Goal4045 Partition Component Signature Preview

Date: 2026-06-08

## Purpose

Goal4045 adds a generic component-size-signature continuation for the
fixed-radius `partition_convergence_hybrid` candidate.

Goal4041 showed that the current device ambiguous-union path is correct but
does not deserve default promotion as a full-label route. One reason is that the
full component-label preview still materializes compact labels on the host even
when partition union work happened on the device.

Many benchmark and validation paths only need a component-size signature, not a
full per-point label column. Goal4045 therefore adds:

`build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d`

The function consumes the same generic fixed-radius partition summary, performs
safe-full plus connected ambiguous partition union on the device, then computes
component sizes from device roots using CuPy. It returns the compact signature
instead of full labels.

## Contract

Inputs:

- generic 3-D point rows;
- radius and partition cell factor;
- optional reused partition summary;
- `ambiguous_union_execution="cupy_partition_points"`.

Outputs:

- `component_size_signature`: sorted component sizes;
- metadata preserving partition counts, safe/ambiguous status counts, skip
  reason for zero-ambiguous rows, and all claim-boundary flags.

This is not a DBSCAN-specific function. It is a generic fixed-radius graph
component summary continuation.

## Boundary

This is an executable preview, not a promoted default route. It does not add a
native ABI, does not choose partners automatically, does not add app-specific
native-engine logic, does not authorize release wording, does not authorize
public speedup wording, does not authorize broad RT-core wording, does not
authorize whole-app wording, and does not authorize true-zero-copy wording.

