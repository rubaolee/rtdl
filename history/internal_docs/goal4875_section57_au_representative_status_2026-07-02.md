# Goal4875 Status: Section 5.7 Australia Representative Public-Primitive Route

Date: 2026-07-02

## 2026-07-02 Final Update

The Australia representative route now passes byte-for-byte against the fair
comparison baseline:

- baseline: `Author+RTDLContractPatch`, not the unstable unpatched
  AuthorPatch output;
- RTDL route: public `prepare_planar_map_lsi_2d_optix` + public
  `prepare_planar_map_point_location_2d_optix` + Python application-layer
  output-chain assembly;
- no `rtdsl.rayjoin_overlay` import in the public route script;
- no Embree claim;
- dataset: current-OSM Australia Lakes x Parks representative, not exact
  Section 5.7 paper input.

Final full representative result:

- Author+RTDLContractPatch output:
  `/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt`
- public RTDL route output:
  `/workspace/goal4875_section57_au_representative/public_route_author_contract_rounding/rtdl_public_overlay.txt`
- both SHA256:
  `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`
- both line count: `276320`
- both byte count: `6189260`

The decisive small-case diagnosis was:

- unpatched AuthorPatch selected duplicate half-edge `178`, face `49059`;
- RTDL selected canonical duplicate half-edge `3`, face `0`;
- the candidate scan proved these two half-edges are exact reverse duplicates
  with identical `xsect_y` and slope;
- `Author+RTDLContractPatch` on the same small case matched RTDL byte-for-byte:
  SHA256 `db860a9240e8e644bdc61059653e94fcaa6ad295a8975dfbbe3b7ebac314c81f`.

The final remaining full-run mismatch was not geometric. It was an obsolete
formatting nudge that forced positive half-boundary display coordinates one
printed bucket lower. Removing that nudge made the public RTDL output
byte-identical to `Author+RTDLContractPatch`.

Focused local regression:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4373_rayjoin_cdb_point_location_route_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4866_rayjoin_section57_output_contract_test

