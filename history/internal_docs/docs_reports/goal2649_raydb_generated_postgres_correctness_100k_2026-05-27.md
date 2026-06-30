# Goal2648 RayDB PostgreSQL Correctness for Paper RT Backends

Status: `ok`.

## Provenance

- timestamp UTC: `2026-05-28T00:30:19Z`
- host: `4b7c6ab4b262`
- git commit: `43419882d805e9d71a798c901cb97f05d8b6c8c8`
- script: `/workspace/rtdl_goal2645/scripts/goal2648_raydb_postgres_rt_correctness.py`
- output JSON: `docs/reports/goal2649_raydb_generated_postgres_correctness_100k_2026-05-27.json`
- fixture kind: `generated`

## Matrix

| backend | mode | rows | PostgreSQL match | RT core | native symbol |
|---|---|---:|---|---|---|
| paper_rt_embree | count | 100000 | True | False | `rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction` |
| paper_rt_embree | sum | 100000 | True | False | `rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction` |
| paper_rt_optix | count | 100000 | True | True | `rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction` |
| paper_rt_optix | sum | 100000 | True | True | `rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction` |

## Boundary

- PostgreSQL is used here only as an external SQL correctness oracle for the RayDB-style fixture. It is not a performance baseline in this report.
