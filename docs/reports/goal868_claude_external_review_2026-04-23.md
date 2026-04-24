---

## Verdict: ACCEPT

- **All four source files exist** and contain the exact strings the script searches for: `run_bfs_expand_optix_host_indexed(` and `run_triangle_probe_optix_host_indexed(` appear in both `rtdl_optix_workloads.cpp` (lines 1307, 1405) and `rtdl_optix_api.cpp` (lines 560, 584), confirming both OptiX graph paths are host-indexed helpers with no RT-core traversal.
- **The public app guard is live in source**: `rtdl_graph_analytics_app.py` line 28 raises `RuntimeError` with the exact message the script checks, meaning any require-RT-core path is actively rejected today.
- **The support matrix entry is authoritative**: `app_support_matrix.py` marks `graph_analytics` as `performance_class=HOST_INDEXED_FALLBACK` (line 337) and carries the redesign-or-exclusion note at line 617 — both match the script's substring checks precisely.
- **Tests use synthetic stubs that mirror the real strings**, so they validate detection logic but not real-source state; however, the direct grep above confirms real-source truth independently, making the MD report's five `True` flags accurate as of current HEAD.
