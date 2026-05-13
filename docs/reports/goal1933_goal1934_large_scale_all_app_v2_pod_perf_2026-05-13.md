# Goal1933/1934 - Large-Scale All-App v2 Pod Performance Evidence

Status: large-scale-evidence-collected-release-still-blocked

Date: 2026-05-13

Hardware: `NVIDIA RTX A5000`, driver `570.195.03`

Source checkpoint: `f9d8d270`

## Purpose

Goal1932 proved the final all-app packet could run, but many rows were too short
for serious performance interpretation. Goal1933 and Goal1934 reran the
important rows at larger scale, using background pod jobs, visible progress
logs, and shell `timeout` wrappers so the session did not wait blindly.

## Fixed-Radius Family

Artifact: `docs/reports/goal1934_fixed_radius_huge_v2_pod/fixed_radius_524288.json`

Scale: `524288` query points by `524288` search points, one repeat per partner
because each v1.8 prepared row is now seconds-scale.

| App | Partner | v1.8 prepared OptiX s | v2 prepared partner s | v2 / v1.8 |
| --- | --- | ---: | ---: | ---: |
| `facility_knn_assignment` | CuPy | 1.873314 | 0.002160 | 0.001153x |
| `facility_knn_assignment` | Torch | 1.349197 | 0.001144 | 0.000848x |
| `hausdorff_distance` | CuPy | 1.143636 | 0.000856 | 0.000748x |
| `hausdorff_distance` | Torch | 1.384863 | 0.000694 | 0.000501x |
| `ann_candidate_search` | CuPy | 1.461004 | 0.000779 | 0.000533x |
| `ann_candidate_search` | Torch | 1.140788 | 0.000636 | 0.000557x |
| `outlier_detection` | CuPy | 1.376060 | 0.000674 | 0.000490x |
| `outlier_detection` | Torch | 1.393067 | 0.000817 | 0.000586x |
| `dbscan_clustering` | CuPy | 1.439040 | 0.000793 | 0.000551x |
| `dbscan_clustering` | Torch | 1.464116 | 0.000650 | 0.000444x |
| `barnes_hut_force_app` | CuPy | 1.429851 | 0.000679 | 0.000475x |
| `barnes_hut_force_app` | Torch | 1.411392 | 0.000626 | 0.000444x |

Interpretation:

- This is the strongest v2 result so far. The same prepared fixed-radius
  contract that already worked at small scale becomes seconds-scale on v1.8 and
  remains sub-millisecond to low-millisecond on the v2 prepared partner path.
- The app claims remain scoped: these rows are fixed-radius threshold/count
  decisions, not ranked KNN, exact Hausdorff ranking, full DBSCAN cluster
  expansion, or full Barnes-Hut force-vector evaluation.

## Robot Collision

Artifact: `docs/reports/goal1933_large_scale_v2_pod_batch/robot_collision_16384x1024.json`

Scale: `16384` poses, `1024` obstacles, `65536` rays, `2048` triangles.

| Partner | v1.8 prepared OptiX s | v2 prepared partner s | v2 / v1.8 | Exact pose flags |
| --- | ---: | ---: | ---: | --- |
| CuPy | 0.001052 | 0.000670 | 0.636548x | pass |
| Torch | 0.001005 | 0.000584 | 0.581517x | pass |

Interpretation:

- The adapter is correct and positive, but this scale is still sub-second.
- The win is from keeping native any-hit flags and pose reduction in partner
  device columns. It is not yet a seconds-scale whole-robot workload.

## Segment/Polygon Any-Hit Rows

Artifact: `docs/reports/goal1933_large_scale_v2_pod_batch/segment_anyhit_rows_4096.json`

Scale: `4096` segment/polygon pairs.

| Partner | v1.8 native OptiX rows s | v2 partner rows s | v2 / v1.8 |
| --- | ---: | ---: | ---: |
| CuPy | 0.014505 | 0.004269 | 0.294346x |
| Torch | 0.014505 | 0.006227 | 0.429287x |

Interpretation:

- The row-output path is positive, but still too short at `4096` for final
  performance claims.
- Compact count/flag rows remain the better v2 story than materialized row
  output.

## Polygon Exact-Metric Controls

Artifacts:

- `docs/reports/goal1933_large_scale_v2_pod_batch/control_polygon_pair_overlap_8192.json`
- `docs/reports/goal1933_large_scale_v2_pod_batch/control_polygon_jaccard_8192.json`

Scale: `8192` copies.

| App | Candidate discovery s | Exact continuation s | Parity |
| --- | ---: | ---: | --- |
| `polygon_pair_overlap_area_rows` | 1.881906 | 0.931633 | pass |
| `polygon_set_jaccard` | 1.589324 | 1.423977 | pass |

Interpretation:

- These are now meaningful seconds-scale control rows.
- They are not v2 partner acceleration rows. Exact geometry continuation still
  dominates enough that a future partner tensor continuation, not just RT
  candidate discovery, is needed for a clean v2 speedup claim.

## Database Control

Artifact: `docs/reports/goal1933_large_scale_v2_pod_batch/control_database_analytics_100000.json`

Scale: `100000` copies, compact-summary output.

| Metric | Seconds |
| --- | ---: |
| One-shot total | 8.597274 |
| Prepared-session prepare | 5.566840 |
| Prepared warm query median | 1.261744 |
| Reported all-section query time | 1.261577 |

Interpretation:

- The DB control row is now seconds-scale and phase-clean.
- It remains a bounded prepared compact-summary native continuation, not a v2
  partner columnar scan/grouped-reduction implementation.

## Graph Control

Artifact: `docs/reports/goal1933_large_scale_v2_pod_batch/control_graph_analytics_100000.json`

Scale: `100000` copies.

| Metric | Value |
| --- | ---: |
| Embree native query median | 13.353462 s |
| BFS discovered edges | 200000 |
| Triangle count | 100000 |
| Visibility blocked edges | 300000 |

Interpretation:

- The graph control row is seconds-scale and correct.
- It should remain split/control evidence, not a single v2 whole-graph speedup
  claim.

## What We Learned

- v2.0 has a genuinely strong performance story for prepared fixed-radius
  threshold/count apps. At large scale, the v2 prepared partner path is roughly
  `0.04%` to `0.12%` of the v1.8 prepared time in the measured rows.
- v2.0 is also positive for compact segment/polygon and robot flag reductions,
  but those need larger or more realistic scenarios before final broad language.
- Exact polygon metrics, database analytics, and graph analytics are now backed
  by seconds-scale evidence, but they are control/fallback rows unless their
  app continuations move into reviewed partner contracts.
- This packet improves the evidence quality, but it does not authorize v2.0
  release, whole-app speedup wording, arbitrary PyTorch/CuPy acceleration, or
  package-install claims.
