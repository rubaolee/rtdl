# Goal4235 Current-Head Rehearsal After Measurement Closure

Date: 2026-06-09

Status: internal current-head rehearsal accepted with boundary

## Purpose

Goal4235 reruns the ten promoted benchmark front doors on the current online
head after the Goal4228-4231 measurement-closure chain and Goal4234 external
review packet. This checks that the current source still executes cleanly on the
RTX 4000 Ada pod after the target-map and review commits.

This is not a release packet. It is not a public performance table. It is a
clean-head rehearsal packet that preserves the existing claim boundary.

## Environment

| Field | Value |
| --- | --- |
| Source commit | `726906872628a68716a76603feb7f71ce3c9a966` |
| Source short | `72690687` |
| Pod worktree clean before runner output | `true` |
| GPU | `NVIDIA RTX 4000 Ada Generation, 550.127.08, 20475 MiB` |
| Python | `/usr/bin/python3` |
| OptiX library | `/root/goal4177.dpBIx4/repo/build/librtdl_optix.so` |

## Rehearsal Table

| App | Row | Status | Wrapper sec | Runtime class |
| --- | --- | --- | ---: | --- |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | `pass` | `1.502` | `safe_but_short` |
| `spatial_rayjoin` | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | `pass` | `10.506` | `representative_mixed_route_public_cdb` |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | `pass` | `3.502` | `default_scale_prepared_repeat_no_validation` |
| `robot_collision` | `robot_collision_optix_scale_default_1024_no_probe_reference` | `pass` | `5.253` | `resident_high_repeat_hot_path_summary_no_probe_reference` |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | `pass` | `0.752` | `safe_but_short` |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | `pass` | `6.754` | `resident_high_repeat_hot_path_summary` |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | `pass` | `1.751` | `safe_summary_output` |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | `pass` | `2.002` | `safe_medium` |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | `pass` | `3.252` | `safe_medium` |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | `pass` | `1.501` | `safe_but_short` |

## Reading

All ten promoted front doors pass at the current source commit. This confirms
that the Goal4230 measurement-adequacy closure and Goal4231 target-map refresh
did not leave the current benchmark surface stale.

The packet still carries the current-scale registry boundary:

- short rows remain short-row health checks, not public timing claims,
- RayJoin remains a mixed-route representative profile, not a single paper
  reproduction number,
- RT-DBSCAN keeps the current unblocked single-pass route policy,
- three rows require Numba as an explicit reference partner, and
- all claim-authorization flags remain false.

## Remaining Release Gates

Goal4235 does not close the formal release gates. Those remain:

- exact public claim wording,
- user-facing docs audit,
- fresh multi-AI consensus over the exact release packet,
- AMD/HIPRT functional and timing evidence on real AMD hardware,
- optional additional long timing if a public performance table is requested.

## Boundary

Goal4235 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
