# Goal1662 v1.6.11 Dual-GPU Performance Release Report - 2026-05-10

## Verdict

The `v1.6.11` release-prep performance evidence is strong enough to prepare a release with narrow, app-specific performance wording.

Do not claim that `v1.6.11` is broadly faster than `v1.0`. Do not claim universal GPU acceleration. Do not count unsupported rows as wins or losses.

The defensible performance story is:

- `v1.6.11` exposes real app-generic Embree and OptiX backend surfaces for many public app workloads.
- On two independent NVIDIA pods, long RT-heavy workloads show repeatable OptiX wins over Embree on the same current app-level command surface.
- Short workloads or workloads dominated by Python orchestration, packing, launch overhead, exact continuation, or summary logic are not universal OptiX wins.

## Evidence Package

| Artifact | Path |
| --- | --- |
| RTX 4090 raw JSON | `docs/reports/goal1661_comprehensive_backend_pod_results_2026-05-10.json` |
| RTX 4090 generated summary | `docs/reports/goal1661_comprehensive_backend_pod_summary_2026-05-10.md` |
| RTX 4090 interpretation | `docs/reports/goal1661_comprehensive_backend_pod_interpretation_2026-05-10.md` |
| RTX 4090 full log archive | `docs/reports/goal1661_comprehensive_backend_pod_results_2026-05-10.tgz` |
| RTX 3090 raw JSON | `docs/reports/goal1661_comprehensive_backend_pod_results_3090_2026-05-10.json` |
| RTX 3090 generated summary | `docs/reports/goal1661_comprehensive_backend_pod_summary_3090_2026-05-10.md` |
| RTX 3090 interpretation | `docs/reports/goal1661_comprehensive_backend_pod_interpretation_3090_2026-05-10.md` |
| RTX 3090 full log archive | `docs/reports/goal1661_comprehensive_backend_pod_results_3090_2026-05-10.tgz` |
| 4090 3-AI consensus | `docs/reviews/goal1661_comprehensive_backend_pod_3ai_consensus_2026-05-10.md` |

## Method

Both pods ran the same comprehensive executor:

```bash
python3 scripts/goal1661_comprehensive_backend_pod_executor.py \
  --install-system-deps \
  --workdir <pod-workdir> \
  --optix-prefix /opt/optix \
  --row-timeout 2400 \
  --build-timeout 1200
```

The executor uses two clean checkouts:

- Current candidate: `main`, treated as `v1.6.11`.
- Baseline: `v1.0` tag.

It builds and measures:

- `embree_1t`: Embree with `RTDL_EMBREE_THREADS=1`.
- `embree_auto`: Embree with `RTDL_EMBREE_THREADS=auto`.
- `optix`: NVIDIA OptiX backend.

Rows that do not have a real backend selector, stable historical command surface, or independent app timing semantics are marked unsupported rather than counted as performance results.

## Environments

| GPU | Driver | CUDA reported by nvidia-smi | Current commit | Baseline commit | OK | Failed | Unsupported |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| RTX 4090 | 550.127.05 | 12.4 | `e9f3cbb73180b40e87e212bdfe09ebfee0ce085f` | `b9c9620af78a2fab92083d43af312bb6310e452a` | 58 | 0 | 37 |
| RTX 3090 | 580.159.03 | 13.0 | `9b54159fb07cdcdc0d99ac89aff3484a0bbf61b2` | `b9c9620af78a2fab92083d43af312bb6310e452a` | 58 | 0 | 37 |

The 3090 current commit includes evidence/report files added after the 4090 run. It does not contain runtime implementation changes relative to the 4090 measured code path.

## Current v1.6.11 Backend Results

These tables compare OptiX against Embree auto on the same current app-level command surface.

### RTX 4090

| App | Embree auto sec | OptiX sec | OptiX/Embree speedup |
| --- | ---: | ---: | ---: |
| `polygon_set_jaccard` | 318.889 | 5.178 | 61.590 |
| `robot_collision_screening` | 8.190 | 1.385 | 5.913 |
| `polygon_pair_overlap_area_rows` | 12.996 | 3.786 | 3.432 |
| `hausdorff_distance` | 5.362 | 1.681 | 3.189 |
| `barnes_hut_force_app` | 7.999 | 3.645 | 2.195 |
| `facility_knn_assignment` | 3.085 | 1.682 | 1.834 |
| `ann_candidate_search` | 3.041 | 1.808 | 1.681 |
| `database_analytics` | 2.288 | 2.689 | 0.851 |
| `road_hazard_screening` | 2.326 | 3.206 | 0.725 |
| `service_coverage_gaps` | 1.064 | 1.586 | 0.671 |
| `event_hotspot_screening` | 1.034 | 1.670 | 0.619 |
| `segment_polygon_hitcount` | 0.851 | 1.425 | 0.597 |
| `segment_polygon_anyhit_rows` | 0.884 | 1.484 | 0.596 |

