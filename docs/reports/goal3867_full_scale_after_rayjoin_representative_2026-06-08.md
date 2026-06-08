# Goal3867 Full Scale Refresh After Representative RayJoin Row

Date: 2026-06-08

Status: implemented and A5000-validated.

## Purpose

Goal3866 replaced the old short RayJoin PIP-only scale row with a
representative bounded public-CDB mixed route. Goal3867 reruns the full ten-app
scale-profile harness against that registry so the project has a current green
packet with the stronger RayJoin row.

This is an internal scale-profile packet. It is not a release packet and does
not authorize public speedup, RayJoin paper reproduction, broad RT-core, true
zero-copy, or automatic partner-selection claims.

## Artifact

`docs/reports/goal3867_full_scale_after_rayjoin_representative_a5000/summary.json`

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Measured clean checkout commit:

`d598ed59`

The artifact was produced from a clean clone, with the JSON output directory
outside the repo so embedded git-status fields in child payloads remain clean.

## Results

`all_pass: true`

`json_pass_count: 10`

| App | Row | Status | Elapsed sec |
| --- | --- | --- | ---: |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | pass | `2.002` |
| `spatial_rayjoin` | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | `10.256` |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | `3.503` |
| `robot_collision` | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | `1.536` |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | pass | `0.752` |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | pass | `2.002` |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | pass | `1.752` |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | pass | `2.002` |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | pass | `3.003` |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | `1.502` |

The RayJoin row writes progress to stderr because it runs inherited Numba and
PIP-batch probes. The scale runner still marks it pass because stdout is clean,
parseable JSON and no forbidden claim flags are set.

## Interpretation

This is the first current all-app scale packet where `spatial_rayjoin` is not a
tiny PIP-only smoke. The row now exercises:

- Numba one-shot PIP scalar count;
- RTDL/OptiX repeated PIP batch executor;
- RTDL/OptiX LSI scalar count;
- RTDL/OptiX overlay active count.

That better matches the benchmark-app guidance: users choose routes explicitly;
RTDL/OptiX is the recommended route where the generic primitive expresses the
answer, and Numba is the no-RawKernel partner reference where one-shot custom
logic is still better.

## Boundary

Goal3867 does not authorize release action, public speedup wording, whole-app
RayJoin speedup wording, RayJoin paper-reproduction wording, broad RT-core
wording, true-zero-copy wording, automatic partner selection, AMD performance
wording, or app-specific native-engine logic.

