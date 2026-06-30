# Goal3376: Owner-Face CuPy Live OptiX Candidate Route Probe

Date: 2026-06-04

## Status

Goal3376 replaces the stored candidate-row input from Goal3374 with RTDL/OptiX live candidate device columns.

The route now does this:

1. Materialize or reuse the bounded public RayJoin county slice `br_county_start256_count512.cdb`.
2. Use RTDL/OptiX `PreparedOptixPointClosedShapeMembership2D.candidate_device_columns(...)` to produce generic device-resident `(point_id, shape_id)` candidate columns.
3. Mask the seven known route-fixture points in CuPy.
4. Derive topology rows and incident owner-face candidate rows from the CDB at runtime.
5. Run the composed CuPy owner-face selector/filter over the live candidate rows.
6. Compare the recovered shapes to the stored exact-answer oracle from Goal3328.

The stored artifact is now only an expected-answer oracle. The candidate rows, topology rows, and incident rows are not read from stored artifacts.

## Pod Evidence

The probe ran on the RTX A5000 pod from a clean `origin/main` checkout at commit `ddc6962c4c23d4bd9091f487d35f029b7b042ef7`.

Command shape:

```bash
cd /root/rtdl
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. python3 -m py_compile scripts/goal3376_owner_face_cupy_optix_candidate_route_probe.py
RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
PYTHONPATH=src:. timeout 300 python3 scripts/goal3376_owner_face_cupy_optix_candidate_route_probe.py \
  --download \
  --output docs/reports/goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.json
```

Artifact:

`docs/reports/goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.json`

Recorded environment:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- CuPy: `14.1.1`
- OptiX library: `/root/rtdl/build/librtdl_optix.so`
- CDB input: `/root/rtdl/data/rayjoin_public_cdb/br_county_start256_count512.cdb`

## Result

Live candidate stream:

- `candidate_rows_from_optix_device_columns: true`
- `stored_candidate_artifact_used_as_input: false`
- `optix_candidate_device_resident: true`
- `optix_candidate_overflow: false`
- OptiX candidate rows over the 512-chain county slice: `1429`
- Selected seven-point candidate rows: `26`
- OptiX traversal seconds for the candidate stream: `0.000346161`

Runtime CDB metadata:

- `topology_rows_derived_from_cdb: true`
- `incident_rows_derived_from_cdb: true`
- `stored_topology_artifact_used_as_input: false`
- `stored_incident_artifact_used_as_input: false`
- CDB topology rows: `512`
- pipeline topology rows: `11`
- incident rows: `21`

Correctness:

- `owner_face_present_for_all_points: true`
- `selected_owner_faces_match_expected: true`
- `recovered_shapes_match_exact: true`

The live candidate stream includes the known boundary extras:

| point_id | live candidate shape IDs |
| ---: | --- |
| 522 | 521, 522, 523 |
| 523 | 521, 522, 523 |
| 538 | 418, 535, 539, 540 |
| 539 | 418, 535, 539, 540 |
| 540 | 418, 535, 539, 540 |
| 564 | 437, 559, 562, 565 |
| 565 | 437, 559, 562, 565 |

After the owner-face CuPy continuation, the recovered exact shape IDs are:

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

This is a live-candidate route probe only. It is not a default route, not release evidence, not whole-RayJoin evidence, and not a public performance claim.

All claim-boundary flags in the JSON are `false`.

What it proves:

- RTDL/OptiX can produce the generic point/shape candidate stream for the bounded CDB route;
- CuPy can consume the live candidate device columns through the existing adapter;
- CDB-derived topology/incident metadata plus the owner-face continuation removes the known boundary extras for the seven mismatch points;
- no app-specific native engine logic was added.

What remains blocked:

- route-scale correctness beyond the seven known mismatch points;
- removing the seven-point mask and deriving owner-face priority policy for all points;
- default route selection;
- native lowering of the owner-face continuation;
- release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, and true-zero-copy claims.
