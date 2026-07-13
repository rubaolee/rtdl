# Goal5049 - RayJoin App Migration To Public v2.14.4 Surfaces

Date: 2026-07-06

Status:

```text
completed_rayjoin_sort_path_migrated_to_public_device_order_by_surface__no_performance_claim
```

## Purpose

Goal5049 migrates one RayJoin paper-reproduction app path from a direct internal
native helper call to a public v2.14.4 RTDL API surface.

This is an API-surface convergence goal.  It is not a new RayJoin performance
goal and does not change the v2.14.3 performance headline.

## Implementation

Modified:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

Added:

```text
tests/goal5049_rayjoin_public_v2144_surface_migration_test.py
```

The app route:

```text
--device-columnar --native-lexsort
```

previously called:

```text
optix_runtime.run_cuda_lexsort_i64_f64_i64_i64_device(...)
```

directly from the RayJoin app.

It now calls the public surface:

```text
DeviceColumnBuffer -> device_order_by(..., backend="native_cuda")
```

through a local adapter:

```text
_run_public_device_order_by_native_lexsort(...)
```

The adapter wraps the four sort keys as a `DeviceColumnBuffer`:

```text
edge_key:int64
dist_key:float64
tie_key:int64
order_key:int64
```

and uses:

```text
device_order_by(buffer, keys=("edge_key", "dist_key", "tie_key", "order_key"), backend="native_cuda")
```

## Scope

Migrated paths:

1. intersection sort for `sort_xsect_indices_for_map_numba_device(... native_lexsort=True)`;
2. descriptor-pair sort inside `descriptor_pair_count_projected_device(...)`.

Both are still app-owned RayJoin workflow steps, but the ordering operation is
now expressed through a generic RTDL API rather than a direct `optix_runtime`
call.

## Important Semantic Detail

The intersection-sort buffer is padded, but the original direct native helper
sorted only `valid_count` rows.  The public migration preserves that boundary by
passing sliced device views:

```text
edge_key[:valid_count]
dist_key[:valid_count]
tie_key[:valid_count]
order_key[:valid_count]
```

This avoids silently changing ordering semantics or timing scope by sorting the
padded sentinel tail.

## Verification

Command:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5049_rayjoin_public_v2144_surface_migration_test tests.goal5019_native_lexsort_bridge_test tests.goal5048_non_rayjoin_numba_partner_public_api_genericity_test tests.goal5045_public_device_order_by_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
........s.....
----------------------------------------------------------------------
Ran 14 tests in 0.194s

OK (skipped=1)
```

## What This Proves

- One RayJoin app path now uses the public v2.14.4 `device_order_by` API.
- The app no longer imports `optix_runtime` solely to call the native lexsort
  helper.
- The migrated helper records `public_device_order_by_used`.
- The helper preserves the previous `valid_count` sort boundary.
- Existing native lexsort structural tests still pass.

## What This Does Not Prove

- It does not prove a new performance improvement.
- It does not change the v2.14.3 performance headline.
- It does not make RayJoin a core RTDL primitive.
- It does not make `device_group_by` public.
- It does not prove POD runtime success for the migrated call path in this local
  environment.

## Claim Boundary

Authorized:

```text
rayjoin_app_uses_public_device_order_by_for_native_lexsort_path
public_api_surface_convergence
no_direct_optix_runtime_lexsort_call_from_rayjoin_app
```

Not authorized:

```text
new_speedup_claim
author_parity_claim
true_zero_copy_claim
device_group_by_public_ready
RayJoin_core_primitive
POD_runtime_success
```

## Next

Request external review.  If accepted, proceed to Goal5050: public/private
surface boundary audit for v2.14.4, including legacy grouped/segmented Numba
exports and remaining RayJoin-named lower-level symbols.
