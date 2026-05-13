# Goal1924 - All-App v2 Completion and Performance Analysis Plan

Status: execution-plan-not-complete

Date: 2026-05-13

## Purpose

The next v2.0 requirement is broader than the current pod packet:

1. every active public app row must have a v2 Python+partner+RTDL implementation
   or an explicit exclusion/control-row decision;
2. every implemented row must be comparable against the v1.8 Python+RTDL row
   with the same dataset and same output contract;
3. the final report must explain not only ratios, but why rows improve,
   regress, or stay neutral.

This document converts the post-Goal1923 state into an execution plan. It does
not claim that all apps are finished.

## Current Evidence

The accepted post-pod v2 packet covers three implementation families:

| Family | App rows covered now | Evidence |
| --- | --- | --- |
| fixed-radius partner count/threshold | `service_coverage_gaps`, `event_hotspot_screening` | `goal1903_fixed_radius_batch_pod.json`, Goal1921 analysis |
| segment/polygon count columns | `segment_polygon_hitcount` | `goal1903_segment_polygon_batch_pod_512.json`, `goal1903_segment_polygon_batch_pod_2048.json` |
| road-hazard priority flags | `road_hazard_screening` | `goal1889_road_hazard_prepared_reuse_pod_512.json`, `goal1889_road_hazard_prepared_reuse_pod_2048.json` |

Older v2 evidence also exists for:

| App row | Evidence state |
| --- | --- |
| `segment_polygon_anyhit_rows` | Goal1856/1853/1850 adapter and timing evidence exists, but it should be rerun in the final all-app batch so the artifact shape and hardware provenance match Goal1903/Goal1913. |

## Active App Rows

The active v1.8/v1.6.11 comparison surface has 16 rows, excluding frozen/demo
backends. Current v2 completion state:

| App | v2 family | Current v2 state | Next action |
| --- | --- | --- | --- |
| `database_analytics` | columnar payload / grouped reduction | missing | Build v2 partner columnar scan/grouped-reduction adapter, then compare against v1.8 DB prepared session. |
| `graph_analytics` | graph visibility/BFS/triangle RT subpaths | missing | Build partner-owned graph output columns for the RT-shaped subpaths or explicitly split into visibility/BFS/triangle rows. |
| `service_coverage_gaps` | fixed-radius threshold | implemented and pod-timed | Keep; include in final all-app batch and analysis. |
| `event_hotspot_screening` | fixed-radius threshold | implemented and pod-timed | Keep; include in final all-app batch and analysis. |
| `facility_knn_assignment` | fixed-radius coverage-threshold decision | missing | Reuse fixed-radius partner prepared scene for coverage-threshold decision; do not claim ranked KNN assignment unless separately implemented. |
| `road_hazard_screening` | segment/polygon count -> partner flags | implemented and pod-timed | Keep; include in final all-app batch and analysis. |
| `segment_polygon_hitcount` | segment/polygon count columns | implemented and pod-timed | Keep; include in final all-app batch and analysis. |
| `segment_polygon_anyhit_rows` | generic witness rows | implemented in earlier goals | Rerun in final all-app batch; decide whether row-output materialization is a v2 final app row or a primitive diagnostic row. |
| `polygon_pair_overlap_area_rows` | candidate discovery plus exact geometry continuation | missing | Use generic witness/candidate discovery for RT, then compute area continuation in partner tensor code or mark exact-area continuation as CPU/Python fallback. |
| `polygon_set_jaccard` | candidate discovery plus exact Jaccard | missing | Same as polygon overlap, but final metric needs partner tensor reduction or explicit fallback. |
| `hausdorff_distance` | fixed-radius threshold decision | missing | Reuse prepared fixed-radius partner threshold adapter for the directed threshold decision; exact distance ranking is out of scope unless separately implemented. |
| `ann_candidate_search` | fixed-radius candidate-coverage decision | missing | Reuse prepared fixed-radius partner threshold adapter; do not claim FAISS/HNSW/ANN index behavior. |
| `outlier_detection` | fixed-radius scalar threshold count | missing | Extend Goal1878-style fixed-radius partner adapter to output scalar threshold-count/outlier-count summaries. |
| `dbscan_clustering` | fixed-radius scalar core count | missing | Extend the fixed-radius scalar adapter; full cluster expansion remains Python/app logic unless partner tensor expansion is implemented. |
| `robot_collision_screening` | ray/triangle any-hit pose flags | missing | Lift the Goal1838 any-hit output-flag primitive to app-level pose flags with partner-owned output flags. |
| `barnes_hut_force_app` | fixed-radius node-coverage decision | missing | Reuse prepared fixed-radius partner threshold adapter for node coverage; force-vector evaluation remains Python/app logic unless separately implemented. |

