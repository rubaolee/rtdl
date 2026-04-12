# Goal 282 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 282 hardened the 3D PostGIS path to use the n-D GiST opclass and verified the live query plan on real KITTI data.

## What Changed

- `src/rtdsl/external_baselines.py`
  - `prepare_postgis_point3d_tables(...)` now creates:
    - `USING GIST (geom gist_geometry_ops_nd)`
- `tests/goal281_postgis_3d_fixed_radius_baseline_test.py`
  - now verifies the n-D opclass request appears in the executed SQL

## Live Linux Plan Audit

Dataset shape:

- KITTI raw source root:
  - `/home/lestat/data/kitti_raw`
- bounded packages:
  - consecutive frames
  - `4096` points per package
  - `radius = 1.0`
  - `k_max = 1`

Observed key plan lines:

```text
->  Nested Loop
      ->  Seq Scan on rtdl_query_points3d_tmp q
      ->  Index Scan using rtdl_search_points3d_tmp_geom_gist on rtdl_search_points3d_tmp s
            Index Cond: (geom &&& st_expand(q.geom, '1'::double precision))
            Filter: st_3ddwithin(q.geom, geom, '1'::double precision)
```

Interpretation:

- this is not a naive full seq-scan join
- the probe side remains a sequential scan over all query rows, which is expected here
- the search side uses the 3D n-D GiST index
- the index broad phase is now 3D (`&&&`), not the earlier 2D broad phase (`&&`)

## Result

Goal 282 is complete. The live 3D PostGIS KITTI path now uses the correct indexed search strategy for the real bounded workload.
