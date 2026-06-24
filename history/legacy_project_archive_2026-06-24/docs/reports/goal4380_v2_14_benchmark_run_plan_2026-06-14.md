# Goal4380 v2.14 Executable Benchmark Run Plan

Status: executable plan; not release evidence.

## Summary

- Validation: `accept_executable_plan`
- Release rows planned: `12`
- Human-scale same-contract rows: `11`
- RayJoin Section 5.7 overlay rows: `1`
- Public wording authorized rows now: `0`

## Rows

| Row | Runner | Evidence Status | Expected Artifact |
| --- | --- | --- | --- |
| hausdorff_xhd_threshold | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| spatial_rayjoin_lsi | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| spatial_rayjoin_pip | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| spatial_rayjoin_overlay | `rayjoin_section57_overlay` | requires_fresh_section57_overlay_run_8_of_8 | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.json` |
| rt_dbscan_core_flags_numba_signature | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| robot_collision_grouped_segment_flags | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| contact_manifold_aabb_collect_k | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| raydb_style_grouped_i64_count | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| barnes_hut_node_coverage | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| librts_spatial_index_aabb | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| rtnn_ranked_summary | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |
| triangle_counting_any_hit | `human_scale_same_contract` | requires_fresh_same_contract_human_scale_run | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json` |

## Commands

### hausdorff_xhd_threshold

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only hausdorff_xhd
```

### spatial_rayjoin_lsi

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only spatial_rayjoin_lsi
```

### spatial_rayjoin_pip

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only spatial_rayjoin_pip
```

### spatial_rayjoin_overlay

```bash
python3 scripts/rayjoin_section57_overlay_matrix.py run --dataset-root /workspace/rayjoin_section57_data/cdb_topology --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay --query-exec /workspace/RayJoin_fresh/release/bin/query_exec --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec --author-warmup 5 --author-repeat 5 --rtdl-warmup 1 --rtdl-repeat 3 --run-json docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_run.json --summary-json docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.json --summary-md docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.md
```

### rt_dbscan_core_flags_numba_signature

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only rt_dbscan
```

### robot_collision_grouped_segment_flags

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only robot_collision
```

### contact_manifold_aabb_collect_k

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only contact_manifold
```

### raydb_style_grouped_i64_count

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only raydb_style
```

### barnes_hut_node_coverage

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only barnes_hut
```

### librts_spatial_index_aabb

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only librts_spatial_index
```

### rtnn_ranked_summary

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only rtnn
```

### triangle_counting_any_hit

```bash
python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract --only triangle_counting
```

## Claim Boundary

The v2.14 benchmark cleanup gap matrix is a draft planning and validation surface. It does not authorize release action, tag action, public speedup wording, whole-application speedup wording, broad RT-core wording, RTDL-beats-RayJoin wording, RayJoin paper-reproduction wording, author-hot-compute parity wording, automatic partner selection, Intel/AMD GPU performance wording, true-zero-copy wording, or app-specific native engine logic.

This run plan only defines how to collect fresh evidence. The generated results still need phase-level review before any v2.14 public wording is authorized.