## Implementation Families

The missing app work should be done by family, not app-by-app from scratch.

### Family A: Fixed-Radius Decision and Scalar Summary

Apps:

- `facility_knn_assignment`
- `hausdorff_distance`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `barnes_hut_force_app`

Reuse:

- `prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene`
- `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns`
- partner tensor threshold/reduction operations

Expected performance shape:

- likely strong on larger rows because Goal1921 fixed-radius evidence is strong;
- small rows may be overhead-bound;
- app postprocess may dominate if it remains Python-side.

### Family B: Ray/Triangle Any-Hit Flags

Apps:

- `robot_collision_screening`
- maybe diagnostic `segment_polygon_anyhit_rows`

Reuse:

- Goal1838/1848/1853 any-hit and witness-output contracts.

Expected performance shape:

- good when output is compact flags/counts;
- row-output paths can be slower if witness materialization is large or copied
  back to host.

### Family C: Segment/Polygon Count and Derived Flags

Apps:

- `segment_polygon_hitcount`
- `road_hazard_screening`

State:

- already implemented and pod-timed.

Expected performance shape:

- mixed at 512 rows;
- positive at 2048 rows with prepared reuse;
- partner-owned output columns are supported for exact measured rows.

### Family D: Polygon Exact-Metric Continuations

Apps:

- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Need:

- RT candidate discovery remains generic;
- exact geometry continuation must move to partner tensor code or remain an
  explicit fallback;
- final analysis must separate candidate discovery speed from whole-metric
  speed.

Expected performance shape:

- RT candidate discovery may be fast;
- exact area/Jaccard continuation can dominate and erase speedup if left in
  Python/CPU;
- these rows need the most careful claim boundaries.

### Family E: Columnar Database Analytics

Apps:

- `database_analytics`

Need:

- v2 partner-owned input/output column contract for columnar scan and grouped
  reduction;
- same-contract comparison against the v1.8 DB prepared session;
- strict boundary that this is not a DBMS-wide claim.

Expected performance shape:

- likely dominated by column packing, predicate selectivity, and reduction;
- may improve only after output/reduction stays partner-owned.

### Family F: Graph Analytics

Apps:

- `graph_analytics`

Need:

- split the app into public comparison rows: visibility edges, BFS expansion,
  and triangle-count candidate generation;
- decide which are true RTDL RT paths and which are graph postprocess;
- partner-owned output columns for candidate/flag/count results.

Expected performance shape:

- visibility/candidate rows may benefit;
- BFS/triangle-count whole-app rows may remain Python/postprocess dominated.

## Final All-App Harness Requirements

The all-app harness should produce one JSON file with:

- source commit;
- hardware;
- partner framework versions;
- app name;
- family;
- dataset size and seed;
- v1.8 baseline timing;
- v2 native partner timing;
- v2 prepared partner timing when applicable;
- parity/strict status;
- output ownership: partner-owned device output, host materialized, or fallback;
- claim flags;
- notes explaining performance behavior.

Long rows must print progress regularly.

## Analysis Rules

The final report should not be a simple speedup table. It must classify each row:

- `positive`: v2 beats v1.8 prepared under the same output contract.
- `mixed`: v2 beats one baseline or partner but not another.
- `neutral`: differences are small or overhead-bound.
- `negative`: v2 is slower than the relevant v1.8 prepared baseline.
- `not-comparable`: row uses fallback, different output contract, or missing
  partner implementation.

For each row, explain the likely cause:

- RT work large enough to amortize boundary overhead;
- partner-owned output avoids host materialization;
- prepared RT state reuse matters;
- exact app continuation still CPU/Python dominated;
- small-row dispatch/tensor setup overhead dominates;
- output cardinality explodes.

## Execution Order

1. Family A fixed-radius decision/scalar summaries.
2. Family B robot any-hit flags and segment-anyhit rerun.
3. Family D polygon exact-metric continuations.
4. Family E database columnar analytics.
5. Family F graph split rows.
6. Final all-app harness and RTX pod run.
7. Detailed all-app analysis report.
8. Claude + Gemini review for the total performance conclusion.

## Current Answer

No, all apps are not finished in v2.0 yet. The current v2 pod evidence is a
strong slice, not a full all-app matrix. The immediate engineering target is to
complete Family A first because it unlocks six missing app rows with the
already-proven fixed-radius partner contract.
