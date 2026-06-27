# Goal603 External Review: v0.9.3 Native-Coverage Contract

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6 (external)
Verdict: **ACCEPT**

## What was reviewed

- `src/rtdsl/apple_rt_runtime.py` (modified)
- `tests/goal603_apple_rt_native_contract_test.py` (new)
- `docs/reports/goal603_v0_9_3_apple_rt_native_contract_2026-04-19.md`

## Contract correctness

The three-predicate native set is consistent across every layer:

| Layer | Native predicates |
| --- | --- |
| `APPLE_RT_NATIVE_PREDICATES` frozenset | ray_triangle_closest_hit, ray_triangle_hit_count, segment_intersection |
| `_APPLE_RT_SUPPORT_NOTES` keys | same three |
| `apple_rt_predicate_mode()` special-case branches | same three |
| Test assertions (`test_current_native_rows_are_explicit`) | same three |

No predicate outside this set receives `native_candidate_discovery != "no"`. The
default path in `_apple_rt_support_notes()` returns `"no"` / `"full_cpu_reference_compat"` /
`native_shapes=()` for all 15 remaining predicates. `test_compatibility_rows_are_not_marked_hardware_backed`
exhaustively checks this property.

## False-native risk: none found

`run_apple_rt()` dispatches to hardware only via explicit `predicate_name ==` guards
followed by `isinstance` shape checks (for the ray cases). Any predicate that fails
all three guards hits the `native_only` fence:

```python
if native_only:
    raise NotImplementedError(...)
return _run_cpu_python_reference_from_normalized(compiled, normalized)
```

A new workload added to `APPLE_RT_COMPATIBILITY_PREDICATES` without a corresponding
entry in `_APPLE_RT_SUPPORT_NOTES` and a new dispatch arm in `run_apple_rt()` will
automatically get mode `cpu_reference_compat`, `native_candidate_discovery="no"`, and
`native_shapes=()`. The matrix cannot silently overclaim hardware backing.

## Shape-dependent edge case

`ray_triangle_hit_count` is correctly handled:

- `_APPLE_RT_SUPPORT_NOTES` marks it `shape_dependent` / `supported_for_3d_only`
- `run_apple_rt()` gates native dispatch on `isinstance(ray, _CanonicalRay3D)`
- For 2D inputs, control falls through to the `native_only` fence
- `test_native_only_still_rejects_2d_shape_dependent_hitcount` asserts `NotImplementedError`
  for exactly this path — the test exercises `Ray2D` + `Triangle` inputs, confirming
  the shape guard works

## Matrix completeness

`APPLE_RT_COMPATIBILITY_PREDICATES` contains 18 entries. `apple_rt_support_matrix()` iterates
`sorted(APPLE_RT_COMPATIBILITY_PREDICATES)`, so row count is deterministic and the test
assertion `len(rows) == 18` will catch any silent additions or removals.

## Minor observations (non-blocking)

- `segment_intersection` dispatch in `run_apple_rt()` (lines 579-580) skips the `native_only`
  check because it returns before reaching it. This is correct behavior — the predicate is
  always hardware-backed for the supported shape — but the asymmetry with the ray branches
  is worth noting for future maintainers adding shape-conditional segment support.
- `_CanonicalSegment` is imported as `Segment` from `.reference`; the matrix documents it as
  `Segment2D/Segment2D`. This is a benign naming-convention mismatch (documentation only).

## Summary

Goal603 achieves its stated scope: the v0.9.3 honesty boundary is now machine-checkable. No
new workload is marked hardware-backed. The `native_only` guard closes the false-positive
path for all current and future compatibility predicates. Tests cover the contract
exhaustively including the shape-dependent edge case.
