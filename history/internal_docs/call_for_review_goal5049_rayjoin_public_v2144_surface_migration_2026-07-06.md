# Call For Review - Goal5049 RayJoin Public v2.14.4 Surface Migration

Date: 2026-07-06

Review target:

```text
history/internal_docs/goal5049_rayjoin_public_v2144_surface_migration_2026-07-06.md
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
tests/goal5049_rayjoin_public_v2144_surface_migration_test.py
```

## Requested Verdict Labels

```text
approve_goal5049_rayjoin_sort_path_uses_public_device_order_by_no_performance_claim
revise_goal5049_before_goal5050
fail_goal5049_direct_internal_helper_or_performance_overclaim
```

## Context

Goal5049 migrates one RayJoin paper-reproduction app path onto the public
v2.14.4 API surface.

The migrated path is the optional native lexsort path used by the writer-free
Section 5.7 binary route.  The app previously called
`optix_runtime.run_cuda_lexsort_i64_f64_i64_i64_device(...)` directly.  It now
wraps the sort keys in a `DeviceColumnBuffer` and calls public
`device_order_by(..., backend="native_cuda")`.

This is API convergence, not a performance goal.

## Review Questions

1. Does the RayJoin app now use public `device_order_by` for the native lexsort
   path instead of directly importing/calling `optix_runtime` lexsort?
2. Does the migration preserve the previous `valid_count` sort boundary by
   slicing padded device arrays before wrapping them in a `DeviceColumnBuffer`?
3. Does the descriptor-pair device consumer also use the same public ordering
   adapter?
4. Do the tests verify both source-level migration and helper-level binding
   behavior?
5. Does the change avoid RayJoin core promotion, output-chain semantics, or
   author-format behavior in RTDL core?
6. Does the report avoid new speedup, author-parity, true-zero-copy, and POD
   runtime success claims?
7. Is it correct that Goal5050 should audit remaining public/private boundary
   issues, including legacy grouped/segmented Numba exports and RayJoin-named
   lower-level symbols?

## Non-Authorization

This review must not authorize:

```text
new_speedup_claim
author_parity_claim
true_zero_copy_claim
device_group_by_public_ready
RayJoin_core_primitive
POD_runtime_success
```
