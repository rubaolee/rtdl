# Research Benchmark Apps

This directory contains the 10 promoted benchmark apps used to validate RTDL as
a language/runtime, not just as a primitive library.

Start with [../../../tutorials/current/06_benchmark_apps.md](../../../tutorials/current/06_benchmark_apps.md).
That tutorial explains how each app is built from the current V4 front door,
generic operators, inherited prepared routes, and explicit partners.

## Apps

| App | Source |
| --- | --- |
| RTDBSCAN | `rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` |
| RayDB-style | `raydb_style/rtdl_raydb_style_benchmark_app.py` |
| Triangle counting | `triangle_counting/rtdl_triangle_counting_benchmark_app.py` |
| LibRTS spatial index | `librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` |
| Hausdorff XHD | `hausdorff_xhd/rtdl_hausdorff_distance_app.py` |
| Robot collision | `robot_collision/rtdl_robot_collision_benchmark_app.py` |
| Contact manifold | `contact_manifold/rtdl_contact_manifold_benchmark_app.py` |
| RTNN | `rtnn/rtdl_rtnn_benchmark_app.py` |
| Spatial RayJoin | `spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` |
| Barnes-Hut | `barnes_hut/rtdl_barnes_hut_benchmark_app.py` |

## Rule

Use V4 as the current system. If an app route is inherited from V2.14 or V3,
that is still part of V4 because V4 is the current superset. Do not describe an
inherited route as a new V4-only speedup.
