# Goal3328: RayJoin CDB Topology Shape-ID Probe

Date: 2026-06-04

Status: diagnostic evidence only. This report does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3327 showed that the failing `br_county_start256_count512.cdb` point-in-closed-shape slice is not missing exact rows. Instead, the fast generic device-column route emits extra shape ids for 7 points. Goal3328 asks whether those extra shape ids have CDB topology relationships with the exact shape ids.

The answer is yes: every mismatching point has at least one shared face id between the exact shape-id set and the extra shape-id set.

## Pod Evidence

The probe ran on the same RTX A5000 pod code used for Goal3327. The pod working tree remained at commit `f03e915e` because the newly committed Goal3327 JSON already existed there as an untracked generated artifact; no runtime source changed after `f03e915e`, so this is a valid diagnostic continuation over the same native/runtime code.

Artifact:

- `docs/reports/goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json`

Input:

- Dataset: `data/rayjoin_public_cdb/br_county_start256_count512.cdb`
- Mismatching point/shape ids: read from Goal3327
- Topology source: `rtdsl.datasets.chains_to_topology_rows(...)`

## Key Observation

| Point ID | Exact Shape IDs | Extra Shape IDs | Shared Face IDs |
| ---: | --- | --- | --- |
| 522 | `522, 523` | `521` | `247` |
| 523 | `522, 523` | `521` | `247` |
| 538 | `535, 539` | `418, 540` | `228, 253` |
| 539 | `535, 539` | `418, 540` | `228, 253` |
| 540 | `418, 540` | `535, 539` | `228, 253` |
| 564 | `562, 565` | `437, 559` | `262, 271` |
| 565 | `562, 565` | `437, 559` | `262, 271` |

These are not isolated floating-point misses. They are structured topology/ownership cases where multiple chains around a face boundary are plausible candidates unless the contract states how to project topology onto one accepted membership relation.

## Design Consequence

This further supports the Goal3324 candidate primitive:

- Generic engine layer: can produce point/closed-shape boundary events, candidate shape ids, chain/face topology rows, and grouped reductions.
- Generic future primitive: can define a topology-aware closed-shape membership/count contract with explicit ownership policy.
- App layer: decides CDB/RayJoin acceptance semantics and validates whether a fast route is authorized for a dataset.

In other words, the required fix is not an app-specific RayJoin patch inside OptiX. The required fix is a generic topology-aware ownership contract that apps can use.

## Current Boundary

Until that contract exists and is validated, `preflight_rayjoin_pip_fast_count_domain(...)` must remain the gate:

- Matching domains may use the fast route only after exact preflight.
- Non-matching domains must fall back to exact prepared rows.

The county slice remains a fail-closed case.
