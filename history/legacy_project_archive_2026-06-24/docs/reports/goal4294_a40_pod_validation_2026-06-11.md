# Goal4294: A40 Pod Validation After Remote Driver Hardening

Date: 2026-06-11

## Purpose

Validate the current v2.10 source on a live NVIDIA pod after the remote pod
driver/probe hardening from Goals 4285-4293.

This run targeted the user-provided pod:

- Host: redacted NVIDIA A40 pod endpoint
- GPU: NVIDIA A40
- Driver: `565.57.01`
- Source commit: `6a556994a5176a3acc8bad2557c0905caa893898`
- Working tree for the accepted scale-profile rerun: clean

## Bootstrap Repairs Needed On The Pod

The pod did not initially have every dependency needed by the v2.10 validation
bundle. The following environment fixes were applied before the accepted rerun:

- Installed OptiX headers from `NVIDIA/optix-dev` v8.0.0 under
  `/root/vendor/optix-dev`.
- Built `build/librtdl_optix.so` with CUDA 12.8 and the OptiX headers.
- Installed GEOS development headers and `pkg-config` for native oracle build
  paths.
- Pinned the Numba CUDA toolchain to a CUDA 12.4 NVVM package to avoid the
  pod driver's unsupported-PTX failure while keeping the native RTDL OptiX build
  on CUDA 12.8.
- Materialized the RayJoin public-CDB slice data outside the checkout at
  `/root/rtdl_v2_10_validation.2dkWdf/rayjoin_public_cdb_data` so the final
  scale-profile artifact remained source-clean.

## Accepted Artifact Packet

Copied artifacts are stored in:

`docs/reports/goal4294_a40_pod_validation_artifacts_2026-06-11/`

Key files:

- `source_tree_doctor.json`
- `benchmark_evidence_index.json`
- `front_door_hardware_summary.json`
- `large_scale_partner_comparison.json`
- `scale_profile_summary_clean.json`
- `scale_rows/*.json`

## Results

### Front-Door Hardware

`front_door_hardware_summary.json` reports:

- `all_pass`: `true`
- `row_count`: 10
- Release/public-speedup/broad-RT-core/paper-reproduction flags: all false

### Clean Scale Profile

`scale_profile_summary_clean.json` reports:

- `all_pass`: `true`
- `row_count`: 10
- `working_tree_clean`: `true`
- `source_commit_short`: `6a556994`
- Release/public-speedup/broad-RT-core/paper-reproduction flags: all false

Per-row wrapper elapsed times:

| Row | Status | Wrapper elapsed |
| --- | --- | ---: |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 s |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.780 s |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503 s |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 5.037 s |
| `contact_manifold_optix_scale_default_grid64` | pass | 0.752 s |
| `raydb_style_optix_count_scale_default_262k` | pass | 6.255 s |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 s |
| `librts_spatial_index_optix_scale_default_32768` | pass | 1.502 s |
| `rtnn_prepared_optix_scale_default_65536` | pass | 3.770 s |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.503 s |

The RayJoin row was the only missing row in the prior bundle attempt; it passed
after the required public-CDB fixture was materialized.

### Large-Scale Partner Comparison

`large_scale_partner_comparison.json` reports:

- `all_match_cpu_oracle`: `true`
- `all_partner_contract_totals_meet_one_second_floor`: `true`
- `subsecond_hot_total_rows`: `[]`
- Grouped suite hot total: CuPy `5.551 s`, Numba `11.538 s`
- Compact-mask suite hot total: CuPy `1.415 s`, Numba `39.412 s`

The comparison remains same-contract partner-continuation evidence only. It
does not claim universal partner superiority or whole-application speedup.

## Boundary

This goal records successful A40 hardware validation of the current v2.10
front-door, scale-profile, source-doctor, benchmark-index, and partner
comparison paths after pod bootstrap repairs.

It does not authorize release action, package-install wording, public speedup
wording, whole-app acceleration wording, broad RT-core wording, paper
reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4294_a40_pod_validation_test
```

## Verdict

`accept-with-boundary`: the A40 pod evidence is now complete for the current
v2.10 validation packet, with the claim boundary still intentionally narrow.
