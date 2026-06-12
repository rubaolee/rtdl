# Goal4329 Current Pod Validation After v2.11 Surface Fixes

Date: 2026-06-11

## Purpose

Validate the current staged v2.11 working tree on a fresh NVIDIA pod after the
Goal4317 grouped-reduction route, Goal4320 programming-surface truthfulness,
Goal4323 dense group-id metadata, and Goal4326 versioning glossary changes.

This is a hardware validation packet, not a release authorization. The packet
keeps all public/release/speedup/zero-copy claim flags false.

## Pod And Source

| Field | Value |
| --- | --- |
| Pod | live RTX 4000 Ada RunPod endpoint, redacted per Goal4303 security guard |
| GPU | NVIDIA RTX 4000 Ada Generation, driver `550.127.05`, 20475 MiB |
| Base commit | `bf12a82bdda5f067da9ffb16a355a212f6280e70` |
| Source state | base commit plus current tracked diff and selected untracked v2.11 files |
| CUDA | `/usr/local/cuda-12.8`, `nvcc 12.8.93` |
| OptiX headers | `/root/vendor/optix-sdk`, `optix-dev v8.0.0` |
| Partner stack | `numba==0.60.0`, `numpy==2.0.2`, `cupy-cuda12x==14.1.1`, `nvidia-cuda-nvcc-cu12==12.4.131` |

## Setup Results

| Step | Result |
| --- | --- |
| GEOS/pkg-config install | pass |
| OptiX 8.0 header clone | pass |
| Partner smoke | pass (`partner_smoke_ok`) |
| `make build-optix` | pass, produced `build/librtdl_optix.so` |
| Goal763 bootstrap | pass, `status: ok`; 35 focused OptiX tests passed |
| Source tree doctor | pass, `ok: true` |
| Goal3828 dry-run | pass, 10 selected rows |

## Clean Full Scale Packet

Artifact root: `docs/reports/goal4329_current_pod_validation/`

Primary all-pass summary:
`docs/reports/goal4329_current_pod_validation/scale_summary_allpass.json`

| Row | Status | Wrapper sec | Hot-path status |
| --- | ---: | ---: | --- |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 | smoke/internal |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.506 | smoke/internal |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503 | smoke/internal |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 5.003 | floor met, internal evidence only |
| `contact_manifold_optix_scale_default_grid64` | pass | 0.752 | smoke/internal |
| `raydb_style_optix_count_scale_default_262k` | pass | 6.754 | floor met, internal evidence only |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 | smoke/internal |
| `librts_spatial_index_optix_scale_default_32768` | pass | 2.002 | smoke/internal |
| `rtnn_prepared_optix_scale_default_65536` | pass | 3.252 | smoke/internal |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.502 | smoke/internal |

Summary verdict:

- `all_pass: true`
- `json_pass_count: 10`
- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_rt_core_claim_authorized: false`
- `paper_reproduction_claim_authorized: false`

## RayJoin Data-Staging Note

The first full packet intentionally remains in the artifact directory as
diagnostic evidence: `scale_summary.json` reports `9/10` because the fresh pod
did not yet contain the public-CDB RayJoin fixture. The failing stderr says:

`RayJoin public-CDB data directory not found`

This was corrected by materializing the required public-CDB slices with the
existing Goal2159 downloader/materializer:

- `br_county_start256_count512.cdb`
- `br_soil_start256_count512.cdb`

After setting `RTDL_RAYJOIN_PUBLIC_CDB_DIR`, the single RayJoin rerun passed,
then the clean full `scale_summary_allpass.json` packet passed all 10 rows.

## RayJoin Hot-Path Snapshot

From the all-pass RayJoin row:

| Contract | Recommended route | Metric |
| --- | --- | ---: |
| PIP one-shot | Numba CUDA JIT scalar count | RTDL/OptiX is `0.253x` vs Numba |
| PIP repeated requests | RTDL/OptiX prepared batch executor | `1.25x` per-request speedup vs single request |
| LSI scalar count | RTDL/OptiX prepared segment-pair count | `247.55x` vs Numba |
| Overlay active count | RTDL/OptiX prepared shape-pair active count | `209.88x` vs Numba |

This is contract-level internal evidence. It is not a full RayJoin paper
reproduction claim and does not authorize broad public performance wording.

## Boundary

This packet does not authorize a release.

Goal4329 proves that the current staged v2.11 source tree can be built and run
on an RTX 4000 Ada pod with the current 10-row benchmark scale packet. It does
not authorize a release, package-install claim, whole-app speedup claim, broad
RT-core claim, paper-reproduction claim, true-zero-copy claim, automatic partner
selection, or app-specific native-engine logic.
