# Goal3374: Owner-Face CuPy Runtime-CDB Route Probe

Date: 2026-06-04

## Status

Goal3374 moves the Goal3372 route-fixture probe one step closer to a live route: the composed CuPy owner-face selector plus filter now receives topology rows and incident owner-face candidate rows derived at runtime from the bounded RayJoin public CDB slice `br_county_start256_count512.cdb`.

The candidate/exact mismatch set still comes from the stored Goal3328 oracle. This is intentional for this step: it isolates the CDB-derived topology/incident path without claiming that the upstream RT hit stream has been fully reconnected.

## Pod Evidence

The probe ran on the RTX A5000 pod from a clean `origin/main` checkout at commit `4cc57bc49fab9e06532e7cbd08b38fb81e1ae570`.

Command shape:

```bash
cd /root/rtdl
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. python3 -m py_compile scripts/goal3374_owner_face_cupy_runtime_cdb_route_probe.py
PYTHONPATH=src:. timeout 300 python3 scripts/goal3374_owner_face_cupy_runtime_cdb_route_probe.py \
  --download \
  --output docs/reports/goal3374_owner_face_cupy_runtime_cdb_route_probe_2026-06-04.json
```

Artifact:

`docs/reports/goal3374_owner_face_cupy_runtime_cdb_route_probe_2026-06-04.json`

Recorded environment:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- CuPy: `14.1.1`
- CDB input: `/root/rtdl/data/rayjoin_public_cdb/br_county_start256_count512.cdb`

## Result

The probe derives these inputs from the CDB at runtime:

- `topology_rows_derived_from_cdb: true`
- `incident_rows_derived_from_cdb: true`
- `stored_topology_artifact_used_as_input: false`
- `stored_incident_artifact_used_as_input: false`

It then applies `run_closed_shape_owner_face_priority_membership_pipeline_cupy(...)` to the same seven known route mismatch points from the prior fixture.

Key counts:

- CDB chains: `512`
- CDB topology rows: `512`
- pipeline topology rows: `11`
- incident rows: `21`
- candidate rows: `26`
- points: `7`

Correctness checks:

- `owner_face_present_for_all_points: true`
- `selected_owner_faces_match_expected: true`
- `recovered_shapes_match_exact: true`

Recovered shape IDs:

| point_id | recovered exact shape IDs |
| ---: | --- |
| 522 | 522, 523 |
| 523 | 522, 523 |
| 538 | 535, 539 |
| 539 | 535, 539 |
| 540 | 418, 540 |
| 564 | 562, 565 |
| 565 | 562, 565 |

## Boundary

This is a Runtime-CDB route probe only. It is not native RT traversal. It does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, RTDL-beats-RayJoin, or native default route claims.

All claim-boundary flags in the JSON are `false`.

What it proves:

- the app layer can derive generic topology columns from the current bounded CDB route;
- the app layer can derive generic incident face candidate columns from the current bounded CDB route;
- the composed CuPy owner-face selector/filter still recovers the exact seven-point mismatch fixture after replacing stored topology/incident artifacts with runtime CDB derivation.

What remains blocked:

- live upstream RT hit-stream reconnection for the candidate rows;
- broad route-scale correctness beyond the seven known mismatch points;
- native lowering of the owner-face continuation;
- default route selection;
- any public release/performance/RayJoin reproduction wording.
