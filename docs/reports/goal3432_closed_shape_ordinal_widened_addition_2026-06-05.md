# Goal3432 Closed-Shape Ordinal Widened Addition

**Date:** 2026-06-05  
**Status:** implemented; pod validation pending  
**Scope:** close the residual low-risk arithmetic note from Goal3429 Claude review

## Purpose

Goal3429 accepted Goals 3427 and 3428, but kept one residual low-risk item from the earlier Goal3425 review: the native candidate-column kernel wrote point ordinals with a cast after `uint32_t` addition:

```cpp
(unsigned long long)(params.point_index_offset + pidx)
```

For current launch chunk limits this was not practical overflow risk, but the expression shape was still less precise than the intended 64-bit ordinal contract.

## Change

`src/native/optix/rtdl_optix_workloads.cpp` now widens both terms before addition:

```cpp
(unsigned long long)params.point_index_offset + (unsigned long long)pidx
```

This changes only the optional `point_ordinal` device column. Public `point_id` output remains unchanged.

## Test Coverage

`tests/goal3424_closed_shape_instance_identity_refinement_test.py` now asserts that the widened expression appears in the native workloads source.

## Boundary

This is a correctness hardening patch only. It does not authorize release, public speedup, RayJoin reproduction, broad RT-core speedup, true zero-copy, hidden dispatch, automatic retry, or native default-route claims.
