# Goal1410 v1.5 vs v1.0 RTX Pod Performance Results

Date: 2026-05-06

This report records same-command, same-scale v1.5 candidate vs v1.0 application
performance measurements on the RTX pod provided by the user. It complements
the local Linux GTX 1070 evidence with RTX-class OptiX hardware evidence.

The measurements remain app/backend/subpath evidence. They do not authorize
unqualified whole-app speedup wording.

## Environment

- SSH endpoint used: `root@213.173.108.108 -p 21035`
- SSH key used: `~/.ssh/id_ed25519_rtdl_codex`
- Hostname: `ac96d0647e50`
- OS: Ubuntu Linux, kernel `6.8.0-110-generic`
- GPU: NVIDIA RTX PRO 4500 Blackwell, 32623 MiB
- NVIDIA driver: `580.126.20`
- CUDA compiler: `nvcc` release `13.0`, build `V13.0.88`
- Embree package: `libembree-dev 4.3.0+dfsg-2`
- GEOS package: `libgeos-dev 3.12.1-3build1`
- NVRTC package: `cuda-nvrtc-dev-13-0 13.0.88-1`
- OptiX SDK headers: `/root/optix-dev`
- Clean benchmark clone: `/root/rtdl_goal1408_perf`
- v1.5 candidate commit: `9cf1fdda71043ec992d232ccf0305e502d9e1ad8`
- v1.0 release commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- Scale: `copies=512`, `iterations=3`

OptiX setup note: the first OptiX build omitted GEOS linkage because
`pkg-config` was missing, producing `GEOSPreparedGeom_destroy_r` load errors.
The final artifact uses a rebuilt `build/librtdl_optix.so` linked against
`libgeos_c`, `libcuda`, and `libnvrtc`.

## Artifact Index

- RTX pod Embree artifact:
  `docs/reports/goal1408_v1_5_vs_v1_0_perf_rtx_pod_embree/`
- RTX pod OptiX artifact:
  `docs/reports/goal1408_v1_5_vs_v1_0_perf_rtx_pod_optix_fixed/`

## Embree Results

| App | v1.0 sec | v1.5 sec | v1.0/v1.5 | Status |
| --- | ---: | ---: | ---: | --- |
| `database_analytics` | 0.001099 | 0.001149 | 0.956x | roughly equal |
| `service_coverage_gaps` | 0.013891 | 0.014300 | 0.971x | roughly equal |
| `event_hotspot_screening` | 0.019873 | 0.019986 | 0.994x | roughly equal |
| `facility_knn_assignment` | 0.044091 | 0.044597 | 0.989x | roughly equal |
| `road_hazard_screening` | 0.006733 | 0.010865 | 0.620x | v1.5 slower |
| `segment_polygon_hitcount` | 0.018680 | 0.018843 | 0.991x | roughly equal |
| `polygon_pair_overlap_area_rows` | 0.080925 | 0.085677 | 0.945x | v1.5 slower |
| `hausdorff_distance` | 0.025291 | 0.025492 | 0.992x | roughly equal |
| `ann_candidate_search` | 0.951182 | 0.949120 | 1.002x | roughly equal |
| `outlier_detection` | 0.014001 | 0.013547 | 1.034x | roughly equal |
| `dbscan_clustering` | 0.013796 | 0.013915 | 0.991x | roughly equal |
| `robot_collision_screening` | 0.318840 | 0.323507 | 0.986x | roughly equal |
| `barnes_hut_force_app` | 0.091615 | 0.091168 | 1.005x | roughly equal |

Embree interpretation: v1.5 is broadly performance-neutral against v1.0 on the
RTX pod CPU path. `road_hazard_screening` and `polygon_pair_overlap_area_rows`
are slower at this scale; the remaining measured Embree rows are roughly equal.

## OptiX Results

