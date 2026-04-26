# Goal937 Ready RTX Claim-Review Packet

Date: 2026-04-25

## Verdict

Nine public apps or bounded app sub-paths are currently ready to enter NVIDIA
RTX claim review. This packet does not authorize public speedup claims. It
collects the current allowed claim, evidence source, and non-claim boundaries so
reviewers can decide what, if anything, is safe to say in v1.0 public docs.

## Rule Used

An app/sub-path is included only if the support matrix currently marks it
`ready_for_rtx_claim_review` and `rt_core_ready`.

That means:

- the app path uses OptiX traversal over an acceleration structure;
- artifact intake or preserved evidence exists;
- claim scope is bounded;
- non-claim language excludes whole-app overreach;
- final public wording still requires review.

## Claim-Review Candidates

| App | Bounded claim path | Evidence | Allowed claim to review | Non-claim boundary |
| --- | --- | --- | --- | --- |
| `robot_collision_screening` | prepared ray/triangle any-hit scalar pose-count | Goal765 / Goal793 / Goal795 / Goal929 | prepared OptiX ray/triangle any-hit pose-count traversal | not full robot planning, kinematics, CCD, or witness-row output |
| `outlier_detection` | prepared fixed-radius threshold-count summary | Goal765 / Goal793 / Goal795 / Goal929 | prepared OptiX fixed-radius threshold traversal for density/outlier summaries | not row-returning neighbors or whole anomaly-detection system speedup |
| `dbscan_clustering` | prepared fixed-radius core-threshold summary | Goal765 / Goal793 / Goal795 / Goal929 | prepared OptiX fixed-radius traversal for DBSCAN core-flag/core-count summary | not full DBSCAN clustering, cluster expansion, or Python graph traversal speedup |
| `service_coverage_gaps` | prepared gap-summary mode | Goal917 / Goal918 / Goal929 | prepared OptiX fixed-radius threshold traversal for compact coverage-gap summaries | not nearest-clinic row output, not whole service-coverage optimization |
| `event_hotspot_screening` | prepared count-summary mode | Goal917 / Goal919 / Goal929 | prepared OptiX fixed-radius count traversal for compact hotspot summaries | not neighbor-row output or whole hotspot analytics speedup |
| `facility_knn_assignment` | `coverage_threshold_prepared` | Goal887 / Goal920 / Goal929 | prepared OptiX fixed-radius threshold traversal for service-coverage decision | not ranked KNN assignment, fallback assignment, or facility-location optimization |
| `graph_analytics` | visibility edges plus native graph-ray candidate generation | Goal889 / Goal929 / Goal930 | OptiX ray/triangle any-hit for visibility-edge filtering plus native graph-ray candidate generation for BFS/triangle-count | not shortest path, graph DB, distributed graph analytics, or whole graph-system speedup |
| `polygon_pair_overlap_area_rows` | native-assisted candidate discovery | Goal877 / Goal929 / Goal930 | OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-pair overlap | not fully native polygon-area kernel and not full app speedup |
| `polygon_set_jaccard` | native-assisted candidate discovery at reviewed chunk contract | Goal877 / Goal929 / Goal930 | OptiX native-assisted LSI/PIP candidate discovery for bounded polygon-set Jaccard | not fully native Jaccard kernel; exact set-area/Jaccard refinement remains CPU/Python; larger chunk sizes remain held |

## Not Ready Yet

| App | Current hold | Reason |
| --- | --- | --- |
| `database_analytics` | `needs_interface_tuning` | Real OptiX DB candidate discovery/native counters exist, but same-semantics baseline review and interface/materialization dominance review remain required. |
| `road_hazard_screening` | `needs_native_kernel_tuning` | Native OptiX correctness passed, but tested native path was slower than CPU; Goal933 prepared profiler needs real RTX artifact. |
| `segment_polygon_hitcount` | `needs_native_kernel_tuning` | Native OptiX correctness passed, but tested native path was slower than host-indexed/CPU; Goal933 prepared profiler needs real RTX artifact. |
| `segment_polygon_anyhit_rows` | `needs_native_kernel_tuning` | Small native bounded gate passed, but Goal934 prepared scalable pair-row path still needs RTX artifact and overflow-free review. |
| `hausdorff_distance` | `needs_real_rtx_artifact` | Prepared threshold-decision path exists, but current artifacts are reduced/manual and need validated full artifact intake. |
| `ann_candidate_search` | `needs_real_rtx_artifact` | Prepared candidate-coverage path exists, but current artifacts are reduced/manual and need validated full artifact intake. |
| `barnes_hut_force_app` | `needs_real_rtx_artifact` | Prepared node-coverage decision path exists, but current artifacts are reduced/manual and need validated full artifact intake. |
| `apple_rt_demo` | out of NVIDIA target | Apple-specific, not NVIDIA RTX. |
| `hiprt_ray_triangle_hitcount` | out of NVIDIA target | HIPRT-specific, not NVIDIA OptiX/RTX. |

## Public Wording Guardrails

Allowed wording pattern:

```text
RTDL includes a bounded NVIDIA OptiX/RTX-backed sub-path for <app>: <claim path>.
The claim covers <native traversal/summary phase only>; <excluded work> remains
outside the claim.
```

Forbidden wording:

- "RTDL accelerates the whole app" unless the whole-app measurement and
  postprocess/interface costs are explicitly included and reviewed.
- "RTDL beats CPU/PostGIS/Embree" unless the exact same-semantics baseline,
  phase-clean artifact, and review packet authorize that comparison.
- "All graph/database/spatial work is RT-core accelerated" because several apps
  have bounded sub-path claims only.
- "Polygon area/Jaccard is fully native OptiX" because exact refinement remains
  CPU/Python.

## Next Work

1. Write public-facing wording for only these nine bounded paths.
2. Run a final review that checks README/front-page/tutorial examples use the
   bounded wording, not broad speedup language.
3. For held apps, wait for the next consolidated pod run using Goal936 rather
   than starting per-app pods.

## Boundary

This packet is a claim-review input, not a release authorization and not a
public benchmark claim.
