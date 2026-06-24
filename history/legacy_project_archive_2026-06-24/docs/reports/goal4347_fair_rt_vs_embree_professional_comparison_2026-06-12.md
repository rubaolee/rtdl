# Goal4347 Fair RT Hardware vs Embree CPU Comparison Packet

## Verdict

The pod now has a serious internal comparison packet: the full OptiX scale run is all-pass after the CUDA/PTX environment fix, Embree 4.3.0 is built and exercised, and ratio rows only use matched output contracts. This is NVIDIA RTX 4000 Ada versus Embree on an AMD EPYC CPU, not Intel CPU evidence.

## Ratio Rows

| App / contract | OptiX hot metric | Best Embree hot metric | Embree threads | Embree / OptiX | Faster | Note |
|---|---:|---:|---:|---:|---|---|
| `librts_spatial_index` / `generic_prepared_aabb_index_query_2d` | 0.000623803 s | 0.0626853 s | 8 | 100.49x | optix | clean_same_scale_query_phase |
| `hausdorff_xhd` / `directed_threshold_prepared_fixed_radius_count` | 0.00385349 s | 0.00974801 s | 8 | 2.53x | optix | clean_internal_query_ratio |
| `contact_manifold` / `native_collect_k_bounded_witness_rows` | 0.000443441 s | 0.000368218 s | 64 | 0.83x | embree | clean_internal_query_ratio |
| `triangle_counting` / `rt_graph_2a1_generic_ray_triangle_any_hit` | 0.155335 ms | 12.1083 ms | 8 | 77.95x | optix | clean_internal_query_ratio |
| `robot_collision` / `prepared_triangle_scene_grouped_segment_any_hit_same_scene_query_scale` | 4.0496e-05 s | 0.00118126 s | 8 | 29.17x | optix | boundary_limited_phase_ratio |
| `raydb_style` / `generated_grouped_count_same_rows_groups_boundary_limited_residency` | 0.000209818 s | 0.00787316 s | 64 | 37.52x | optix | boundary_limited_phase_ratio |
| `spatial_rayjoin` / `public_cdb_pip_count` | 0.000738079 s | 0.00295986 s | 64 | 4.01x | optix | count=1417 counts_match=True |
| `spatial_rayjoin` / `public_cdb_lsi_count` | 8.88379e-05 s | 0.642341 s | 8 | 7230.48x | optix | count=269 counts_match=True |
| `rt_dbscan` / `clustered3d_4096_core_flags_plus_numba_column_signature` | 0.0114709 s | 0.110916 s | 64 | 9.67x | optix | validated_vs_cpu_reference optix=True embree=True; native_threshold_ratio=14.99x |
| `barnes_hut` / `8192_body_prepared_node_coverage_threshold` | 0.00807277 s | 0.0222435 s | 8 | 2.76x | optix | matches_oracle optix=True embree=True |
| `rtnn` / `65536_fixed_radius_3d_ranked_summary_raw` | 0.00198331 s | 0.361476 s | 64 | 182.26x | optix | row_count=65536 same_contract=True |

## Evidence-Only Rows

- `spatial_rayjoin` / `public_cdb_overlay_seed`: optimized OptiX active-count contract and Embree generic overlay row contract are not the same output; generic Embree strict parity missed 3 requires_pip flags out of 239478 rows in diagnostic. OptiX active-count hot metric `0.000198145s`; Embree generic row count `239478`. Source: `docs/reports/goal4347_fair_rt_vs_embree_run/diagnostics/rayjoin_overlay_embree_mismatch_summary.json`.

## Methodology

- Use hot query/phase medians, not process wrapper elapsed, whenever apps expose a prepared-repeat metric.
- Run Embree at multiple thread settings where available and select the faster measured Embree row while retaining both artifacts.
- Use identical output contracts for ratios; mismatched contracts are evidence-only, not speedup ratios.
- Partner continuations are held constant where possible, e.g. RT-DBSCAN uses Numba continuation for both OptiX and Embree.

## Hardware Boundary

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.
- CPU: AMD EPYC 7702 with 128 logical CPUs visible. This is not an Intel CPU measurement.
- Embree: 4.3.0 native backend built on pod.
- Toolchain: CUDA 12.8/Numba env pins `ptxas` new enough for PTX 8.7, resolving the earlier spatial_rayjoin/rt_dbscan/barnes_hut failure.

## Interpretation

RT hardware is strongest when the benchmark can keep the comparison as a prepared traversal/count/ranked-summary query: LibRTS AABB, RTNN, triangle counting, RayJoin LSI, RayDB, robot collision, and RT-DBSCAN native threshold phase show large wins. Embree can still win on tiny host-friendly work, as contact_manifold does here. Barnes-Hut node coverage is a modest but real RT win. RayJoin overlay remains excluded from strict ratio until the overlay flag contract is made identical.

JSON packet: `docs\reports\goal4347_fair_rt_vs_embree_professional_comparison_2026-06-12.json`
