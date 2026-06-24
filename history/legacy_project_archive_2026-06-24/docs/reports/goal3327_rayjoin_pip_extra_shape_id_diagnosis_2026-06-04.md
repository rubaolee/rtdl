# Goal3327: RayJoin PIP Extra Shape-ID Diagnosis

Date: 2026-06-04

Status: diagnostic evidence only. This report does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goals 3320-3322 showed that the current generic fast point/closed-shape count route is valid on the `br_soil_start256_count512.cdb` slice but overcounts the `br_county_start256_count512.cdb` slice by 12 rows across 7 points. Goal3327 narrows the failure from a scalar count mismatch to concrete extra shape ids.

The key question was:

> For each mismatching point, which shape ids are emitted by the fast device-column route but absent from the exact prepared membership rows?

## Pod Evidence

The probe was run on the pod from Git `main` at commit `f03e915e` with `build/librtdl_optix.so` on an NVIDIA RTX A5000.

Artifact:

- `docs/reports/goal3327_rayjoin_pip_extra_shape_id_diagnosis_2026-06-04.json`

Environment:

- `RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS=z_point`
- `RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE=1`
- Fast device-column route boundary mode: `inclusive`

## Result Summary

| Dataset | Exact Rows | Device-Column Rows | Delta | Mismatch Points | Missing Shape IDs |
| --- | ---: | ---: | ---: | ---: | ---: |
| `br_county_start256_count512.cdb` | 1417 | 1429 | +12 | 7 | 0 |
| `br_soil_start256_count512.cdb` | 1471 | 1471 | 0 | 0 | 0 |

The failing county slice has only positive deltas: the fast route emits extra shape ids, but it does not miss exact shape ids in this bounded probe.

## County Mismatch Pattern

| Point ID | Exact Shape IDs | Fast Device Shape IDs | Extra Shape IDs | Delta |
| ---: | --- | --- | --- | ---: |
| 522 | `522, 523` | `521, 522, 523` | `521` | +1 |
| 523 | `522, 523` | `521, 522, 523` | `521` | +1 |
| 538 | `535, 539` | `418, 535, 539, 540` | `418, 540` | +2 |
| 539 | `535, 539` | `418, 535, 539, 540` | `418, 540` | +2 |
| 540 | `418, 540` | `418, 535, 539, 540` | `535, 539` | +2 |
| 564 | `562, 565` | `437, 559, 562, 565` | `437, 559` | +2 |
| 565 | `562, 565` | `437, 559, 562, 565` | `437, 559` | +2 |

This is a structured ownership/topology failure, not a random numerical drift. The current fast route sees closed-shape membership candidates, but the RayJoin/CDB contract needs a policy that resolves face/ring/chain/boundary ownership. That policy must stay outside app-specific engine logic.

## Design Consequence

Goal3324's candidate primitive direction is now better grounded:

- The needed generic primitive is not "RayJoin count."
- The needed generic primitive is a topology-aware closed-shape membership/count contract over point ids, shape ids, boundary ids, and ownership policy.
- CDB chain/face interpretation and RayJoin benchmark acceptance policy remain app code.

The engine can expose generic topology rows and generic boundary-event streams. The app can decide whether a point on a shared or duplicate boundary belongs to one face, two faces, neither face, or a benchmark-specific ownership projection.

## Claim Boundary

The existing `preflight_rayjoin_pip_fast_count_domain(...)` fail-closed gate remains required:

- Soil slice: fast route can be used only after preflight validates exact match.
- County slice: fast route must be rejected and must fall back to exact prepared rows or a future topology-aware primitive.

This evidence is diagnostic and design-guiding. It does not make the current fast route generally correct for CDB point-in-polygon counts.
