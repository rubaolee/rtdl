# Goal4895 Completion Report: Generic Packed CDB Input Cache

Date: 2026-07-03

## Requested verdict

`approve_goal4895_packed_cdb_cache_productized`

## Purpose

After Goal4894, the representative overlay path was no longer dominated by directed point-location candidate explosion. The largest remaining measured cost was CDB text load/pack:

- Goal4894 total: `92.773s`
- Goal4894 load/pack left: `72.165s`
- Goal4894 load/pack right: `4.624s`

Goal4895 attacks that dominant cost by adding a generic packed CDB/planar-map input loader with optional disk cache.

## Code changes

Changed files:

- `src/rtdsl/datasets.py`
- `src/rtdsl/__init__.py`
- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`
- `tests/goal4895_planar_map_cdb_packed_loader_test.py`
- `tests/goal4895_public_cdb_loader_harness_integration_test.py`

New public data utility:

- `rtdsl.load_planar_map_cdb_packed_inputs(path)`
- `rtdsl.PlanarMapCdbPackedInputs`

Cache env:

- `RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR`
- Legacy fallback accepted: `RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR`

What the loader returns:

- packed generic LSI segments;
- packed directed face-segments for point-location;
- packed points;
- chain offsets and counts;
- per-chain left/right faces;
- coordinate arrays needed by app-level continuation.

This is a generic CDB/planar-map input utility. It does not assemble overlay output, run RayJoin workflow logic, or inspect app identity.

## Why this is not RayJoin-specific

The loader parses the CDB/planar-map interchange format and creates native buffers. It does not run LSI, PIP, midpoint logic, output-chain assembly, duplicate-half-edge policy, or Section 5.7 logic. Those remain outside the loader.

The paper-reproduction harness now uses this public data utility instead of a duplicated private loader. This keeps the application code in user/application space while moving reusable input packing into RTDL.

## Local tests

Command:

```powershell
$env:PYTHONPATH='src'; py -m unittest tests.goal4895_planar_map_cdb_packed_loader_test tests.goal4895_public_cdb_loader_harness_integration_test tests.goal4894_directed_point_location_fine_grained_default_test tests.goal4851_planar_map_lsi_public_front_door_test tests.goal4857_planar_map_point_location_public_front_door_test
```

Result:

```text
Ran 14 tests in 0.113s
OK
```

## POD tests

Command:

```bash
PYTHONPATH=src python -m unittest \
  tests.goal4895_planar_map_cdb_packed_loader_test \
  tests.goal4895_public_cdb_loader_harness_integration_test \
  tests.goal4894_directed_point_location_fine_grained_default_test
```

Result:

```text
Ran 5 tests in 0.039s
OK
```

## POD performance validation

POD scratch:

- `/workspace/goal4894_productize_20260703b`

Artifacts:

- Cold cache: `history/internal_docs/goal4895_cache_cold_overlay_summary_2026-07-03.json`
- Warm cache: `history/internal_docs/goal4895_cache_warm_overlay_summary_2026-07-03.json`

Dataset:

- Australia lakes x parks representative current-source pair.
- Same comparator as Goal4894.

Correctness:

- Cold cache byte-equal: true
- Warm cache byte-equal: true
- Output SHA256: `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`

Performance:

| Route | Total | Load/pack left | Load/pack right | LSI | PIP map0 | PIP map1 | Writer |
|---|---:|---:|---:|---:|---:|---:|---:|
| Goal4893 fixed8 baseline | 129.448s | ~72.3s | ~4.7s | ~6.5s | 35.617s | 2.929s | ~2.67s |
| Goal4894 fine-grained default | 92.773s | 72.165s | 4.624s | 6.180s | 1.141s | 0.031s | 2.667s |
| Goal4895 packed cache cold | 50.896s | 31.399s | 4.434s | 5.322s | 1.497s | 0.034s | 2.702s |
| Goal4895 packed cache warm | 30.591s | 4.663s | 3.446s | 5.491s | 1.119s | 0.033s | 3.775s |

Ratios:

- Goal4895 warm vs Goal4894 default: `3.03x` total speedup.
- Goal4895 warm vs Goal4893 fixed8 baseline: `4.23x` total speedup.
- Load/pack left: `72.165s -> 4.663s`, `15.48x`.
- Load/pack combined: `76.789s -> 8.109s`, `9.47x`.

## Interpretation

Goal4895 validates that the largest remaining cost after Goal4894 was not RT traversal. It was repeated text CDB parsing and native buffer packing.

The generic packed cache turns repeat runs into a much smaller warm-start path. The first cold-cache run also improves substantially because the new vectorized loader is faster than the duplicated harness loader.

## What this does not claim

This does not claim:

- full Section 5.7 all-pair reproduction;
- broad RayJoin speedup;
- broad RTDL speedup;
- speedup on first-ever data acquisition or source conversion;
- that LSI is solved;
- that output writer is solved;
- that the cache is a public release commitment.

It does show a real engineering win on the current representative paper-reproduction app: public RTDL primitives plus a generic packed CDB input cache reduce end-to-end runtime from `92.773s` to `30.591s` while preserving byte equality.

## Next blocker

After warm cache:

- LSI public rows: `5.491s`
- output writer: `3.775s`
- load/pack combined: `8.109s`
- PIP combined: `1.152s`

The next rational target is LSI traversal/refinement, not more CDB cache work and not more PIP range tuning.
