# Goal4846 Results - RayJoin Section 5.2 LSI

Date: 2026-07-01

## Scope

This file records the Goal4846 Section 5.2 LSI status after dataset inventory and the Block x Water run.

Baseline:

- AuthorPatch RayJoin `query_exec -query=lsi -mode=rt`.
- RTDL v2.14-line OptiX LSI predicate route.

Out of scope:

- PIP.
- Section 5.7 overlay.
- Embree.
- V3/V4.
- regenerated-data claims as exact paper-input claims.

## Dataset Status

| Pair | Current POD input status | Goal4846 status |
|---|---|---|
| County x Zipcode | available as current same-source CDB path | correctness passed in Goal4845 |
| Block x Water | available as current same-source/regenerated CDB path | correctness passed in Goal4846 |
| LKAF x PKAF | not found on current POD | missing exact input |
| LKAS x PKAS | not found on current POD | missing exact input |
| LKAU x PKAU | not found on current POD | missing exact input |
| LKEU x PKEU | not found on current POD | missing exact input |
| LKNA x PKNA | not found on current POD | missing exact input |
| LKSA x PKSA | not found on current POD | missing exact input |

## County x Zipcode

From Goal4845:

| Route | LSI count |
|---|---:|
| AuthorPatch | 961165 |
| RTDL OptiX | 961165 |
| Delta | 0 |

Goal4845 exposed and repaired a generic RTDL candidate-generation defect for exact/scaled nonzero segments that collapse to a single float32 candidate ray.

## Block x Water

### AuthorPatch Run

Correct command shape:

```text
cd /workspace/rtdl_goal4806_fast_min
/workspace/RayJoin_goal4840_author_probe/release_probe/bin/query_exec \
  -poly1 artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb \
  -poly2 artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb \
  -serialize=/dev/shm \
  -grid_size=15000 \
  -mode=rt \
  -query=lsi \
  -warmup=0 \
  -repeat=1 \
  -logtostderr=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false
```

Result:

```text
Intersections: 649605
```

Timer excerpt:

| AuthorPatch phase | Time |
|---|---:|
| Read map 0 | 14307.5 ms |
| Read map 1 | 11001.2 ms |
| Load Data | 555.144 ms |
| Adaptive Grouping | 23.174 ms |
| Build Index | 21.3439 ms |
| Query | 22.6271 ms |
| Cleanup | 585.289 ms |

### RTDL Run

Command:

```text
cd /workspace/rtdl_goal4817_user_smoke_20260630_102224
PYTHONPATH=src \
RTDL_OPTIX_LIB=/workspace/rtdl_goal4817_user_smoke_20260630_102224/build/librtdl_optix.so \
python3 scripts/rayjoin_paper_reproduction_suite.py run-rtdl \
  --dataset-root /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset \
  --case-id lsi_block_water \
  --backend optix \
  --warmup 0 \
  --repeat 1 \
  --input-provenance same_source_regenerated_cdb \
  --output-json /workspace/goal4846_lsi_block_water_rtdl_optix.json
```

Result:

```text
RTDL OptiX LSI count: 649605
Delta vs AuthorPatch: 0
```

RTDL timing fields from the artifact:

| RTDL field | Value |
|---|---:|
| elapsed_sec | 20.367579385638237 |
| native_traversal_median_sec | 0.008402552 |
| candidate_count_pass | 0.008402552 |
| emitted_count | 649605 |

Interpretation:

- Correctness passes: AuthorPatch and RTDL both report `649605`.
- Timing is bounded and not final. AuthorPatch's `Query` timer is about `22.6 ms`; RTDL's native candidate count pass is about `8.4 ms`, but the Python wrapper elapsed time is about `20.37 s`. Do not report a broad performance win from this row until the timing denominator is tightened.

## Important Debugging Lesson

The first Block x Water AuthorPatch attempts were slow because the command used absolute `/workspace/...` CDB paths while the existing `/dev/shm` serialized cache was keyed by relative `artifacts/...` paths. That missed the cache and forced the author loader down a slow `read_pgraph/load_from` path.

Using the relative path from `/workspace/rtdl_goal4806_fast_min` hit the existing cache and completed in about 22 seconds.

This is an execution-harness issue, not an LSI algorithm issue.

## Current Completion Status

| Category | Count |
|---|---:|
| Available pairs with correctness pass | 2 |
| Missing exact-input pairs | 6 |
| Count mismatches currently open | 0 |

Goal4846 has completed the currently available two-pair Section 5.2 LSI correctness path on this POD. Full 8/8 exact-paper-input completion remains blocked by missing lakes/parks CDB inputs.