### RTX 3090

| App | Embree auto sec | OptiX sec | OptiX/Embree speedup |
| --- | ---: | ---: | ---: |
| `polygon_set_jaccard` | 399.070 | 6.760 | 59.031 |
| `robot_collision_screening` | 9.068 | 1.857 | 4.883 |
| `hausdorff_distance` | 7.266 | 2.161 | 3.362 |
| `barnes_hut_force_app` | 9.574 | 4.818 | 1.987 |
| `ann_candidate_search` | 4.297 | 2.233 | 1.924 |
| `polygon_pair_overlap_area_rows` | 10.708 | 5.656 | 1.893 |
| `facility_knn_assignment` | 3.675 | 2.018 | 1.821 |
| `event_hotspot_screening` | 1.548 | 2.024 | 0.765 |
| `road_hazard_screening` | 3.113 | 4.098 | 0.760 |
| `database_analytics` | 2.713 | 3.664 | 0.740 |
| `service_coverage_gaps` | 1.533 | 2.144 | 0.715 |
| `segment_polygon_anyhit_rows` | 0.937 | 2.229 | 0.420 |
| `segment_polygon_hitcount` | 0.829 | 2.097 | 0.396 |

## Cross-GPU Reproducibility

For current `v1.6.11` OptiX rows, the 4090 is consistently faster than the 3090, but not by an order of magnitude. The average 3090/4090 OptiX time ratio across accepted rows is about `1.32x`.

| App | 3090 OptiX sec | 4090 OptiX sec | 3090/4090 time ratio |
| --- | ---: | ---: | ---: |
| `segment_polygon_anyhit_rows` | 2.229 | 1.484 | 1.502 |
| `polygon_pair_overlap_area_rows` | 5.656 | 3.786 | 1.494 |
| `segment_polygon_hitcount` | 2.097 | 1.425 | 1.472 |
| `database_analytics` | 3.664 | 2.689 | 1.363 |
| `service_coverage_gaps` | 2.144 | 1.586 | 1.352 |
| `robot_collision_screening` | 1.857 | 1.385 | 1.341 |
| `barnes_hut_force_app` | 4.818 | 3.645 | 1.322 |
| `polygon_set_jaccard` | 6.760 | 5.178 | 1.306 |
| `hausdorff_distance` | 2.161 | 1.681 | 1.285 |
| `road_hazard_screening` | 4.098 | 3.206 | 1.278 |
| `outlier_detection` | 3.366 | 2.722 | 1.237 |
| `ann_candidate_search` | 2.233 | 1.808 | 1.235 |
| `event_hotspot_screening` | 2.024 | 1.670 | 1.211 |
| `graph_analytics` | 7.643 | 6.316 | 1.210 |
| `facility_knn_assignment` | 2.018 | 1.682 | 1.200 |

The repeated 3090 and 4090 pattern supports the qualitative release claim that OptiX acceleration is real for selected long RT-heavy workloads.

## Cross-Version Findings

The accepted `v1.0` versus `v1.6.11` rows are mixed and mostly close. They do not support broad wording such as "`v1.6.11` is faster than `v1.0`".

### RTX 4090 Cross-Version Rows

