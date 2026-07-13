# Call For Review - Goal5050 v2.14.4 Public/Private Boundary Audit

Date: 2026-07-06

Review target:

```text
history/internal_docs/goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md
tests/goal5050_v2144_public_private_boundary_audit_test.py
src/rtdsl/__init__.py
src/rtdsl/numba_partner_api.py
src/rtdsl/optix_runtime.py
src/native/optix/rtdl_optix_core.cpp
```

## Requested Verdict Labels

```text
approve_goal5050_boundary_audit_public_surfaces_clean_legacy_debts_documented
revise_goal5050_before_v2_14_4_closeout
fail_goal5050_hidden_rayjoin_core_or_group_by_public_overclaim
```

## Context

Goal5050 is a boundary audit, not a performance or feature goal.

It checks whether v2.14.4 can honestly say:

```text
RTDL exposes generic public device-columnar prepared-pipeline APIs, while RayJoin
is an app using those APIs.
```

It also records two debts:

1. legacy grouped/segmented Numba symbols still exist as lower-level exports,
   but `device_group_by` is not public and grouped operations are not accepted by
   `NumbaPartnerContinuation`;
2. RayJoin-named lower-level native/OptiX symbols still exist, but the public
   wrappers are generic and the native symbol rename is deferred.

## Review Questions

1. Does the report correctly identify the public v2.14.4 API surfaces:
   `DeviceColumnBuffer`, `PreparedGeometrySession`, `device_order_by`, and
   `NumbaPartnerContinuation`?
2. Does it correctly preserve the non-authorization boundaries around speedup,
   true-zero-copy, app-specific semantics, and RT traversal replacement?
3. Does it correctly classify legacy grouped/segmented Numba exports as
   lower-level compatibility debt rather than public `device_group_by`?
4. Does it correctly state that grouped operation values are excluded from
   `NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS` and fail closed through the
   new public API?
5. Does it correctly disclose RayJoin-named lower-level native symbols such as
   `rtdl_optix_prepare_rayjoin_cdb_point_location_2d` and
   `_PLANAR_MAP_LSI_LEGACY_NATIVE_ALIAS = "rayjoin_lsi"`?
6. Is deferring native symbol renaming reasonable for v2.14.4, provided the debt
   is explicitly documented?
7. Does the report avoid claiming that all internal/core symbols are RayJoin-free?
8. Is Goal5049's RayJoin app migration accurately described as partial API
   convergence, not a performance claim?

## Non-Authorization

This review must not authorize:

```text
device_group_by_public_ready
all_internal_symbols_rayjoin_free
public_speedup_claim
author_parity_claim
true_zero_copy_claim
RayJoin_core_primitive
RT_traversal_replacement_claim
POD_runtime_success_for_skipped_smokes
```
