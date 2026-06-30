# RTDL v2.14 Row-Scoped RT-Core Comparison

Status: current public v2.14 evidence table.

This table compares selected RTDL/OptiX rows against same-contract Embree CPU
baselines. It is row-scoped evidence, not a claim that every app or every input
is faster.

## Same-Contract Rows

| Row | Contract | Partner policy | Public readout | Interpretation |
| --- | --- | --- | --- | --- |
| `rtnn_ranked_summary` | Prepared 3D fixed-radius ranked-summary aggregate | Primitive-first exact row; a separate best path uses fixed CuPy same-stream continuation | Exact OptiX path is about `10.14x` to `11.80x` faster than Embree; separate float32 best path is about `47.36x` to `89.85x` faster | Large RTNN-shaped row; not a full RTNN paper-dataset reproduction. |
| `rt_dbscan_core_flags_numba_signature` | Prepared fixed-radius count-threshold core flags plus component signature | Fixed Numba prepared-grid continuation for backend comparison | At 524,288 points, total is about `1.05x` faster on OptiX; threshold stage is about `1.37x` faster | RT threshold work benefits, but shared Numba continuation dominates total time. |
| `spatial_rayjoin_lsi` | Prepared segment-pair scalar count | Primitive-first | OptiX is about `29.93x` faster | Scalar count row only; not full RayJoin paper reproduction. |
| `spatial_rayjoin_pip` | Prepared PIP scalar count | Primitive-first final row; other partner routes are separate references | OptiX is about `1.10x` faster | Modest same-contract row; do not inflate it into broad polygon-overlay wording. |
| `spatial_rayjoin_overlay` | Section 5.7 overlay app route over available exact CDB subset | App orchestration; no hidden partner comparison | Two exact-ready pairs show about `2.61x` and `1.88x` OptiX-over-Embree speedups | Available 2/8 exact subset only; not a full 8/8 Section 5.7 reproduction. |
| `raydb_style_grouped_i64_count` | Prepared ray/triangle grouped i64 reduction count | Primitive-first native grouped reduction | OptiX is about `14.05x` faster per iteration | Generated RayDB-style row; not a SQL or DBMS claim. |
| `librts_spatial_index_aabb` | Generic prepared `AABB_INDEX_QUERY_2D` all-ops | Primitive-first | At 1M boxes x 1K queries, hot query is about `13.39x` faster; cold total is about `2.27x` faster | Hot query is traversal-heavy; cold total includes scene build. |
| `triangle_counting_any_hit` | Prepared weighted any-hit summary | Primitive-first | Largest row total is about `2.44x` faster; hot query is about `107.61x` faster | Prepared RT-Graph-shaped row; Python graph lowering and setup compress total speedup. |
| `barnes_hut_node_coverage` | Prepared fixed-radius node-coverage threshold decision | Primitive-first | 1,000,000 bodies x 65,536 nodes: hot query is about `2.06x` faster | Node-coverage traversal only; force-vector integration is outside this claim. |
| `hausdorff_xhd_threshold` | Prepared fixed-radius threshold decision | Primitive-first | 1,048,576 points per side: directed hot-query sum is about `1.58x` faster | Threshold decision only; not exact nearest-witness Hausdorff. |
| `robot_collision_grouped_segment_flags` | Prepared grouped-segment any-hit flags | Primitive-first prepared buffers | 1,048,576 groups: total is about `1.86x` faster; traversal is about `6.69x` faster | Discrete sampled any-hit flags; not a planner or physics simulator. |
| `contact_manifold_aabb_collect_k` | Generic AABB broadphase plus bounded witness rows | Primitive-first broadphase; Python exact refinement is app-owned | Jittered-grid 65,536 case: AABB query is about `1.23x` faster; hot path is about `1.16x` faster | Broadphase/contact-witness row only; downstream contact solving remains app logic. |

## Required Interpretation Rules

- Compare only same-contract rows.
- Do not compare different partners as if they were backend-only differences.
- Keep RayJoin LSI, PIP, and overlay as separate contracts.
- Keep RTDL-vs-Embree same-route claims separate from RTDL-vs-author-code
  claims.
- Keep full 8/8 RayJoin Section 5.7 wording blocked unless the missing exact
  input pairs are available and measured.
- For partner-dependent rows, name the partner and the partner boundary.
