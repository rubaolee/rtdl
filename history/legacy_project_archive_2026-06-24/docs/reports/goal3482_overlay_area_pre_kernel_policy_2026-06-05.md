# Goal3482 - Overlay-Area Pre-Kernel Policy

## Status

Implemented locally.

Goal3482 addresses the main risk called out by the Goal3480 Claude review:
before writing a GPU scalar-area kernel, RTDL needs an explicit tolerance,
topology, and scratch-capacity policy.

## Policy

The policy lives in:

- `src/rtdsl/v2_8_overlay_area_continuation_contract.py`

It adds:

- total-area tolerance: `max(1e-8, 1e-9 * abs(expected_total_area))`;
- row-area absolute tolerance: `1e-10`;
- topology input status: `requires_prepared_simple_polygon_component_payload`;
- unsupported topology status: `unsupported_topology_not_canonicalized`;
- scratch policy: `tile_triangle_pairs_fail_closed_on_tile_or_accumulator_overflow`.

## Interpretation

The GPU scalar-area continuation should not silently repair invalid topology.
Raw invalid, self-intersecting, hole-bearing, or multipolygon inputs must be
canonicalized into prepared simple polygon component payloads before entering
the kernel. The kernel should process triangle pairs in bounded tiles and report
fail-closed status on unsupported topology or scratch/accumulator overflow.

## Boundary

This is pre-kernel policy metadata, not a runtime kernel and not a release
claim. It does not authorize public speedup wording, broad RT-core speedup
wording, true-zero-copy wording, paper reproduction claims, hidden partner
selection, hidden dispatch, app-specific engine logic, or full overlay
completion claims.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3482_overlay_area_pre_kernel_policy_test`

