# Goal 1603: v1.6 Stable Native-Path App-Leakage Audit

## Verdict

The stable `v1.6` Python+RTDL release boundary can remain app-generic at the
public primitive-contract level, but the native engine tree is not fully
app-agnostic internally.

This audit does not block the `v1.6` architecture anchor if the release wording
continues to limit the stable surface to RTDL primitive paths and explicitly
excludes compatibility, proof, experimental, and app-shaped native entry points.
It does block any claim that native internals are fully app-agnostic.

`v1.6` remains unpublished. This audit does not authorize release/tag action,
public speedup wording, true zero-copy wording, partner tensor handoff claims,
or stable `COLLECT_K_BOUNDED` promotion.

## Stable Primitive Boundary

The stable primitive boundary for the `v1.6` Python+RTDL track remains:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`

Representative Embree native exports that match this primitive boundary include:

- `rtdl_embree_run_ray_anyhit`
- `rtdl_embree_run_ray_anyhit_3d`
- `rtdl_embree_run_ray_hitcount`
- `rtdl_embree_run_ray_hitcount_3d`
- `rtdl_embree_run_grouped_count`
- `rtdl_embree_run_grouped_sum`
- `rtdl_embree_run_fixed_radius_count_threshold`

Representative OptiX native exports that match this primitive boundary include:

- `rtdl_optix_run_ray_anyhit`
- `rtdl_optix_run_ray_anyhit_3d`
- `rtdl_optix_run_ray_hitcount`
- `rtdl_optix_run_ray_hitcount_3d`
- `rtdl_optix_run_grouped_count`
- `rtdl_optix_run_grouped_sum`
- `rtdl_optix_run_fixed_radius_count_threshold`

These names are acceptable for the stable primitive surface because they describe
RTDL primitive behavior rather than application domains.

## App-Shaped Compatibility And Proof Paths

The native tree still contains app-shaped, workload-shaped, or proof-oriented
entry points. Examples found during this audit include:

- GIS/polygon names such as `rtdl_embree_run_pip`, `rtdl_optix_run_pip`,
  `rtdl_embree_run_shape_pair_relation_flags`, `rtdl_optix_run_shape_pair_relation_flags`,
  `rtdl_embree_run_segment_polygon_hitcount`, and
  `rtdl_optix_run_segment_polygon_hitcount`.
- Candidate-collection names such as
  `rtdl_embree_collect_polygon_pair_candidates_bounded` and
  `rtdl_optix_collect_polygon_pair_candidates_bounded`.
- Database-shaped names such as `rtdl_embree_db_dataset_grouped_sum`,
  `rtdl_optix_db_dataset_grouped_sum`, and
  `rtdl_optix_db_dataset_compact_summary_batch`.
- Workload-specific metric names such as
  `rtdl_embree_run_directed_hausdorff_2d`.
- Graph and workload proof names such as `rtdl_embree_run_bfs_expand`,
  `rtdl_optix_run_bfs_expand`, `rtdl_embree_run_conjunctive_scan`, and
  `rtdl_optix_run_conjunctive_scan`.
- Robot/pose-shaped prepared-index names such as
  `rtdl_optix_prepare_pose_indices_2d`,
  `rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices`, and
  `rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices`.

These paths may remain in the repository as compatibility, historical, internal,
or proof surfaces, but they must not be used as evidence that `v1.6` native
internals are fully app-agnostic.

## Pending Primitive Boundary

`COLLECT_K_BOUNDED` remains pending and experimental for the `v1.6` closure
boundary. The native tree contains generic-looking bounded collection exports,
including `rtdl_embree_collect_k_bounded_i64`,
`rtdl_optix_collect_k_bounded_i64`, and
`rtdl_optix_collect_k_bounded_i64_device`, but their presence does not promote
the primitive to the stable `v1.6` surface.

The promotion track still requires fail-closed semantics, exact bound tests,
bounded result buffers, Embree/OptiX parity where claimed, benchmarks, real
NVIDIA evidence for OptiX claims, and external review.

## Claim Boundary

Allowed wording:

```text
The v1.6 Python+RTDL release surface is app-generic at the stable RTDL
primitive-contract level for the listed supported primitives.
```

Blocked wording:

```text
RTDL native internals are fully app-agnostic.
```

```text
All native exports are app-name-free.
```

```text
The historical/proof app-shaped native paths are part of the stable v1.6 public
primitive surface.
```

```text
COLLECT_K_BOUNDED is stable in v1.6.
```

## Next Fixes

Before publishing `v1.6`, the final release statement and support matrix should
keep this distinction visible:

- Stable public surface: primitive-named Python+RTDL contracts backed by Embree
  and OptiX where validated.
- Excluded/internal surface: app-shaped compatibility and proof exports.
- Pending surface: `COLLECT_K_BOUNDED`, true zero-copy, partner tensor handoff,
  and public performance claims not yet backed by reviewed exact-subpath
  evidence.

Future hardening can either retire app-shaped native compatibility exports or
wrap/rename them behind app-free primitive packets. That work is useful, but it
is not required to continue the `v1.6` architecture-anchor path as long as the
public claim boundary stays narrow.