Ran 30 tests in 0.073s
OK
```

This is a bounded representative reproduction success, not a full eight-pair
Section 5.7 claim and not a broad performance claim.

## Scope

This is a representative Section 5.7 polygon-overlay workload on the current-OSM
Australia Lakes x Parks pair. It is not an exact eight-pair paper-input claim.

The target implementation is a user/application route:

- public RTDL `prepare_planar_map_lsi_2d_optix`
- public RTDL `prepare_planar_map_point_location_2d_optix`
- Python application-level output-chain assembly
- no import of `rtdsl.rayjoin_overlay` in the final public-route script
- no Embree claim

## Artifacts On POD

- AuthorPatch baseline output:
  `/workspace/goal4875_section57_au_representative/author_patch_au_overlay.txt`
- Public RTDL route after FMA scale compatibility:
  `/workspace/goal4875_section57_au_representative/public_route_fma/rtdl_public_overlay.txt`
- Bundled-helper sanity output:
  `/workspace/goal4875_section57_au_representative/rtdl_bundled_full/rtdl_overlay.txt`
- Public-route script:
  `/workspace/goal4875_public_primitives_au_overlay.py`

## What Passed

The public RTDL route now reaches byte-for-byte equivalence with the existing
bundled helper:

- public route SHA256:
  `68e46f46b87e5bc29a45544efccfe657121859e216b4f430bae98ab48b30e912`
- bundled helper SHA256:
  `68e46f46b87e5bc29a45544efccfe657121859e216b4f430bae98ab48b30e912`

This proves the public route is not blocked by missing public LSI/PIP front
doors. It can express the current RTDL overlay path using public primitives and
application code, without importing the bundled RayJoin helper.

## Public RTDL Route Metrics

For the public route after FMA scale compatibility:

- LSI rows: `13452`
- vertex PIP positives:
  - map0 in map1: `193846`
  - map1 in map0: `30538`
- midpoint positives:
  - map0: `920`
  - map1: `1824`
- output:
  - chains: `19820`
  - faces: `8229`
  - lines: `276320`
  - bytes: `6189260`

Phase timings:

- load/pack left CDB: about `71s`
- load/pack right CDB: about `5s`
- public LSI rows: about `6s`
- vertex PIP map0 in map1: about `10.8s`
- vertex PIP map1 in map0: about `1.6s`
- midpoint PIP total: about `0.12s`
- output-chain write: about `17s`

The dominant public-route cost is currently CDB read/pack and Python output
assembly, not the RT-core LSI/PIP kernels.

## What Failed

The public RTDL route is not byte-equal to the saved AuthorPatch output:

- AuthorPatch saved SHA256:
  `832aa80954080ebe07fffa68a31715072441628a3b449ecdaf381acdb013de75`
- public RTDL SHA256:
  `68e46f46b87e5bc29a45544efccfe657121859e216b4f430bae98ab48b30e912`
- AuthorPatch saved lines: `276318`
- public RTDL lines: `276320`

The first stable difference is an output-chain split:

- AuthorPatch line 244:
  `8 37 232 268 8 0`
- RTDL line 244:
  `8 1 232 232 8 0`

RTDL then emits:

- `9 8 232 239 8 0`
- `10 29 239 267 9 0`

The geometry around that region is the same, but RTDL changes the other-map
face earlier than AuthorPatch. This localizes the first mismatch to the
midpoint/output-chain contract between adjacent LSI intersections, not to the
overall LSI row count or ordinary vertex PIP counts.

## AuthorPatch Baseline Instability On This Representative Pair

A repeated AuthorPatch run on the same current-OSM Australia representative
input produced different whole-file outputs:

- original saved AuthorPatch:
  - lines `276318`
  - bytes `6189236`
  - SHA256 `832aa80954080ebe07fffa68a31715072441628a3b449ecdaf381acdb013de75`
- repeat run 1:
  - lines `276384`
  - bytes `6190718`
  - SHA256 `da7e8de23b439116c8878a78735a4ac13e9e09d511c97467d66b631f00545733`
  - chains `19793`, faces `8217`
- repeat run 2:
  - lines `276392`
  - bytes `6190917`
  - SHA256 `30454b8b05317e31bc428330c183d4998618820ac57ea82eac04e0464d11afd0`
  - chains `19799`, faces `8213`
- repeat run 3:
  - lines `276398`
  - bytes `6191051`
  - SHA256 `bce43296c6dda3113805a3c195a687e1638bf32beac3a2a1d0bf51338abf204e`
  - chains `19798`, faces `8215`

The early chain-8 window remains stable across these author repeats, but the
whole output is not stable. Therefore this representative pair cannot honestly
use single-run AuthorPatch byte equality as a final correctness gate unless the
AuthorPatch baseline is further determinized.

## Non-Evidence Attempt Reverted

I tested a hypothesis that RTDL should form midpoint PIP inputs by taking the
exact rational midpoint before conversion to internal coordinates. That changed
the public route to:

- lines `276323`
- chains `19821`
- midpoint map0 positives `921`

The first diff did not move. This was a non-evidence patch and was reverted in
both the public-route script and `src/rtdsl/rayjoin_overlay.py`.

## Current Diagnosis

The useful state is:

1. Public RTDL primitives are sufficient to reproduce the current bundled-helper
   path for this representative workload.
2. Remaining mismatch against AuthorPatch is localized to midpoint/output-chain
   face assignment for adjacent intersections.
3. The AuthorPatch representative baseline is not byte-stable across repeated
   runs, so the comparison target itself needs either a deterministic tie rule
   or a bounded/non-byte-equal interpretation.
4. Numba is not currently on the correctness-critical path for this route.
   The current correctness path is RTDL OptiX LSI/PIP plus Python application
   output assembly. Numba remains a candidate for later acceleration of
   application-side compaction/assembly after correctness is closed.

## Next Controlled Step

Do not run another broad full overlay first.

Build a focused diagnostic around the first split:

- identify the exact map0 edge and partner edge ids that produce output points
  232, 239, and 268;
- dump the sorted intersections, midpoint query coordinates, and midpoint face
  ids for that edge;
- construct a small CDB-like synthetic case from that edge and the relevant
  partner edges;
- compare AuthorPatch, RTDL public primitives, and the small synthetic route on
  that case;
- only then decide whether the fix belongs in a generic RTDL point-location
  contract, a generic deterministic duplicate-half-edge rule, or application
  output assembly.
