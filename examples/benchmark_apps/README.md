# Benchmark Apps

These are the 10 RTDL V4 benchmark apps.

Read [../../tutorials/current/06_benchmark_apps.md](../../tutorials/current/06_benchmark_apps.md)
first. It teaches the relation, operator, partner, and continuation used by
each app.

| App | Current V4 entry |
| --- | --- |
| RTDBSCAN | `rt_dbscan/v4_app.py` |
| RTNN | `rtnn/v4_app.py` |
| Triangle counting | `triangle_counting/v4_app.py` |
| Robot collision | `robot_collision/v4_app.py` |
| RayDB-style query | `raydb_style/v4_app.py` |
| LibRTS spatial index | `librts_spatial_index/v4_app.py` |
| Contact manifold | `contact_manifold/v4_app.py` |
| Spatial RayJoin | `spatial_rayjoin/v4_app.py` |
| Barnes-Hut | `barnes_hut/v4_app.py` |
| Hausdorff XHD | `hausdorff_xhd/v4_app.py` |

Each `v4_app.py` file is the clean current entrypoint. It shows the app's V4
relation, operators, and partners. Use `--run-harness -- --help` from that
entrypoint only when you need the full reproduction harness.

For a quick learning map, run:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\benchmark_app_recipes.py
```
