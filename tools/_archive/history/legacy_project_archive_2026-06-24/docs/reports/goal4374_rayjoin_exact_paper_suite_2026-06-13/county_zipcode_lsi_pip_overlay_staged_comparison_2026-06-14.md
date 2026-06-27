# RayJoin County x Zipcode RTDL Comparison Packet

Date: 2026-06-14

Input status: same-source regenerated CDB from ArcGIS-derived topology under `/workspace/rayjoin_same_source_data/cdb_partial_topology`. This is not yet the recovered paper-preprocessed Dryad CDB.

## Current Verdict

| Program / phase | Author RT result | RTDL OptiX result | RTDL Embree result | Exactness verdict | Performance verdict |
| --- | ---: | ---: | ---: | --- | --- |
| LSI, paper LSI direction | 180,506 pairs | 180,506 pairs | 180,506 pairs | Exact count; OptiX pair dump previously matched author pair-for-pair. | Strong RT-core win: OptiX hot median 1.694 ms vs Embree 310.546 ms. |
| PIP, paper PIP direction | Count not emitted by normal author run | 3,823,790 positives | 3,823,790 positives | RTDL OptiX and Embree match each other; author count still needs diagnostic emission for this standalone program. | OptiX hot 89.860 ms vs Embree 196.839 ms; native traversal 9.381 ms vs 196.765 ms. |
| Overlay LSI direction | 181,629 intersections | 181,629 intersections | 181,629 intersections | Exact count; Embree fixed via AABB-candidate + RayJoin scaled-int refinement. | OptiX staged hot LSI materialization 4.776 s; Embree 5.893 s. |
| Overlay vertex PIP map0 in map1 | 7,030,924 positives | 7,036,936 positives | 7,036,951 positives | Not author-exact yet. Remaining gap is RayJoin internal scaled-coordinate PIP/SOS semantics, not RT traversal speed. | Do not use as final public overlay correctness claim. |
| Overlay vertex PIP map1 in map0 | 3,823,783 positives | 3,823,790 positives | 3,823,790 positives | Not author-exact yet, but close. Same root cause as above. | Do not use as final public overlay correctness claim. |
| Overlay full compute, staged packed cache | Author normal RT elapsed 7.012 s | 12.361 s | 17.102 s | LSI exact; PIP/face assignment not author-exact. | Current RTDL OptiX is 1.38x faster than RTDL Embree, but slower than RayJoin author RT. |

## Overlay Timing Detail

| Engine | Input mode | Total elapsed / total_sec | LSI hot | Vertex PIP map0 hot | Vertex PIP map1 hot | Midpoint PIP map0 hot | Midpoint PIP map1 hot |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RayJoin author RT | Serialized CDB cache | 7.012 s wall | 6.777 ms `Intersection edges` | included in `Computer output polygons` | included in `Computer output polygons` | included in `Computer output polygons` | included in `Computer output polygons` |
| RTDL OptiX RT cores | RTDL packed binary cache | 12.361 s | 4.776 s | 3.198 s | 1.640 s | 0.346 s | 0.572 s |
| RTDL Embree CPU | RTDL packed binary cache | 17.102 s | 5.893 s | 3.338 s | 2.705 s | 0.489 s | 0.584 s |

## What Changed In This Pass

| Area | Change |
| --- | --- |
| Embree overlay LSI | Replaced the slow/missing ray-user-geometry path for RayJoin overlay LSI with native Embree AABB collision candidates plus the same RayJoin scaled-int predicate refinement. Overlay-direction LSI now matches author/OptiX at 181,629 pairs. |
| RTDL overlay ingestion | Added a packed CDB fast loader and optional binary packed cache via `RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR`. Cache-hit load for County is ~0.30 s and Zip is ~0.15 s, instead of ~99 s of Python CDB dataclass load. |
| Overlay point-location semantics | Added `RTDL_RAYJOIN_CDB_QUERY_MAP_ID` plumbing so RTDL PIP can select RayJoin's query-map-specific boundary rule. This reduced semantic drift but did not close author exactness because author uses internal scaled edge coefficients. |

## Remaining Blocker

Overlay is not publishable as an exact RayJoin Section 5.7 reproduction yet. The LSI phase is exact and comparable. The PIP/face assignment phase still differs from author RT by small but real boundary-count deltas:

| Phase | Author | RTDL OptiX | OptiX delta | RTDL Embree | Embree delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vertex PIP map0 in map1 | 7,030,924 | 7,036,936 | +6,012 | 7,036,951 | +6,027 |
| Vertex PIP map1 in map0 | 3,823,783 | 3,823,790 | +7 | 3,823,790 | +7 |

Next required optimization/correctness work: implement the RayJoin CDB PIP route over internal scaled coordinates and edge coefficients, then re-run overlay. Until that lands, public wording should say: "RTDL has exact RayJoin LSI reproduction and a staged overlay compute prototype, but full overlay face-id reproduction is still blocked on RayJoin's internal-coordinate PIP semantics."

## Source Result Files

| Row | Result JSON |
| --- | --- |
| Author overlay normal timing | `/workspace/rayjoin_same_source_data/results/overlay_county_zipcode_author_rt_w0r1_probe.json` |
| Author overlay diagnostic counts | `/workspace/rayjoin_same_source_data/results/overlay_county_zipcode_author_rt_w0r1_diag_pip.json` |
| RTDL OptiX overlay staged cache | `/workspace/rayjoin_same_source_data/results/overlay_county_zipcode_rtdl_optix_compute_cached_qmap_w0r1.json` |
| RTDL Embree overlay staged cache | `/workspace/rayjoin_same_source_data/results/overlay_county_zipcode_rtdl_embree_compute_cached_qmap_w0r1.json` |