| App | v1.0 sec | v1.5 sec | v1.0/v1.5 | Status |
| --- | ---: | ---: | ---: | --- |
| `database_analytics` | 0.001760 | 0.001843 | 0.955x | roughly equal |
| `graph_analytics` | 0.461245 | 0.405026 | 1.139x | v1.5 faster |
| `facility_knn_assignment` | 0.000077 | 0.000078 | 0.982x | roughly equal |
| `road_hazard_screening` | 0.010508 | 0.006612 | 1.589x | v1.5 faster |
| `segment_polygon_hitcount` | 0.028254 | 0.027528 | 1.026x | roughly equal |
| `polygon_pair_overlap_area_rows` | 0.878978 | 0.735516 | 1.195x | v1.5 faster |
| `hausdorff_distance` | 0.000140 | 0.000139 | 1.004x | roughly equal |
| `ann_candidate_search` | 0.000078 | 0.000078 | 0.998x | roughly equal |
| `robot_collision_screening` | 0.000101 | 0.000092 | 1.089x | v1.5 faster |
| `barnes_hut_force_app` | 0.000076 | 0.000074 | 1.031x | roughly equal |

OptiX interpretation: v1.5 shows positive RTX pod movement for
`graph_analytics`, `road_hazard_screening`, `polygon_pair_overlap_area_rows`,
and `robot_collision_screening` under the measured compact/prepared subpaths.
The remaining measured OptiX rows are roughly equal.

## v1.5 Embree vs OptiX On RTX Pod

The Embree run used `RTDL_EMBREE_THREADS=auto`, which recorded 112 effective
CPU threads in the raw artifact. The table below compares v1.5 Embree against
v1.5 OptiX on the same pod for rows where both backends have measured profiles.

| App | Embree sec | OptiX sec | Faster backend |
| --- | ---: | ---: | --- |
| `database_analytics` | 0.001149 | 0.001843 | Embree 1.6x |
| `facility_knn_assignment` | 0.044597 | 0.000078 | OptiX 571.8x |
| `road_hazard_screening` | 0.010865 | 0.006612 | OptiX 1.6x |
| `segment_polygon_hitcount` | 0.018843 | 0.027528 | Embree 1.5x |
| `polygon_pair_overlap_area_rows` | 0.085677 | 0.735516 | Embree 8.6x |
| `hausdorff_distance` | 0.025492 | 0.000139 | OptiX 183.4x |
| `ann_candidate_search` | 0.949120 | 0.000078 | OptiX 12168.2x |
| `robot_collision_screening` | 0.323507 | 0.000092 | OptiX 3516.4x |
| `barnes_hut_force_app` | 0.091168 | 0.000074 | OptiX 1232.0x |

Interpretation: both backends use ray-tracing-style execution, but Embree runs
directly in CPU memory while OptiX crosses the CPU/GPU boundary. The Embree
wins are therefore consistent with small, compact, or CPU-refinement-heavy
profiles where avoiding GPU upload/download, CUDA launch latency,
synchronization, and marshaling outweighs GPU RT traversal throughput. This is
especially visible for `polygon_pair_overlap_area_rows`, whose measured profile
includes candidate discovery plus CPU/Python exact-area refinement. Conversely,
the prepared decision-style OptiX profiles show that GPU RT dominates once the
work is compact enough and large enough to amortize fixed GPU overhead.

## Excluded Apps

These apps are intentionally excluded from v1.5 same-contract comparison:

- `apple_rt_demo`: Apple RT is outside the active v1.5 Embree+OptiX scope.
- `hiprt_ray_triangle_hitcount`: HIPRT is outside the active v1.5 Embree+OptiX
  scope.
- `polygon_set_jaccard`: depends on `COLLECT_K_BOUNDED`, deferred to v1.5.1.
- `segment_polygon_anyhit_rows`: depends on `COLLECT_K_BOUNDED`, deferred to
  v1.5.1.

## Release Interpretation

The RTX pod evidence supports a bounded release statement:

- v1.5 preserves approximately comparable Embree performance for most included
  app profiles at the measured scale.
- v1.5 improves several OptiX RTX pod subpaths versus v1.0, most clearly
  `road_hazard_screening` (`1.589x`), `polygon_pair_overlap_area_rows`
  (`1.195x`), and `graph_analytics` (`1.139x`).
- Several OptiX measurements are extremely small sub-millisecond prepared
  queries; those should not be used as headline speedup claims.
- Public wording must stay subpath-specific and should cite this artifact plus
  external review before release-facing speedup claims are made.
