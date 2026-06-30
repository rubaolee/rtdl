# Goal3333: RayJoin Probe-Point Owner-Face Availability Probe

Date: 2026-06-04

Status: negative/limit evidence. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3330 showed that caller-supplied owner face ids can reconcile the known county CDB overcount rows. Goal3333 checks whether those owner face ids are trivially available from the CDB probe-point chain rows themselves.

They are not.

## Pod Evidence

Artifact:

- `docs/reports/goal3333_rayjoin_probe_point_owner_face_availability_2026-06-04.json`

Pod commit:

- `83d1c8c5`

Input:

- `br_county_start256_count512.cdb`
- The 7 mismatching point ids from Goals 3327-3328
- Owner-face ids used by the Goal3330 reconciliation test

## Result

| Measure | Value |
| --- | ---: |
| Mismatching points inspected | 7 |
| Owner face equals point-chain left face | 4 |
| Owner face equals point-chain right face | 1 |
| Owner face equals neither left nor right | 2 |

Rows where the needed owner face is neither the point-chain left nor right face:

| Point ID | Point Chain Faces | Owner Face Needed |
| ---: | --- | ---: |
| 538 | `228, 253` | 217 |
| 564 | `271, 262` | 187 |

## Interpretation

A simple dataset-loader policy such as "use the left face" or "use the right face" is insufficient for this CDB slice. The owner-face contract is still the right generic boundary, but the app/data layer needs a richer topology derivation step before the fast route can be generally authorized.

That is useful negative evidence:

- It prevents overclaiming Goal3330 as a completed RayJoin fix.
- It keeps the current preflight fallback mandatory.
- It clarifies the next real work: derive or provide owner-face columns as explicit input, then lower the generic owner-face filter to device/native code.

## Boundary

The native engine must not infer RayJoin or CDB ownership semantics. It can execute a generic owner-face filter only after the caller supplies the ownership column.
