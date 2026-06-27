# Goal3723 RayJoin LSI Direct-Intersection Route Probe

Date: 2026-06-07

## Purpose

Goal3719 proved that Python/ctypes overhead is not the material cause of RTDL's remaining same-source RayJoin LSI gap. Goal3723 tests the next natural hypothesis: RayJoin's LSI kernel does useful work directly inside the custom OptiX intersection program, while RTDL's current generic exact-count route uses an intersection program plus an any-hit program.

Goal3722 therefore added a diagnostic-only generic segment-pair prepared-left route that counts exact intersections inside the custom intersection program and does not install an any-hit program. The goal is not to make a default route. The goal is to learn whether removing the any-hit callback materially closes the RayJoin gap.

## Pod Evidence

Artifact:

`docs/reports/goal3722_rayjoin_lsi_direct_intersection_route_a5000/summary.json`

Environment:

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX A5000, driver 580.126.09 |
| RTDL commit | `986ce324` |
| RayJoin commit | `02bf6220d6d20b04af77ee20364eced75cc029c9` |
| Dataset | RayJoin bundled Brazil county/soil text files |
| Left segments | 326,193 |
| Right segments | 251,011 |
| RayJoin repeat/warmup | 3 / 2 |
| RTDL repeat/warmup | 12 / 4 |

## Results

| Route | Seconds | Relative |
| --- | ---: | ---: |
| RayJoin LSI query | 0.000880003 | 1.000x RayJoin |
| RTDL existing any-hit exact count | 0.001098436 | 0.801x vs RayJoin |
| RTDL direct intersection exact count | 0.001148371 | 0.766x vs RayJoin |
| Direct-intersection vs existing any-hit | 0.001148371 vs 0.001098436 | 0.957x |

Correctness:

| Source | Count |
| --- | ---: |
| RayJoin LSI | 20,860 |
| RTDL existing any-hit route | 20,860 |
| RTDL direct-intersection route | 20,860 |

The new route is correct on this dataset, but it is slower than the existing RTDL any-hit exact-count route.

## Diagnosis

This closes the simple "remove any-hit" hypothesis. RayJoin's advantage is not explained by RTDL paying an any-hit callback alone. In this probe:

| Phase | Existing any-hit | Direct intersection |
| --- | ---: | ---: |
| `candidate_count_pass` | 0.000954849 s | 0.001012131 s |
| `emitted_count` | 20,860 | 20,860 |
| `raw_candidate_count` | 20,972 | 0, not recorded |
| `mode` | `count_prepared_left` | `count_prepared_left_direct_intersection` |

The direct route has fewer conceptual callbacks, but it performs the double exact predicate inside the intersection program for every candidate. RayJoin's LSI implementation is more specialized: it uses map-specific edge ranges (`eid_range`), internal integer edge/point structures, and an app-specific queue-oriented custom intersection program. RTDL's route remains generic and same-contract exact, with float BVH rays plus double exact segment columns.

The next useful target is therefore not another callback-placement toggle. It is a deeper, app-agnostic segment-pair primitive improvement:

- Reduce generic segment-pair launch/parameter overhead without losing app-agnostic structure.
- Investigate a first-class grouped primitive representation similar in spirit to RayJoin's `eid_range`, but expressed generically as primitive groups/ranges rather than map/domain objects.
- Compare double exact predicate cost against RayJoin's integer/internal-coordinate predicate and decide whether RTDL needs a generic fixed-point or integer-coordinate exact predicate option.
- Keep the existing any-hit exact route as the faster current RTDL path for this dataset.

## Claim Boundary

This goal is diagnostic-only. It does not authorize:

- RTDL-beats-RayJoin claims.
- RayJoin paper reproduction claims.
- Public RT-core speedup claims.
- Release/default-route claims.
- True zero-copy claims.

## Decision

Do not promote the direct-intersection route as the recommended LSI route. Keep it as a diagnostic implementation and move the next RayJoin perf work toward generic grouped/ranged primitive representation and exact-predicate representation.
