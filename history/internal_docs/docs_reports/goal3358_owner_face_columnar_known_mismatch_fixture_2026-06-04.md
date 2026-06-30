# Goal3358: Owner-Face Columnar Known-Mismatch Fixture

Date: 2026-06-04

Status: internal v2.8 same-contract fixture. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3358 adds a same-contract fixture over the seven known county mismatch points diagnosed in Goals3327-3335. This moves the columnar owner-face pipeline beyond toy rows while still staying a Python reference fixture.

## Fixture

Inputs come from existing artifacts:

- `docs/reports/goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json`
- `docs/reports/goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json`

The fixture uses the known owner-face mapping from the earlier row reference:

- `522 -> 248`
- `523 -> 248`
- `538 -> 217`
- `539 -> 217`
- `540 -> 212`
- `564 -> 187`
- `565 -> 187`

## What Is Tested

The complete columnar path:

1. Incident face columns plus caller-supplied rank signals produce priority columns.
2. Incident face columns plus priority columns produce owner-face columns.
3. Candidate/topology/owner-face columns produce filtered membership columns.
4. Filtered membership columns recover exactly the known exact shape ids for all seven mismatch points.
5. Columnar output matches the existing row-reference filter output.

## Boundary

This is not a native/device implementation. It is a Python reference same-contract fixture for future lowering.

The priority rank signal in this fixture is deliberately supplied by the test from the known owner-face mapping. RTDL still does not infer CDB/RayJoin ownership policy.

Still blocked:

- automatic owner-face derivation,
- native/device lowering,
- pod evidence,
- RayJoin paper reproduction claims,
- RTDL-beats-RayJoin claims,
- public speedup claims,
- broad RT-core speedup claims,
- true zero-copy claims.

## Validation

Goal3358 tests verify exact-row recovery and row/column parity for the seven known county mismatch points.
