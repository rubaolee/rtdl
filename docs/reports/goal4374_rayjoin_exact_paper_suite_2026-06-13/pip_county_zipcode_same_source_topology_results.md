# RayJoin PIP Same-Source Topology Result

Date: 2026-06-13

This is not a recovered paper-preprocessed CDB result. The RayJoin Dryad preprocessed share is unavailable, so this run uses same-source regenerated County x Zipcode CDBs from ArcGIS pages. The base County CDB was regenerated with a topology-aware polygon-to-line merge so shared edges carry left/right face ids instead of duplicated one-sided polygon rings.

## Input Contract

| Field | Value |
| --- | ---: |
| Program | PIP |
| Pair | County x Zipcode |
| Base CDB segments | 8,662,896 |
| Query CDB points | 5,288,684 |
| Query stream | all points from query map S |
| Provenance | same_source_regenerated_cdb |
| Semantic parity check | first 500,000 query rows: OptiX vs Embree face_diff=0, segment_diff=0 |

## Hot Query Results

| Engine | Repeat | Count | Median hot/query time | Native traversal | Total measured hot time | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| RayJoin author RT | 1000 | n/a | 7.207 ms | n/a | about 7.207 s query total | Author `query_exec -query=pip -mode=rt`; serialized CDB reused |
| RTDL OptiX RT cores | 100 | 3,823,790 | 90.475 ms | 9.418 ms | 9.066 s | Includes Python/native call and point upload per repeat |
| RTDL Embree CPU | 100 | 3,823,790 | 192.358 ms | 192.297 ms | 17.198 s | Same CDB, same all-points stream, same hybrid boundary predicate |

## Interpretation

The RT-core traversal itself is now in the same performance class as the author RayJoin PIP kernel: 9.4 ms vs 7.2 ms on the same same-source topology input. RTDL's public Python-facing hot call is slower because it uploads the 5.29M point stream each repeat; the native traversal number is the cleanest hardware comparison.

Embree is semantically aligned but slower on this workload: RTDL OptiX native traversal is 20.4x faster than RTDL Embree native traversal, while RTDL OptiX hot-call median is 2.13x faster than RTDL Embree hot-call median.

This row is reasonable for public wording only if it is labeled as same-source regenerated topology, not exact paper-preprocessed input. Exact paper reproduction still requires the official or bit-equivalent preprocessed CDBs, plus LSI and full polygon overlay rows.
