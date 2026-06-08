# Goal4015 Partition Guidance Immutability

Date: 2026-06-08

## Verdict

`accept`

Goal4015 closes the minor hardening note from the Goal4013 Claude review:
`V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE` is now exported
as a read-only mapping.

## What Changed

The fixed-radius graph component front-door module now wraps the source
partition guidance in `MappingProxyType`. Public `describe` and `plan`
functions return fresh plain dict copies through
`_hybrid_partition_guidance_metadata`, so callers can serialize or inspect the
metadata without mutating the source contract for future calls.

This does not change the runtime route. `grouped_stream` remains the only
supported executable strategy, and `partition_convergence_hybrid` remains a
fail-closed candidate requiring native implementation.

## Validation

Added:

- `tests/goal4015_partition_guidance_immutability_test.py`

The test verifies:

- the exported guidance mapping rejects item assignment;
- mutating the dict returned by `describe_v2_8_fixed_radius_graph_component_front_door`
  does not affect later descriptions or the source mapping;
- mutating the dict returned by a candidate `plan_v2_8_fixed_radius_graph_component_continuation`
  does not affect later plans;
- the source and report record the read-only mapping plus fresh-copy boundary.

## Boundary

Goal4015 is a metadata safety hardening step. It does not add a native ABI,
does not change the accepted grouped-stream runtime route, does not authorize
public speedup wording, and does not authorize release, broad RT-core,
whole-app, true-zero-copy, hidden-dispatch, automatic-partner, or
app-specific-engine claims.
