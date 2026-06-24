# Goal4348: Public-Grade RT Core vs Embree CPU Comparison Packet

Date: 2026-06-12

## Verdict

On an RTX 4000 Ada GPU versus Embree 4.3.0 on the pod's AMD EPYC 7702 CPU, RTDL's matched prepared query/count/traversal phases were faster with OptiX on every ratio-eligible benchmark contract in this packet. The measured OptiX-vs-best-Embree phase ratios range from 1.26x to 7230.48x. These are prepared phase results, not whole-application speedups.

This packet compares NVIDIA RT hardware through OptiX with Embree CPU traversal on the pod. It is not Intel GPU evidence, and this pod CPU is AMD EPYC running Intel Embree.

## Prepared Phase Table

| App / Contract | OptiX Metric | Best Embree Metric | Embree Threads | Embree / OptiX | Faster | Scope |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `barnes_hut` / `8192_body_prepared_node_coverage_threshold` | 0.008073 sec | 0.022244 sec | 8 | 2.76x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `contact_manifold` / `generic_aabb_broadphase_contact_candidates_2d_grid16384` | 0.123806 sec | 0.155611 sec | 64 | 1.26x | `optix` | prepared generic AABB broadphase query median; app exact refinement and contact interpretation are common host-side continuation |
| `hausdorff_xhd` / `directed_threshold_prepared_fixed_radius_count` | 0.003853 sec | 0.009748 sec | 8 | 2.53x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `librts_spatial_index` / `generic_prepared_aabb_index_query_2d` | 0.000624 sec | 0.062685 sec | 8 | 100.49x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `raydb_style` / `generated_grouped_count_same_rows_groups_boundary_limited_residency` | 0.00021 sec | 0.007873 sec | 64 | 37.52x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `robot_collision` / `prepared_triangle_scene_grouped_segment_any_hit_same_scene_query_scale` | 4.0496e-05 sec | 0.001181 sec | 8 | 29.17x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `rt_dbscan` / `clustered3d_4096_core_flags_plus_numba_column_signature` | 0.011471 sec | 0.110916 sec | 64 | 9.67x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `rtnn` / `65536_fixed_radius_3d_ranked_summary_raw` | 0.001983 sec | 0.361476 sec | 64 | 182.26x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `spatial_rayjoin` / `public_cdb_lsi_count` | 8.88379e-05 sec | 0.642341 sec | 8 | 7230.48x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `spatial_rayjoin` / `public_cdb_pip_count` | 0.000738 sec | 0.00296 sec | 64 | 4.01x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |
| `triangle_counting` / `rt_graph_2a1_generic_ray_triangle_any_hit` | 0.155335 ms | 12.108332 ms | 8 | 77.95x | `optix` | prepared query/count/traversal phase; not whole-app unless stated in note |

## Contact Manifold

The old reversed row was a 64-row `native_collect_k` micro-kernel over already-known Python oracle rows, so it is excluded from the main RT-hardware table. The replacement row uses generic prepared AABB broadphase rows on both OptiX and Embree, then the same host refinement/collect continuation.

| Grid | OptiX Broadphase Median | Best Embree Broadphase Median | Embree Threads | Embree / OptiX | Faster | OptiX Prepare | Best Embree Prepare |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 64 | 0.000615 s | 0.00061 s | 8 | 0.99x | `embree` | 0.267747 s | 0.023737 s |
| 512 | 0.002862 s | 0.003444 s | 64 | 1.20x | `optix` | 0.276269 s | 0.025378 s |
| 4096 | 0.023076 s | 0.028484 s | 64 | 1.23x | `optix` | 0.29931 s | 0.053095 s |
| 16384 | 0.123806 s | 0.155611 s | 64 | 1.26x | `optix` | 0.389522 s | 0.157733 s |

Long-repeat diagnostic for the excluded 64-row collector:

| Case | Median | p05 | p95 | Repeats | Scope |
| --- | ---: | ---: | ---: | ---: | --- |
| `optix` | 0.000208 s | 0.000199 s | 0.000287 s | 10000 | generic COLLECT_K_BOUNDED micro-kernel over already-known Python oracle rows; not an RT traversal comparison |
| `embree_t8` | 0.000209 s | 0.0002 s | 0.000287 s | 10000 | generic COLLECT_K_BOUNDED micro-kernel over already-known Python oracle rows; not an RT traversal comparison |
| `embree_t64` | 0.000203 s | 0.000199 s | 0.000308 s | 10000 | generic COLLECT_K_BOUNDED micro-kernel over already-known Python oracle rows; not an RT traversal comparison |

## Excluded Evidence

- `spatial_rayjoin` / `public_cdb_overlay_seed`: optimized OptiX active-count contract and Embree generic overlay row contract are not the same output; generic Embree strict parity missed 3 requires_pip flags out of 239478 rows in diagnostic
- `contact_manifold` / `native_collect_k_bounded_witness_rows`: excluded from the main RT table because it is a tiny generic collector over precomputed oracle rows, not a traversal/broadphase comparison.

## Fairness

Only matched output contracts are ratioed. The compared values are prepared query/count/traversal phase medians unless a row explicitly says otherwise. Partner continuations are held constant where used; RT-DBSCAN uses the same Numba continuation on both sides. Rows with mismatched output contracts remain evidence-only.

Optimization status:

- NVIDIA RT side: all current OptiX scale rows pass after CUDA 12.8/Numba toolchain pinning.
- Embree CPU side: Embree 4.3.0 built on the pod, native AABB count path used, native prepared AABB row output added for contact broadphase, Embree thread sweeps retained where measured.
- Intel GPU side: not measured and intentionally out of scope.
- CPU note: hardware here is AMD EPYC 7702 running Intel Embree, not an Intel CPU.

Validation status: `accept`.
