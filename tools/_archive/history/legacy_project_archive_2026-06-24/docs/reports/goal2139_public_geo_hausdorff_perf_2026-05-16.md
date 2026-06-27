# Goal2139: Public Geo Dataset Hausdorff Performance

Date: 2026-05-16

Harness commit: `5370a8eeaf3cd8017b8573216e541961a5737468`

Pod: `root@69.30.85.189 -p 22108`, NVIDIA RTX A5000, driver 570.211.01

## Question

After Goal2134 and Goal2136 covered the X-HD graphics model names, this goal adds a public geo lane for X-HD-style dataset diversity. The original X-HD geo scripts refer to WKT files such as county, zip-code, lakes, and parks data. Those exact local WKT files are not part of this repository, so this run uses public shapefile sources as reproducible analogues:

- U.S. Census TIGER/Line 2023 county boundaries as a public analogue for `dtl_cnty.wkt`.
- U.S. Census TIGER/Line 2023 ZCTA boundaries as a public analogue for `uszipcode.wkt`.
- Natural Earth 1:10m lakes as a public analogue for `lakes.wkt`.
- Natural Earth 1:10m parks and protected lands as a public analogue for `parks.wkt`.

The benchmark converts shapefile vertices to normalized lon/lat point sets and computes exact 2D projected-point Hausdorff with the same grouped CuPy baseline and RTDL/OptiX seeded-pruned path used in the graphics runs.

## Loader Change

Goal2138 added a `public-geo` case suite to `scripts/goal2126_public_hausdorff_dataset_perf.py`.

The important implementation detail is streaming reservoir sampling for shapefiles. Census ZCTA contains more than 51 million boundary vertices in this run, so the loader samples deterministically without materializing the full coordinate corpus in Python memory.

## Results

All rows matched grouped CuPy distance within the harness tolerance.

| Sampled source points | Group | Case | Source vertices | Grouped CuPy s | RTDL/OptiX s | RTDL / CuPy | Speedup |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| 131,072 | 1024 | Census counties vs ZCTA | 8.20M / 51.22M | 1.018265 | 0.143887 | 0.141x | 7.08x |
| 131,072 | 2048 | Census counties vs ZCTA | 8.20M / 51.22M | 1.014486 | 0.148325 | 0.146x | 6.84x |
| 262,144 | 1024 | Census counties vs ZCTA | 8.20M / 51.22M | 3.760128 | 0.301055 | 0.080x | 12.49x |
| 262,144 | 2048 | Census counties vs ZCTA | 8.20M / 51.22M | 3.904420 | 0.336905 | 0.086x | 11.59x |
| 131,072 | 1024 | Natural Earth lakes vs parks | 162,852 / 7,041 | 0.085671 | 0.071190 | 0.831x | 1.20x |
| 131,072 | 2048 | Natural Earth lakes vs parks | 162,852 / 7,041 | 0.092063 | 0.071407 | 0.776x | 1.29x |
| 162,852 | 1024 | Natural Earth lakes vs parks | 162,852 / 7,041 | 0.092073 | 0.065535 | 0.712x | 1.40x |
| 162,852 | 2048 | Natural Earth lakes vs parks | 162,852 / 7,041 | 0.113681 | 0.076850 | 0.676x | 1.48x |

## Interpretation

The geo lane gives a useful density contrast:

- The detailed Census county/ZCTA row behaves like the dense graphics cases: grouped CuPy slows rapidly as the sampled point count grows, while RTDL/OptiX remains sub-second. The 262k rows are 11.6x to 12.5x faster than grouped CuPy.
- The Natural Earth lakes/parks row is sparse and target-small. It is correct and still faster, but only by 1.2x to 1.5x. This is likely launch/overhead limited, and it should not be used as a headline RT-core speedup row.

The result strengthens the earlier lesson: RTDL's generic RT traversal is most valuable when there is enough candidate geometry for pruning and nearest-witness reduction to dominate overhead.

## Claim Boundary

| Claim | Verdict |
| --- | --- |
| Public geo shapefile loader and deterministic vertex sampling | `accept` |
| Exact 2D projected-point Hausdorff against grouped CuPy for these artifacts | `accept` |
| RTDL/OptiX beats grouped CuPy on the measured detailed Census/ZCTA rows | `accept-with-boundary` |
| Sparse Natural Earth row is a large RT speedup | `not-claimed` |
| Original X-HD local WKT files reproduced exactly | `not-claimed` |
| Full geographic polygon/surface Hausdorff semantics | `not-claimed` |
| MRI/BraTS X-HD dataset reproduction | `not-claimed` |
| v2.0 release authorization | `not-authorized-here` |

Artifacts are in `docs/reports/goal2139_public_geo_pod_a5000/`.
