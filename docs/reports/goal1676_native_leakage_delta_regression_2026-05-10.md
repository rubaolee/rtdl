# Goal1676 Native Leakage Delta Regression

Date: 2026-05-10

Status: local regression guard for the v1.8 / v2.0 app-agnostic native-engine
track.

## Verdict

The local source tree now has a mechanical regression guard for the first two
native cleanup deltas:

- the five OptiX pose-shaped prepared any-hit native symbols removed by
  Goal1673 must stay absent;
- the old `rtdl_oracle_polygon` root wrapper removed by Goal1674 must stay
  absent;
- the replacement OptiX group-shaped prepared any-hit native symbols must stay
  present.

This does not pass the app-agnostic native-engine gate. It only prevents the
first migrated names from returning while the remaining database, graph,
polygon/GIS, KNN, Hausdorff, and Jaccard native families are migrated or
quarantined.

## Delta Against Goal1668

Removed from the strict native symbol set:

- `rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices`
- `rtdl_optix_destroy_prepared_pose_indices_2d`
- `rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed`
- `rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices`
- `rtdl_optix_prepare_pose_indices_2d`
- `rtdl_oracle_polygon`

Replacement OptiX symbols:

- `rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed`
- `rtdl_optix_prepare_group_indices_2d`
- `rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices`
- `rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices`
- `rtdl_optix_destroy_prepared_group_indices_2d`

## Remaining Boundary

The strict scanner still reports app-shaped native symbols. The current local
count includes known uppercase `RTDL_DB_*` constant matches, which must be
classified explicitly in the superseding release audit instead of silently
ignored.

Blocked wording remains:

```text
RTDL native internals are fully app-agnostic.
```

No pod validation was run.
