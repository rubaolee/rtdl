# RTDL v2.14 Row-Scoped RT-Core vs Embree CPU Comparison

Status: released v2.14 row-scoped comparison matrix. This is public
row-scoped wording, not broad public wording.

Date: 2026-06-15

This table supersedes the earlier Goal4380 draft rows where Goal4381/Goal4383 produced stronger or more honest final evidence. In particular, RTDBSCAN must use the compact-Embree-threshold result, not the stale 8.55x draft row.

## Final Same-Contract Matrix

| Row | Contract | Partner policy | Final readout | Phase explanation | Public status |
| --- | --- | --- | --- | --- | --- |
| `rtnn_ranked_summary` | prepared 3D fixed-radius ranked-summary aggregate | exact row primitive-first; best row uses fixed CuPy same-stream continuation separately | exact OptiX 10.14x-11.80x faster than Embree; separate float32 best path 47.36x-89.85x | native aggregate removes summary-row/Python materialization; best path uses prepared queries, CUDA graph replay, and same-stream CuPy with precision caveat | ready as large RTNN-shaped row; no paper-dataset claim |
| `rt_dbscan_core_flags_numba_signature` | prepared fixed-radius count-threshold core flags plus component signature | fixed Numba prepared-grid continuation for backend comparison; Goal4389 also measures same-contract CuPy opponent | at 524,288 points, total 1.05x OptiX faster; threshold stage 1.37x faster; partner supplement: RT+Numba 8.900s vs RT+CuPy 10.662s | RT threshold stage is faster on OptiX, but shared Numba continuation is about 6.92s and dominates total; Numba is current best measured partner for this contract | ready only as narrow engineering row |
| `spatial_rayjoin_lsi` | prepared segment-pair scalar count | primitive-first | OptiX 29.93x faster in Goal4380 matrix | scalar count avoids intersection-row materialization | ready as scalar-count row, not full paper reproduction |
| `spatial_rayjoin_pip` | prepared PIP scalar count | primitive-first final row; other partner routes separated | OptiX 1.10x faster in Goal4380 matrix | PIP scalar count is short and output-light; modest gain is plausible | ready only with modest-speedup wording |
| `spatial_rayjoin_overlay` | Section 5.7 overlay app route over the available exact CDB subset | app orchestration; no hidden partner comparison | 2 exact-ready pairs: OptiX 2.61x and 1.88x faster than Embree | RTDL app wall is not author hot-compute parity; the other 6/8 exact inputs are unavailable in the current public/pod artifact set | ready for available 2/8 exact-subset wording; not full Section 5.7 reproduction |
| `raydb_style_grouped_i64_count` | prepared ray/triangle grouped i64 reduction count | primitive-first native grouped reduction | OptiX 14.05x faster per iteration in Goal4380 matrix | grouped reduction avoids hit-stream materialization; totals used different repeats | ready as generated RayDB-style row |
| `librts_spatial_index_aabb` | generic prepared `AABB_INDEX_QUERY_2D` all-ops | primitive-first | at 1M boxes x 1K queries, hot query 13.39x faster; cold total 2.27x faster | hot query is traversal-heavy; cold total includes scene build | ready with hot-query/cold-total split |
| `triangle_counting_any_hit` | prepared weighted any-hit summary | primitive-first | largest row total 2.44x faster; hot query 107.61x faster | RT cores dominate any-hit traversal, while Python graph lowering and prepare compress total speedup | ready as large synthetic RT-Graph-shaped row |
| `barnes_hut_node_coverage` | prepared fixed-radius node-coverage threshold decision | primitive-first | 1,000,000 bodies x 65,536 nodes: hot query 2.06x faster | node-coverage traversal benefits from RT cores; force-vector work is excluded | ready as node-coverage only |
| `hausdorff_xhd_threshold` | prepared fixed-radius threshold decision | primitive-first | 1,048,576 points per side: directed hot-query sum 1.58x faster | compact threshold decision is traversal-heavy but not exact nearest-witness Hausdorff | ready as threshold decision only |
| `robot_collision_grouped_segment_flags` | prepared grouped-segment any-hit flags | primitive-first prepared buffers | 1,048,576 groups: total 1.86x faster; traversal 6.69x faster | traversal is RT-core friendly; shared output/postprocess compresses total | ready as discrete sampled any-hit flags |
| `contact_manifold_aabb_collect_k` | generic AABB broadphase plus bounded witness rows | primitive-first broadphase; Python refinement app-owned | `jittered_grid_65536`: AABB query 1.23x faster; hot path 1.16x faster | broadphase traversal is faster on OptiX, but bounded rows and Python refinement dominate enough to keep speedup modest | ready as broadphase/contact-witness row |

## Required Interpretation Rules

- Do not compare stale v2.13 or early Goal4380 draft rows against final Goal4381/Goal4383 closeout rows.
- Do not compare different partners as if they were backend-only differences.
- For RTDBSCAN, keep the fixed-Numba OptiX-vs-Embree backend comparison separate from the Goal4389 CuPy-vs-Numba partner supplement.
- Do not publish a speedup without the phase explanation in this file or the linked report.
- Do not call a process-wall comparison author-hot-compute parity.
- Keep RayJoin LSI, PIP, and overlay as separate contracts.
- Keep RTDL-vs-Embree same-route claims separate from RTDL-vs-author-code claims.
- Keep full 8/8 RayJoin Section 5.7 wording blocked. The promoted overlay row is only the available 2/8 exact CDB subset.

## Evidence Reports

- `docs/reports/goal4381_rtnn_aggregate_large_2026-06-14.md`
- `docs/reports/goal4383_rt_dbscan_embree_compact_threshold_2026-06-14.md`
- `docs/reports/goal4389_rtdbscan_partner_dual_implementation_2026-06-15.md`
- `docs/reports/goal4380_v2_14_pod_benchmark_execution_2026-06-14.md`
- `docs/reports/goal4383_librts_large_aabb_2026-06-14.md`
- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14.md`
- `docs/reports/goal4383_barnes_hut_fixed_depth_node_coverage_2026-06-14.md`
- `docs/reports/goal4383_hausdorff_large_threshold_2026-06-14.md`
- `docs/reports/goal4383_robot_collision_large_prepared_buffers_2026-06-14.md`
- `docs/reports/goal4383_contact_jittered_aabb_2026-06-14.md`
