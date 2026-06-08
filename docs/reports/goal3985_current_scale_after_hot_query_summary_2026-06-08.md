# Goal3985 Current Scale After Resident Hot-Query Summary

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3985 validates the Goal3984 resident high-repeat hot-query summary contract on a fresh RTX 4000 Ada pod checkout.

## Pod Setup

- Pod: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `accc84daf76846d29d91fa8a145187851e941f04`
- Fresh checkout: yes
- Helper: `scripts/goal3975_current_scale_partner_pod_setup.sh`
- Partner smoke: `partner_smoke_ok`
- OptiX build: `make build-optix`

## Full Current-Scale Result

Artifact: `docs/reports/goal3985_current_scale_after_hot_query_summary_2026-06-08/summary.json`

| Metric | Value |
| --- | ---: |
| `all_pass` | `true` |
| `json_pass_count` | `10` |
| row count | `10` |
| runner stderr | empty |

## Row Timing Summary

| Row | Status | Wrapper elapsed sec | Stdout bytes |
| --- | --- | ---: | ---: |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 | 7,398 |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.506 | 8,327 |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.252 | 20,202 |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 5.278 | 6,230 |
| `contact_manifold_optix_scale_default_grid64` | pass | 0.751 | 7,675 |
| `raydb_style_optix_count_scale_default_262k` | pass | 7.004 | 43,046 |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 | 3,810 |
| `librts_spatial_index_optix_scale_default_32768` | pass | 2.002 | 5,333 |
| `rtnn_prepared_optix_scale_default_65536` | pass | 3.253 | 8,064 |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.502 | 11,857 |

## Short-Row Calibration Result

The two former short rows now produce seconds-level aggregate hot-path summaries without per-repeat JSON bloat.

| Row | Suppression check | Aggregate hot-path metric | Value sec |
| --- | --- | --- | ---: |
| `raydb_style_optix_count_scale_default_262k` | `prepared_iteration_wall_sec_suppressed=true`, array length `0` | `metadata.prepared_phase_timing_summary.native_call_wall.total_sec` | 3.012 |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | `run_details_suppressed=true`, `runs` length `0` | `run_summary.phase_timing_seconds.traversal.total_sec` | 2.036 |

The corresponding aggregate wrapper-level totals remain separate:

- RayDB prepared iteration wall total: 4.670 sec
- Robot measured total-run total: 3.200 sec

## Boundary

This validates measurement quality for the current internal scale profile. It does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic. Wrapper elapsed remains pod-budget evidence; the representative metrics are explicit aggregate hot-path summaries.

## Next Step

The short-row measurement problem is now closed at the current-scale registry level. The next performance work should move back to runtime design: improve benchmark-app throughput using larger generic primitives and resident execution contracts, not by tuning loader setup or JSON output.
