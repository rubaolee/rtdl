# Backend Choice

Status: V3 rebuild tutorial.

Do not choose a backend by name. Choose it from row evidence.

The current repaired V3 evidence splits benchmark apps into these buckets:

| Bucket | Apps | User rule |
| --- | --- | --- |
| Strong current OptiX rows | `rt_dbscan`, `raydb_style`, `triangle_counting`, strengthened `spatial_rayjoin` rows | Use the exact measured route and keep the claim row-scoped. |
| Positive but scoped rows | `hausdorff_xhd`, `robot_collision`, `barnes_hut`, `contact_manifold` | Use OptiX for the measured path; do not describe whole-app acceleration. |
| Mixed rows | `rtnn`, standard all-workload `spatial_rayjoin` | Pick the route and distribution carefully. |
| Embree-better measured row | `librts_spatial_index` | Use Embree for the measured route unless new evidence changes it. |

Machine-readable classification:

```text
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
```

The lesson is simple: V3 is useful only when it tells the user what to run and
what not to claim.

Read next:

- [Benchmark Evidence](04_benchmark_evidence.md)
