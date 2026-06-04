# Goal3339: Fail-Closed Incident Owner-Face Selector

Date: 2026-06-04

Status: Python reference helper. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3337 exposes generic incident face candidate rows, but it intentionally does not choose ownership. Goal3339 adds the smallest safe selection contract:

- `select_unique_owner_faces_from_incident_candidates(...)`

The helper selects an owner face only when one incident face has a unique maximum `incident_face_count` for a `point_id`. If the maximum is tied, the default behavior is to raise. Callers may explicitly choose `drop` or `emit_ambiguous`, but no silent tie-break is allowed.

## Why This Matters

Goal3335 showed the known RayJoin/CDB mismatches have incident owner-face candidates, but all top candidates tie. That means the current evidence supports a generic fail-closed selector, not an automatic RayJoin fix.

This helper makes that boundary executable:

- Simple unambiguous topology can derive owner-face rows.
- Ambiguous topology stays blocked unless app/data policy supplies more information.
- The native engine still does not infer CDB or RayJoin ownership semantics.

## Validation

Local tests confirm:

- unique incident face maximum selects an owner face,
- tied incident evidence raises by default,
- `drop` and `emit_ambiguous` policies are explicit,
- Goal3335's seven known RayJoin rows are all ambiguous under this selector.

## Next Work

The next real design target is a richer deterministic owner-face derivation contract. That contract must document its tie-break inputs and stay generic before any native/device implementation is attempted.
