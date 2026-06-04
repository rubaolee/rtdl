# Goal3372: Owner-Face CuPy Route Fixture Probe

Date: 2026-06-04

Status: internal v2.8 app-layer route fixture probe. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3369 proved the composed CuPy owner-face pipeline inside a unit test. Goal3372 adds a runnable route-fixture probe:

- `scripts/goal3372_owner_face_cupy_route_fixture_probe.py`

The probe loads the stored topology and incident-face artifacts, derives caller-supplied owner-face priorities, runs the composed CuPy selector plus membership filter, and writes a JSON artifact.

## Pod Artifact

Artifact:

- `docs/reports/goal3372_owner_face_cupy_route_fixture_probe_2026-06-04.json`

Pod:

- Host: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000, 580.126.09`
- CuPy: `14.1.1`
- Commit: `ef36541ed81695d79c39cdc8c08ac37fc154f4e9`

Result:

- `selected_owner_faces_match_expected = true`
- `recovered_shapes_match_exact = true`
- `point_count = 7`
- `incident_row_count = 21`
- `candidate_row_count = 26`
- `topology_row_count = 11`

## Boundary

This is not native RT traversal. It is an app-layer CuPy continuation probe over stored RayJoin/CDB mismatch artifacts.

This does not authorize:

- release,
- public speedup wording,
- RayJoin paper reproduction wording,
- RTDL-beats-RayJoin wording,
- broad RT-core speedup wording,
- true zero-copy wording.

## Next Step

The next useful engineering step is to move from stored seven-point artifacts to a bounded current-route integration that derives topology/incident columns from the loaded CDB case at runtime, then measures whether the composed CuPy continuation reduces host-side mismatch handling overhead without changing the exact-count authority.
