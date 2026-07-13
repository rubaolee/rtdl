# Goal4894 Completion Report: Generic Fine-Grained Directed Point-Location Range Default

Date: 2026-07-03

## Verdict requested

`approve_goal4894_fine_grained_point_location_productized`

## Purpose

Goal4894 productizes the Goal4893 Route-A finding: directed planar-map point-location was not slow because the PIP contract was inherently expensive; it was slow because the default range construction used coarse grouped AABBs that caused a massive candidate explosion. The proven fix is to use fine-grained one-segment ranges as the default generic directed point-location index.

This is a generic directed point-location planner repair. It is not a RayJoin-only hidden kernel.

## Code changes

Changed files:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/rayjoin_overlay.py`
- `tests/goal4894_directed_point_location_fine_grained_default_test.py`

Native planner changes:

- Added `RayjoinCdbGroupMode::FineGrained`.
- Changed no-env default from `Fixed8` to `FineGrained`.
- Added explicit env aliases `fine_grained` / `per_segment`.
- Kept explicit legacy overrides: `fixed8`, `fixed_8`, `adaptive`, `block_merge64`, `author_block_merge64`.
- Changed default `block_merge64` max-merge iteration from `5` to `0` when no max-iter env is provided.
- Implemented the fine-grained branch as one native AABB/range per directed segment:
  - range begin = segment index
  - range end = segment index + 1
  - AABB = rounded exact segment bounds

Bundled helper compatibility change:

- `rayjoin_overlay._directed_segment_point_location_grouping_env()` now sets `RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER=0` instead of `5` when it auto-selects `block_merge64`.

## Why this is generic

The planner decision changes the range granularity for the public directed point-location primitive. It does not inspect RayJoin pair names, CDB file names, Section 5.7 state, output-chain state, or app identity. The same public primitive accepted a synthetic non-RayJoin square map expressed as ordinary segment dictionaries.

The old names in the native code still carry historical `rayjoin_cdb` naming debt, but the behavior being productized here is generic directed point-location range construction.

## Local tests

Command:

```powershell
$env:PYTHONPATH='src'; py -m unittest tests.goal4851_planar_map_lsi_public_front_door_test tests.goal4857_planar_map_point_location_public_front_door_test tests.goal4894_directed_point_location_fine_grained_default_test tests.goal4834_rayjoin_sos_synthetic_contract_test
```

Result:

```text
Ran 28 tests in 0.054s
OK
```

Coverage:

- Goal4894 default/planner guard.
- Section 5.2 public LSI front door.
- Section 5.3 public point-location front door.
- SoS/directed point-location correctness regression.

## POD build and tests

POD:

- Host: `157.157.221.29`
- Port: `23132`
- Scratch: `/workspace/goal4894_productize_20260703b`
- GPU: inherited from active POD environment.

Build:

```bash
make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe
```

Result: passed.

POD regression tests:

```bash
PYTHONPATH=src python -m unittest \
  tests.goal4851_planar_map_lsi_public_front_door_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4894_directed_point_location_fine_grained_default_test \
  tests.goal4834_rayjoin_sos_synthetic_contract_test
```

Result:

```text
Ran 28 tests in 0.098s
OK
```

## Non-RayJoin synthetic validation

Artifact:

- `history/internal_docs/goal4894_non_rayjoin_synthetic_point_location_summary_2026-07-03.json`

Route:

- Public `prepare_planar_map_point_location_2d_optix`.
- Four ordinary segment dictionaries forming a square.
- Four ordinary query point dictionaries.
- No `rtdsl.rayjoin_overlay` import.

Result:

- `row_count`: 4
- `located_segment_count`: 2
- `positive_face_count`: 2
- `base_segment_count`: 4
- `claim_boundary.public_generic_rtdl_primitive`: true
- `claim_boundary.bundled_rayjoin_helper_used`: false

This is a functional smoke that the public primitive is usable outside RayJoin.

## Representative Section 5.7 validation

Artifact:

- `history/internal_docs/goal4894_default_fine_grained_overlay_summary_2026-07-03.json`

Run:

- Australia lakes x parks representative current-source pair.
- No directed point-location grouping env variables set.
- Public LSI and public point-location route.
- Numba app continuation wrapper present, but Numba was not on the correctness-critical RTDL primitive path.

Result:

- `byte_equal_to_author`: true
- Output SHA256: `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`
- Total elapsed: `92.773s`
- Previous explicit Goal4893 best elapsed: `93.345s`
- Previous fixed8 elapsed: `129.448s`

Phase comparison:

| Phase | Goal4893 fixed8 | Goal4893 explicit best | Goal4894 default |
|---|---:|---:|---:|
| Total elapsed | 129.448s | 93.345s | 92.773s |
| Load/pack left | ~72.3s | 72.323s | 72.165s |
| Load/pack right | ~4.7s | 4.729s | 4.624s |
| LSI public rows | ~6.5s | 6.536s | 6.180s |
| Vertex PIP map0 in map1 | 35.617s | 1.108s | 1.141s |
| Vertex PIP map1 in map0 | 2.929s | 0.031s | 0.031s |
| Midpoint PIP map0 | large fixed8 candidate issue | 0.0006s | 0.0006s |
| Midpoint PIP map1 | large fixed8 candidate issue | 0.0005s | 0.0005s |
| Output-chain writer | ~2.67s | 2.668s | 2.667s |

Candidate evidence from Goal4893:

| Route | map0 candidates | map0 reduction | map1 candidates | map1 reduction |
|---|---:|---:|---:|---:|
| fixed8 default | 511,943,147,571 | 1.0x | 36,359,368,176 | 1.0x |
| block_merge64/max_iter=0 | 9,586,860 | 53,400.5x | 1,960,935 | 18,541.9x |

Goal4894 makes the fine-grained behavior the no-env default and reaches the same full-overlay result as the explicit Goal4893 best route.

## Build-cost audit

The fine-grained route increases the number of native AABBs/ranges to one per segment. On the representative pair, the measured prepare/build costs from Goal4893 were:

- fixed8 map0 prepare: `1.478s`
- fine-grained/block_merge64 max_iter=0 map0 prepare: `0.272s`
- fixed8 map1 prepare: `3.429s`
- fine-grained/block_merge64 max_iter=0 map1 prepare: `4.377s`

The map1 prepare cost increases by about `0.95s`, but the map1 run cost falls from `2.929s` to `0.037s`. The map0 prepare cost also improves. In the full representative overlay, the net result is a major PIP-phase improvement and a total elapsed reduction from `129.448s` to `92.773s`.

## What this does not claim

This does not claim:

- full Section 5.7 all-pair reproduction;
- broad RayJoin speedup over the author system;
- broad RTDL speedup;
- Numba acceleration of RTDL native primitives;
- that load/pack or LSI are solved;
- that historical native naming debt is gone.

The honest result is narrower and important: the directed point-location candidate explosion blocker is removed from the product default for this representative workload, while correctness remains byte-equal.

## Remaining work

After Goal4894, the dominant costs are:

- CDB load/pack: about `76.8s`
- LSI public rows: about `6.18s`
- output writer: about `2.67s`

The next performance work should not continue tuning point-location ranges. It should target either CDB load/pack reuse/prepared data or LSI traversal/refinement, depending on the next measured gate.
