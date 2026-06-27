# Benchmark Apps

These are the 10 RTDL V4 benchmark apps.

Read [../../tutorials/current/06_benchmark_apps.md](../../tutorials/current/06_benchmark_apps.md)
first. It teaches the relation, operator, partner, and continuation used by
each app.

| App | Source |
| --- | --- |
| RTDBSCAN | `rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` |
| RTNN | `rtnn/rtdl_rtnn_benchmark_app.py` |
| Triangle counting | `triangle_counting/rtdl_triangle_counting_benchmark_app.py` |
| Robot collision | `robot_collision/rtdl_robot_collision_benchmark_app.py` |
| RayDB-style query | `raydb_style/rtdl_raydb_style_benchmark_app.py` |
| LibRTS spatial index | `librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py` |
| Contact manifold | `contact_manifold/rtdl_contact_manifold_benchmark_app.py` |
| Spatial RayJoin | `spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` |
| Barnes-Hut | `barnes_hut/rtdl_barnes_hut_benchmark_app.py` |
| Hausdorff XHD | `hausdorff_xhd/rtdl_hausdorff_distance_app.py` |

For a quick learning map, run:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\benchmark_app_recipes.py
```
