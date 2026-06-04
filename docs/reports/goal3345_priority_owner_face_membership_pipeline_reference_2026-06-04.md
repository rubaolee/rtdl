# Goal3345: Priority Owner-Face Membership Pipeline Reference

Date: 2026-06-04

Status: Python reference pipeline. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3342 selected owner faces from incident candidates when caller priorities are explicit. Goal3345 wires that selector into the owner-face membership filter:

1. Incident face candidate rows.
2. Caller/data priority rows.
3. Owner-face selection rows.
4. Point-to-owner-face mapping.
5. Generic point/closed-shape candidate filtering by selected owner face.

New helper:

- `owner_face_ids_by_point_from_selection_rows(...)`

## RayJoin Diagnostic Reconciliation

Using Goal3335 incident rows and Goal3328 exact/extra shape-id rows, explicit priority rows can select the owner faces used by the Goal3330 reconciliation. The resulting owner-face mapping filters the fast device candidate shape ids back to the known exact shape ids for all seven mismatching points.

This is still not automatic RayJoin support. It proves a composable generic pipeline once the caller/data layer supplies the priority policy.

## Boundary

The native engine remains app-agnostic:

- It may execute candidate filtering and priority selection contracts.
- It must not invent the priority rows.
- Broad RayJoin/PIP fast-count correctness remains blocked outside validated domains.
