# Goal4182 Current Benchmark Scale-Profile Refresh on RTX 4000 Ada

Date: 2026-06-09

Status: internal evidence accepted with boundary

## Purpose

Goal4182 refreshes the current 10 benchmark app scale-profile packet after the
Goal4176-4181 RT-DBSCAN all-items direct-status work. This is a broad sanity
and direction check for the current major-performance lane: it verifies that the
current benchmark front doors still run on a clean NVIDIA pod, records useful
hot-path timing signals, and keeps release/public-claim boundaries closed.

This report does not authorize a release, public speedup wording, broad RT-core
wording, whole-app acceleration wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.

## Pod And Source

- Pod: `ssh root@157.157.221.29 -p 24101 -i ~/.ssh/id_ed25519`
- Effective RTDL working key used by Codex: `id_ed25519_rtdl_codex`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`
- Source commit: `79afb95a65bfb7a359efb56210294c89ec210060`
- Runner: `scripts/goal3828_current_benchmark_scale_profile_runner.py`
- Artifact: `docs/reports/goal4182_current_benchmark_scale_profile_refresh_rtx4000ada/current_scale_profile_packet.json`

The final packet was run from a clean source worktree. RayJoin public-CDB input
files were generated outside the repository worktree from the public RayJoin raw
text samples using the existing `scripts/goal2159_rayjoin_public_cdb_runner.py`
slice materialization path.

## Packet Result

The final packet passed all ten promoted benchmark rows (`10/10`):

| App | Row | Status | Runner wall sec | Key timing signal |
| --- | --- | ---: | ---: | --- |
| Hausdorff/X-HD | `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 | threshold-count query `0.007604s` |
| Spatial RayJoin | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.256 | PIP one-shot OptiX/Numba `0.252x`; LSI OptiX/Numba `259.5x`; overlay OptiX/Numba `212.9x`; repeated PIP batch `1.243x` per request |
| RT-DBSCAN | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503 | adapter elapsed `0.096349s`; grouped native `0.090601s` |
| Robot collision | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 5.057 | traversal total `1.990741s`; traversal median `0.00003952s` |
| Contact manifold | `contact_manifold_optix_scale_default_grid64` | pass | 0.752 | native collect `0.000451s` |
| RayDB-style | `raydb_style_optix_count_scale_default_262k` | pass | 6.504 | primitive-first grouped i64 reduction |
| Barnes-Hut | `barnes_hut_numba_scale_default_8192` | pass | 1.752 | Numba force-kernel median `0.009043s`; no raw CUDA kernel required |
| LibRTS spatial index | `librts_spatial_index_optix_scale_default_32768` | pass | 2.002 | query median `0.045810s` |
| RTNN | `rtnn_prepared_optix_scale_default_65536` | pass | 3.253 | elapsed median `0.000223s`; emitted `65,536`; raw candidates `206,256` |
| Triangle counting | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.502 | query median `0.182286ms` |

## Interpretation

This packet is more useful as a route-health and bottleneck map than as a final
performance claim. The strongest current signals are:

- Spatial RayJoin remains split by contract: one-shot bounded PIP still favors
  simple Numba CUDA logic, while LSI scalar count and overlay active count
  strongly favor fused app-agnostic RTDL/OptiX primitives.
- RT-DBSCAN current conservative grouped-stream route still runs cleanly after
  the all-items direct-status work, while the Goal4177 declared all-items route
  remains a separate explicit proof route rather than a universal default.
- Primitive-first routes remain healthy for RayDB-style grouped count,
  triangle counting, robot collision, RTNN, LibRTS, contact manifold, and
  Hausdorff/X-HD scale-profile smoke.
- Partner-required rows are still explicit. The packet does not choose partners
  automatically for users.

## Boundary

All release/public-claim flags in the packet remain false. The packet records
internal engineering evidence only. Any future release packet must still be a
separate, user-requested artifact with external review and the required
3-AI consensus for public claims.
