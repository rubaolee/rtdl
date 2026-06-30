# Goal4176: Declared RT-DBSCAN All-Items Direct-Status Refactor

Status: implementation accepted pending pod timing.

## Purpose

Goal4172 introduced an explicit caller-declared all-predicate RT-DBSCAN route.
Its first implementation fed synthetic all-true predicate columns into the
predicate direct-status wrapper. Goal4176 removes that unnecessary predicate
column layer.

The declared route now uses the existing generic all-items direct-status
component-signature primitive:

`prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d`

and wraps the generic component-size signature into the RT-DBSCAN app signature
shape:

`core_count = point_count`, `noise_count = 0`, and component sizes from the
generic all-items direct-status primitive.

## Design

- Native engine unchanged.
- No app-specific ABI added.
- No hidden dispatch.
- No automatic route selection.
- No RT count-threshold execution in this declared route.
- No synthetic predicate columns are materialized.
- No synthetic neighbor-count sentinel columns are materialized.
- Metadata records `uses_generic_all_items_direct_status_signature: true`.
- Metadata records `predicate_columns_materialized: false`.
- Metadata keeps the external-proof requirement for the all-predicate
  precondition.

## Why This Is A Runtime-Level Improvement

This is not a one-off app optimization. The route now uses a generic
all-items component primitive directly instead of going through a predicate
wrapper only to rediscover that every predicate is true. That is the reusable
language/runtime pattern:

when the caller has a valid all-items predicate proof, execute the generic
all-items component primitive and adapt the result at the app boundary.

## Boundary

This report does not authorize automatic route selection, automatic partner
selection, automatic factor selection, release, public speedup wording, broad
RT-core wording, whole-app benchmark claims, paper-reproduction claims,
app-specific engine logic, native ABI additions, AMD performance claims, or
true-zero-copy claims.

Pod timing is still required before replacing the Goal4173 timing numbers in
the route registry.
