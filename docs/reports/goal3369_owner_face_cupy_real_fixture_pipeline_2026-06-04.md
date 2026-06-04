# Goal3369: Owner-Face CuPy Real-Fixture Pipeline

Date: 2026-06-04

Status: internal v2.8 fixture validation. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3367 proves the composed owner-face CuPy device-column pipeline on toy rows. Goal3369 applies the same helper to the seven known county mismatch points from the RayJoin/CDB topology probes:

- `docs/reports/goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json`
- `docs/reports/goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json`

This is still an internal same-contract fixture. It is not a RayJoin paper reproduction claim.

## Fixture

The fixture uses seven known county mismatch points:

- `522`, `523`, `538`, `539`, `540`, `564`, `565`

The test builds:

- incident point/face/count columns from the incident-face probe,
- caller-supplied rank columns that prioritize the known owner face,
- candidate point/shape columns from exact plus extra candidate shape ids,
- topology shape/left-face/right-face columns with face-presence gates.

The composed CuPy device-column pipeline must recover exactly the known exact shape ids for every point and must select the expected owner face by point.

## Boundary

This is a composed CuPy device-column pipeline validation over a real stored fixture. It is not native RT traversal, not native lowering, not a release artifact, and not public performance evidence.

Still blocked:

- native/device lowering of the full owner-face pipeline,
- default selection of this composed helper,
- release or public performance wording,
- RayJoin paper reproduction wording,
- RTDL-beats-RayJoin wording,
- broad RT-core speedup wording,
- true zero-copy wording.

## Pod Evidence

Collected on 2026-06-04:

- Host: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000`
- CuPy: `14.1.1`

Focused real-fixture command:

```text
PYTHONPATH=src python3 -m unittest \
  tests.goal3369_owner_face_cupy_real_fixture_pipeline_test \
  tests.goal3368_owner_face_cupy_selection_review_gap_closure_test \
  tests.goal3367_owner_face_cupy_pipeline_composition_test \
  tests.goal3358_owner_face_columnar_known_mismatch_fixture_test
```

Focused result:

```text
Ran 14 tests in 0.765s
OK
```

Full owner-face family rerun with CuPy available:

```text
Ran 96 tests in 0.782s
OK
```

## Validation

Goal3369 tests cover:

- exact-row recovery on the seven-point fixture through the composed CuPy pipeline,
- selected owner face parity for all seven points,
- report boundary wording.
