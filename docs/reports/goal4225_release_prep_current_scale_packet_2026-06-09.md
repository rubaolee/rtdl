# Goal4225 Release-Prep Current Scale Packet

Date: 2026-06-09

Status: internal release-prep evidence accepted with boundary

## Purpose

Goal4225 reruns the ten current benchmark front doors after the Goal4222,
Goal4223, and Goal4224 route-policy updates. The intent is to verify that the
current promoted benchmark surface is still green on a clean NVIDIA pod before
any future release-grade long-run or consensus packet.

This is not a release authorization. The current scale registry still contains
rows marked `internal_current_scale_not_claim_grade`, so this packet is best
read as a clean current-state health packet.

## Hardware And Source

- Hardware: ephemeral RTX cloud validation pod; live SSH endpoint and local key
  names intentionally redacted from tracked evidence.
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`
- Source commit: `0d9786ca`
- Pod tracked working tree: clean
- Runner: `scripts/goal3828_current_benchmark_scale_profile_runner.py`
- Artifact root: `docs/reports/goal4225_release_grade_current_scale_packet_rtx4000ada/`

## Result

All ten current benchmark rows passed with parseable JSON stdout and no
forbidden claim flags.

| App | Row | Status | Wrapper sec | Runtime class |
| --- | --- | --- | ---: | --- |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | pass | `1.50` | `safe_but_short` |
| `spatial_rayjoin` | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | `10.51` | `representative_mixed_route_public_cdb` |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | `3.50` | `default_scale_prepared_repeat_no_validation` |
| `robot_collision` | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | `5.00` | `resident_high_repeat_hot_path_summary_no_probe_reference` |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | pass | `0.75` | `safe_but_short` |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | pass | `6.75` | `resident_high_repeat_hot_path_summary` |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | pass | `1.75` | `safe_summary_output` |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | pass | `2.00` | `safe_medium` |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | pass | `3.25` | `safe_medium` |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | `1.50` | `safe_but_short` |

## Interpretation

The current v2.10 internal benchmark surface is healthy on RTX 4000 Ada:

- All ten front doors execute successfully from the declared scale-profile
  registry.
- The pod run uses a clean tracked worktree at `0d9786ca`.
- The semantic stdout scan finds no release, public speedup, whole-app,
  broad RT-core, paper-reproduction, true-zero-copy, automatic partner
  selection, AMD, or app-specific native-engine claim leakage.
- Prepared-session residency metadata remains attached for the four scene-heavy
  rows covered by that registry.

The remaining major release work is not another narrow app tweak. It is either
a formal longer-duration release matrix and docs/consensus pass, or AMD/HIPRT
functional parity once AMD hardware is available.

## Boundary

Goal4225 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
