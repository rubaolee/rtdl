# Goal4172: Declared All-Predicate RT-DBSCAN Route

Status: implementation accepted pending pod timing.

## Purpose

Goal4171 showed that the 2M road-like one-shot all-predicate wrapper remains
faster than the current grouped-stream route, but still pays first-run overhead
from measuring threshold flags before it can observe the all-predicate fast
path.

Goal4172 adds an explicit caller-declared all-predicate route:

`partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d`

This route is for users who already know or externally prove that every item
satisfies the predicate. It feeds a caller-declared all-true predicate column
into the existing generic predicate direct-status signature wrapper, avoiding
the OptiX count-threshold phase entirely.

## Design

- Native engine unchanged.
- No app-specific ABI added.
- No hidden dispatch.
- No automatic route selection.
- The route advisor exposes the mode only as an explicit external-proof option.
- No RT-count-threshold execution in this declared-predicate route.
- No RT-core acceleration claim for the declared-predicate subpath.
- Metadata records `predicate_flags_source: caller_declared_all_true`.
- Metadata records `caller_declared_predicate_columns_require_external_proof:
  true`.
- Neighbor counts are threshold-satisfying sentinel values, not exact degrees.

## Boundary

This route is not a replacement for mixed-predicate RT-DBSCAN. It is only valid
when the caller explicitly chooses the route and accepts responsibility for the
all-true predicate precondition.

This report does not authorize automatic route selection, automatic partner
selection, automatic factor selection, release, public speedup wording, broad
RT-core wording, whole-app benchmark claims, paper-reproduction claims,
app-specific engine logic, native ABI additions, AMD performance claims, or
true-zero-copy claims.
