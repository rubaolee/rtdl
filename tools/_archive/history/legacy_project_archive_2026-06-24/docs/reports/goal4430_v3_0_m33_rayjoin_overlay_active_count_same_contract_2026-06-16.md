# Goal4430 V3.0 M33 Spatial RayJoin Overlay Active-Count Same-Contract Refresh

## Decision

M33 repairs a Spatial RayJoin overlay comparison asymmetry. The old fair-run overlay row compared Embree raw relation-row count
`generic_row_count_raw_view_no_python_dicts` against OptiX
`overlay_active_pair_dependency_count`; those are different output contracts and
must not be used as an apple-to-apple backend comparison.

## What Changed

Embree now has a generic prepared 2-D shape-pair active-count primitive:

- `rtdl_embree_shape_pair_active_count_2d_create`
- `rtdl_embree_shape_pair_active_count_2d_count`
- `rtdl_embree_shape_pair_active_count_2d_destroy`

The Python runtime exposes it as `prepare_embree_shape_pair_active_count_2d`.
The native count path reuses a prepared right-shape Embree scene, accepts a
packed left-shape payload, counts active shape pairs, and avoids materializing
`RtdlShapePairRelationRow` rows in the timed count path.

The Embree primitive mirrors the existing OptiX active-count contract: edge
intersections come from the RT traversal, and containment-only pairs are covered
by a generic bounds-checked first-vertex containment continuation. This avoids
the earlier traversal-only undercount for pairs where one polygon is wholly
inside another and no edge crossing is observed.

## Measured Evidence

The formal pod evidence is:

- `docs/reports/goal4430_v3_0_m33_rayjoin_overlay_active_count_same_contract_2026-06-16.json`

The measured case is the public CDB overlay slice:

- left: `data/rayjoin_public_cdb/br_county_start256_count512.cdb`
- right: `data/rayjoin_public_cdb/br_soil_start256_count512.cdb`

The only accepted comparison contract is `overlay_active_pair_dependency_count`.
Full polygon overlay materialization, RayJoin Section 5.7 paper reproduction,
and author-code comparison remain out of scope for this M33 packet.

| Backend | Route | Contract | Active count | Warmup / repeats | Median timed count | Timed total | Setup | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| RTDL OptiX | `prepared_optix_shape_pair_active_count_device_continuation_reuse` | `overlay_active_pair_dependency_count` | 174 | 2 / 25 | 0.000196 s | 0.004915 s | 1.178244 s | device continuation; no row materialization |
| RTDL Embree | `prepared_embree_shape_pair_active_count_2d` | `overlay_active_pair_dependency_count` | 174 | 2 / 25 | 0.089171 s | 2.297924 s | 0.066252 s | prepared CPU scene; no row materialization |

For this narrow same-contract active-count slice, OptiX is 455.27x faster than
Embree by timed median. This is not a full polygon overlay result: it is only
the dependency active-count phase with rows/materialized overlay output removed
on both sides.

## Boundary

M33 is still internal V3 evidence. It authorizes no public speedup wording, no
full overlay wording, no RTDL-beats-RayJoin wording, and no RT-core speedup
claim. Its purpose is narrower and important: prevent a known bad comparison and
provide a same-contract Embree CPU-core row for overlay active count.
