# Goal3330: Owner-Face Closed-Shape Membership Reference Contract

Date: 2026-06-04

Status: Python reference contract. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goals 3327-3328 turned the RayJoin PIP count problem into a precise generic shape:

1. The fast device-column route emits extra `shape_id` candidates for the county CDB slice.
2. Those extras are topology-adjacent: every mismatching point has shared face ids between exact and extra shape groups.
3. Therefore the missing abstraction is explicit topology ownership, not an app-specific RayJoin branch in the native engine.

Goal3330 adds a Python reference contract for that abstraction:

- `filter_closed_shape_membership_candidates_by_owner_face(...)`
- `count_closed_shape_membership_candidates_by_owner_face(...)`
- `owner_face_membership_contract()`

## Contract

Inputs:

- Generic candidate rows with `point_id`/`shape_id` or `left_id`/`right_id`.
- Generic topology rows with `shape_id` or `chain_id`, plus `left_face_id` and `right_face_id`.
- Caller-supplied `owner_face_ids_by_point`.

Outputs:

- `point_id`
- `shape_id`
- `membership=1`
- `owner_face_id`

The important point is who supplies ownership. RTDL does not infer CDB, GIS, RayJoin, or benchmark semantics. The caller supplies owner face ids; the generic contract only filters candidate shape ids through those explicit ownership faces.

## Goal3327/3328 Reconciliation Check

Using the mismatching county slice evidence:

| Point ID | Owner Face | Fast Device Shape IDs | Owner-Face Filtered Shape IDs | Exact Shape IDs |
| ---: | ---: | --- | --- | --- |
| 522 | 248 | `521, 522, 523` | `522, 523` | `522, 523` |
| 523 | 248 | `521, 522, 523` | `522, 523` | `522, 523` |
| 538 | 217 | `418, 535, 539, 540` | `535, 539` | `535, 539` |
| 539 | 217 | `418, 535, 539, 540` | `535, 539` | `535, 539` |
| 540 | 212 | `418, 535, 539, 540` | `418, 540` | `418, 540` |
| 564 | 187 | `437, 559, 562, 565` | `562, 565` | `562, 565` |
| 565 | 187 | `437, 559, 562, 565` | `562, 565` | `562, 565` |

This does not prove that RTDL can infer those owner faces automatically. It proves a useful contract boundary: if the app or dataset loader supplies the ownership column, the generic engine/partner continuation has a clear, app-agnostic filter to implement.

## Design Boundary

This is the recommended next native/device target, not a completed native primitive. A future implementation may lower the same contract into device-resident columns and grouped reductions, but it must keep the same ownership split:

- Engine: candidate ids, topology rows, owner-face filter mechanics.
- App/data loader: ownership policy and owner-face ids.

No RayJoin-specific terms are required by the contract.
