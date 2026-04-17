# Goal 282: v0.5 PostGIS 3D Index Hardening And Plan Audit

Purpose:
- ensure the live 3D PostGIS KITTI path uses the correct 3D GiST opclass
- verify the live query plan is indexed rather than a naive full search
- preserve an explicit evidence trail for the PostGIS side before publishing the three-way benchmark

Success criteria:
- 3D temp-table preparation uses `gist_geometry_ops_nd`
- focused tests verify the n-D opclass is requested
- a live Linux `EXPLAIN ANALYZE` shows indexed execution on the search table for the real KITTI workload
- docs record the actual plan shape honestly

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
