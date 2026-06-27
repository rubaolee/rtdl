# Goal4358 lx1 v2.11 Embree CPU Partner Reference

Date: 2026-06-12

Status: all 10 v2.11 Embree CPU benchmark-app reference rows passed on local Linux. This is CPU/Embree evidence only; it is not NVIDIA RT-core evidence and does not authorize public speedup wording.

## Machine And Artifact

| Field | Value |
| --- | --- |
| Host | `lx1` / `192.168.1.20` |
| RTDL commit | `02ed1169` |
| Artifact | `/home/lestat/work/goal4358_v211_embree_cpu/artifacts/rtdl_v2_11_embree_cpu_partner_reference_lx1_threads8.json` |
| Runner | `scripts/rtdl_v2_11_embree_cpu_partner_reference_runner.py` |
| Threads | `RTDL_EMBREE_THREADS=8` plus matching OMP/TBB/MKL/OPENBLAS/NUMEXPR limits |
| Runner version | `rtdl.v2_11.current_embree_cpu_partner_reference.goal4308.v1` |
| All pass | `true` |
| Numba partner rows | `0` |

The runner's claim boundary remains conservative: no release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, NVIDIA/AMD/Intel GPU performance wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, or app-specific native-engine logic is authorized by this packet.

## Results

| Row id | App | Route class | Status | Runner elapsed s |
| --- | --- | --- | --- | ---: |
| `hausdorff_xhd_embree_cpu_directed_summary` | `hausdorff_xhd` | `embree_cpu_rt_primitive` | pass | 0.455 |
| `spatial_rayjoin_pip_count_embree_cpu_generic_kernel` | `spatial_rayjoin` | `embree_cpu_rt_plus_python_continuation` | pass | 0.466 |
| `rt_dbscan_embree_cpu_prepared_rows` | `rt_dbscan` | `embree_cpu_rt_plus_python_continuation` | pass | 0.470 |
| `robot_collision_embree_cpu_prepared_buffers` | `robot_collision` | `embree_cpu_rt_primitive` | pass | 0.464 |
| `contact_manifold_embree_cpu_native_collect_k` | `contact_manifold` | `embree_cpu_rt_primitive` | pass | 0.440 |
| `raydb_style_embree_cpu_count_primitive_first` | `raydb_style` | `embree_cpu_rt_primitive` | pass | 0.497 |
| `barnes_hut_embree_cpu_node_coverage_prepared` | `barnes_hut` | `embree_cpu_rt_plus_python_continuation` | pass | 0.481 |
| `librts_spatial_index_embree_cpu_aabb_index` | `librts_spatial_index` | `embree_cpu_rt_primitive` | pass | 0.741 |
| `rtnn_embree_cpu_ann_candidate_quality_reference` | `rtnn` | `embree_cpu_rt_plus_python_continuation` | pass | 5.959 |
| `triangle_counting_embree_cpu_native_summary` | `triangle_counting` | `embree_cpu_rt_primitive` | pass | 0.488 |

## Readout

The CPU side is not blocked on Numba for this v2.11 reference packet: every selected row uses Embree and `requires_numba_rows` is empty. This gives us a clean CPU/Embree benchmark-app evidence packet to pair with the next RTX pod run, while keeping the hardware claim boundary explicit.
