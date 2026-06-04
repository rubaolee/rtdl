# Goal3353: Owner-Face Priority Columnar Derivation

Date: 2026-06-04

Status: internal v2.8 Python reference helper. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3351 added row-shaped priority derivation from caller-supplied rank signals. Goal3353 adds a columnar same-contract front door so future native/device lowering has a typed-column target while still sharing the exact Python reference semantics.

New helper:

- `derive_owner_face_priority_columns_from_rank_signals(...)`

## Contract

Inputs:

- `point_ids`,
- `face_ids`,
- `rank_columns`,
- caller-declared `rank_fields`.

Output columns:

- `point_id`
- `face_id`
- `priority`
- `priority_rank_key`

The helper normalizes columns into the Goal3351 row helper, so row and column paths share the same behavior:

- lower rank tuple receives lower priority,
- priorities restart per point,
- mismatched column lengths fail closed,
- missing rank columns fail closed,
- duplicate point/face rows fail closed through the row contract,
- tied rank tuples fail closed by default.

## Boundary

This is not a device implementation. It is a Python reference columnar contract intended to make native/device lowering testable later. The native/device lowering remains blocked until a future implementation proves same-contract behavior and records pod/native evidence.

The engine still does not infer ownership, CDB policy, RayJoin assignment semantics, map/entity lookup, or paper-system behavior. The caller supplies the rank fields and their meaning.

## Validation

Goal3353 tests verify:

- columnar and row front doors produce the same priority rows,
- columnar priorities feed the existing owner-face selector,
- bad column lengths fail,
- missing rank columns fail,
- tied rank values fail,
- the Goal3349 contract lists both row and column derivation helpers,
- the report keeps the reference-only and claim-boundary wording visible.