| App | Mode | v1.0 sec | v1.6.11 sec | v1.6.11/v1.0 speedup |
| --- | --- | ---: | ---: | ---: |
| `event_hotspot_screening` | `optix` | 1.779 | 1.670 | 1.065 |
| `facility_knn_assignment` | `optix` | 1.790 | 1.682 | 1.064 |
| `database_analytics` | `embree_1t` | 2.174 | 2.044 | 1.064 |
| `outlier_detection` | `optix` | 2.868 | 2.722 | 1.054 |
| `polygon_set_jaccard` | `optix` | 5.433 | 5.178 | 1.049 |
| `polygon_pair_overlap_area_rows` | `optix` | 3.887 | 3.786 | 1.027 |
| `graph_analytics` | `optix` | 6.409 | 6.316 | 1.015 |
| `road_hazard_screening` | `optix` | 3.170 | 3.206 | 0.989 |
| `barnes_hut_force_app` | `optix` | 3.506 | 3.645 | 0.962 |
| `hausdorff_distance` | `optix` | 1.590 | 1.681 | 0.946 |
| `database_analytics` | `optix` | 2.516 | 2.689 | 0.935 |
| `segment_polygon_hitcount` | `optix` | 1.289 | 1.425 | 0.905 |
| `robot_collision_screening` | `optix` | 1.240 | 1.385 | 0.895 |
| `database_analytics` | `embree_auto` | 2.037 | 2.288 | 0.890 |
| `service_coverage_gaps` | `optix` | 1.383 | 1.586 | 0.872 |
| `ann_candidate_search` | `optix` | 1.568 | 1.808 | 0.867 |
| `segment_polygon_anyhit_rows` | `optix` | 1.272 | 1.484 | 0.857 |

### RTX 3090 Cross-Version Rows

| App | Mode | v1.0 sec | v1.6.11 sec | v1.6.11/v1.0 speedup |
| --- | --- | ---: | ---: | ---: |
| `graph_analytics` | `optix` | 8.097 | 7.643 | 1.059 |
| `facility_knn_assignment` | `optix` | 2.135 | 2.018 | 1.058 |
| `outlier_detection` | `optix` | 3.518 | 3.366 | 1.045 |
| `barnes_hut_force_app` | `optix` | 4.731 | 4.818 | 0.982 |
| `event_hotspot_screening` | `optix` | 1.952 | 2.024 | 0.965 |
| `database_analytics` | `embree_1t` | 2.599 | 2.712 | 0.958 |
| `hausdorff_distance` | `optix` | 2.042 | 2.161 | 0.945 |
| `database_analytics` | `optix` | 3.441 | 3.664 | 0.939 |
| `polygon_set_jaccard` | `optix` | 6.287 | 6.760 | 0.930 |
| `polygon_pair_overlap_area_rows` | `optix` | 5.246 | 5.656 | 0.927 |
| `database_analytics` | `embree_auto` | 2.430 | 2.713 | 0.896 |
| `road_hazard_screening` | `optix` | 3.602 | 4.098 | 0.879 |
| `ann_candidate_search` | `optix` | 1.943 | 2.233 | 0.870 |
| `service_coverage_gaps` | `optix` | 1.847 | 2.144 | 0.862 |
| `robot_collision_screening` | `optix` | 1.550 | 1.857 | 0.835 |
| `segment_polygon_anyhit_rows` | `optix` | 1.796 | 2.229 | 0.806 |
| `segment_polygon_hitcount` | `optix` | 1.478 | 2.097 | 0.705 |

## Unsupported Rows

Each pod reported `37` unsupported rows. Unsupported means not comparable, not failed.

Primary reasons:

- `v1.0` app profilers often did not expose stable Embree backend selectors.
- Some historical commands lacked a real engine selector, so forcing an engine label would be decorative rather than measured.
- Some app entries were intentionally outside the v1.6.11 Embree/OptiX pod command set.
- DBSCAN shares the Goal757 fixed-radius primitive row with outlier detection and is not independent timing.

## Release Wording Guidance

Acceptable wording:

- "On RTX 4090 and RTX 3090 pods, selected long RT-heavy `v1.6.11` workloads show repeatable OptiX speedups over Embree on the same app-level command surface."
- "`polygon_set_jaccard` measured about `61.6x` on RTX 4090 and `59.0x` on RTX 3090 versus Embree auto in this pod configuration."
- "`robot_collision_screening` measured about `5.9x` on RTX 4090 and `4.9x` on RTX 3090 versus Embree auto in this pod configuration."

Avoid:

- "`v1.6.11` is faster than `v1.0`."
- "RTDL accelerates all apps on GPU."
- "OptiX is always faster than Embree."
- "Unsupported rows failed."
- "These numbers are DBMS-wide, GIS-wide, or whole-application guarantees."

## Release Preparation Recommendation

Proceed with release preparation if the release notes preserve the boundaries above. The performance section should cite exact artifacts and exact workloads, and should explicitly say that short workloads are often dominated by orchestration or launch overhead.

Before publishing, the final release checklist should confirm:

- Public docs link to the exact performance evidence files.
- Release wording uses only accepted rows.
- Unsupported rows remain documented.
- No release note implies broad `v1.6.11` over `v1.0` speedup.
- No release note implies universal GPU acceleration.
