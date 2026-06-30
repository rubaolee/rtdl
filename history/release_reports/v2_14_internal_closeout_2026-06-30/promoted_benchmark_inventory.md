# RTDL v2.14 Promoted Benchmark-App Inventory

Status: frozen for v2.14 closeout.

Date: 2026-06-15

This inventory defines the rows that may appear in the v2.14 row-scoped comparison packet. It does not authorize whole-application speedup wording, paper-reproduction wording, or a release tag.

## Frozen Rows

| Row | App | Contract | Partner policy | Data status | v2.14 status |
| --- | --- | --- | --- | --- | --- |
| `rtnn_ranked_summary` | RTNN | prepared 3D fixed-radius ranked-summary aggregate | primitive-first exact row; separate CuPy same-stream best row | large RTNN-shaped synthetic/paper-family stress, not paper-exact | public-review-ready with no paper-dataset claim |
| `rt_dbscan_core_flags_numba_signature` | RTDBSCAN | fixed-radius count-threshold core flags plus component signature | fixed Numba prepared-grid continuation | large synthetic clustered3D, correctness validated at small scale | public-review-ready only as narrow same-continuation engineering row |
| `spatial_rayjoin_lsi` | RayJoin LSI | prepared segment-pair scalar count | primitive-first | public CDB-derived subset, not full paper suite | public-review-ready as scalar-count row |
| `spatial_rayjoin_pip` | RayJoin PIP | prepared PIP scalar count | primitive-first for final matrix; CuPy/Numba routes remain separate references | public CDB-derived subset, not full paper suite | public-review-ready only with modest-speedup wording |
| `spatial_rayjoin_overlay` | RayJoin overlay | Section 5.7 overlay app route over the available exact CDB subset | app orchestration; no hidden partner comparison | 2/8 exact-ready Section 5.7 pairs; remaining six exact inputs unavailable in the current public/pod artifact set | public-review-ready for the available 2/8 exact subset; not a full 8/8 Section 5.7 reproduction |
| `raydb_style_grouped_i64_count` | RayDB-style | prepared ray/triangle grouped i64 reduction count | primitive-first native grouped reduction | large generated RayDB-style data | public-review-ready as generated/paper-shaped row |
| `librts_spatial_index_aabb` | LibRTS-style AABB | generic prepared `AABB_INDEX_QUERY_2D` all-ops | primitive-first | 100K/1M paper-like uniform fixtures, not exact paper artifact | public-review-ready with hot-query/cold-total split |
| `triangle_counting_any_hit` | Triangle counting | prepared triangle-scene weighted any-hit summary | primitive-first; optional CuPy preprocessing separated | large synthetic RT-Graph-shaped fixture | public-review-ready as prepared primitive row |
| `barnes_hut_node_coverage` | Barnes-Hut | prepared fixed-radius node-coverage threshold decision | primitive-first node coverage; force partner references separated | large synthetic fixed-depth quadtree cells | public-review-ready as node-coverage traversal only |
| `hausdorff_xhd_threshold` | Hausdorff/X-HD style | prepared fixed-radius threshold decision | primitive-first threshold decision | large synthetic tiled point sets with oracle decision | public-review-ready as threshold decision only |
| `robot_collision_grouped_segment_flags` | Robot collision | prepared grouped-segment any-hit flags | primitive-first prepared buffers; OptiX-only device-buffer path separated | large synthetic robot-like fixture | public-review-ready as discrete sampled any-hit flags |
| `contact_manifold_aabb_collect_k` | Contact manifold | generic AABB broadphase plus bounded witness rows | primitive-first broadphase; Python exact refinement is app-owned continuation | large deterministic jittered synthetic data | public-review-ready as AABB broadphase/contact-witness row |

## Excluded Or Internal-Only Rows

| Row | Reason |
| --- | --- |
| Full RayJoin Section 5.7 overlay matrix | Only 2/8 exact-ready pairs are available in the current public/pod artifact set. The 2/8 available subset is promoted; the unavailable 6/8 full-matrix claim is not. |
| RayJoin author-hot-compute parity | Current author numbers are process wall, not hot-compute parity. |
| Full RTDBSCAN paper reproduction | Paper datasets are absent and total time is continuation-dominated. |
| Full Barnes-Hut force solver | v2.14 measures node coverage, not force law or timestep integration. |
| Full contact-manifold physics solver | v2.14 measures broadphase/witness rows, not contact generation. |
| Exact Hausdorff witness-distance app | v2.14 measures threshold decision only. |
| AMD/Intel GPU rows | No available hardware evidence in this release packet. |

## Inventory Rule

Any row not listed here is outside v2.14 public wording unless a new inventory update, test gate, and external review explicitly add it.
