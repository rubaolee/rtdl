# RTDL Research Benchmarks

These are the current benchmark-app entry points for RTDL v2.14. They are serious reconstruction instruments for RTDL language/runtime design, but they are not broad paper-reproduction or whole-application speedup claims.

Run from the repository root with `PYTHONPATH=src:.`. Start with `--help` or the portable `cpu_python_reference` backend when an app exposes it; use native backends only after local dependencies are configured.

| Benchmark | Directory | Entry point | RTDL-owned kernel shape | Boundary |
| --- | --- | --- | --- | --- |
| Hausdorff / X-HD-Style | `hausdorff_xhd/` | `hausdorff_xhd/rtdl_hausdorff_distance_app.py` | prepared nearest/fixed-radius style distance decision | Not exact Hausdorff proof or universal CUDA speedup. |
| Spatial RayJoin-Style | `spatial_rayjoin/` | `spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | segment/polygon and point-in-polygon shaped spatial-query phases | Not full RayJoin paper reproduction or RTDL-beats-RayJoin claim. |
| RT-DBSCAN-Style | `rt_dbscan/` | `rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` | fixed-radius/core-flag phases plus explicit partner continuation where used | Not DBSCAN-native engine ABI or arbitrary clustering acceleration. |
| Robot Collision Screening | `robot_collision/` | `robot_collision/rtdl_robot_collision_benchmark_app.py` | prepared static-scene collision flags/counts | Not full robot planner, physics simulator, or swept-collision solver. |
| Bounded Contact Witness | `contact_manifold/` | `contact_manifold/rtdl_contact_manifold_benchmark_app.py` | AABB broadphase plus bounded witness rows | Not complete contact manifold or solver semantics. |
| RayDB-Style Grouped Aggregate | `raydb_style/` | `raydb_style/rtdl_raydb_style_benchmark_app.py` | ray/triangle grouped count and grouped sum contracts | Not SQL engine, DBMS, or whole RayDB paper reproduction. |
| Barnes-Hut / RT-BarnesHut-Style | `barnes_hut/` | `barnes_hut/rtdl_barnes_hut_benchmark_app.py` | aggregate/node-coverage traversal and frontier-style candidates | Not force integration, full N-body solver, or app-specific force primitive. |
| LibRTS-Style Spatial Index | `librts_spatial_index/` | `librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` | AABB/spatial-index shaped point/range query contract | Not full mutable LibRTS reproduction or universal spatial-index replacement. |
| RTNN Neighbor Search | `rtnn/` | `rtnn/rtdl_rtnn_benchmark_app.py` | prepared fixed-radius and ranked-summary neighbor contracts | Not full RTNN paper reproduction or arbitrary ANN-index acceleration. |
| Triangle Counting | `triangle_counting/` | `triangle_counting/rtdl_triangle_counting_benchmark_app.py` | RT-Graph-style graph relationship counting over generic traversal/reduction contracts | Not broad graph database or all-dataset triangle-counting speedup. |

Older benchmark notes and development records are archived under `history/examples_internal/research_benchmark_docs_2026-06-30/` and `history/internal_docs/`. They are not required for first-time use.
