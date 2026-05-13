# Goal1946 - All-App v1.8 vs v2.0 Performance Deep Dive

Status: codex-analysis-awaiting-external-review

Date: 2026-05-13

## Scope

Goal1946 expands the current Goal1931 all-app rollup into a reader-facing
performance analysis. It answers a narrower question than "is v2.0 released?":

For the 16 active public app rows, what does the current v1.8 versus v2.0
evidence actually say, and why do some rows speed up dramatically while others
must remain controls?

This report is based on already collected artifacts:

- `docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json`
- `docs/reports/goal1903_fixed_radius_batch_pod.json`
- `docs/reports/goal1937_fixed_radius_repeat3_pod/fixed_radius_524288_repeat3.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/segment_1048576_segment_anyhit_rows_1048576.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/robot_8388608x16384_robot_collision_8388608x16384.json`

It does not authorize v2.0 release, package-install support, whole-app speedup,
broad RT-core speedup, or arbitrary PyTorch/CuPy acceleration.

## Executive Summary

Current all-app classification:

| Class | Count | Meaning |
| --- | ---: | --- |
| `positive` | 11 | v2.0 partner path is faster on the same measured row contract. |
| `positive-subsecond` | 1 | v2.0 is much faster, but the v1.8 baseline is still under one second. |
| `control` | 4 | The row has useful evidence, but not a reviewed v2 partner speedup contract. |

For the 12 rows with a measured positive ratio, the geometric mean speedup is
about `288x`. This aggregate is descriptive only; it must not be turned into a
public "RTDL is 288x faster" claim because the rows are heterogeneous and four
active app rows are controls.

The core lesson is sharper:

- v2.0 wins dramatically when the app can be expressed as generic RTDL native
  primitive work plus a small partner tensor continuation over partner-owned
  device columns.
- v2.0 still helps on any-hit rows when the output stays compact and the app
  avoids host row materialization.
- v2.0 should not claim a speedup when the remaining application continuation
  is an exact database, graph, polygon-area, or set-union computation that is
  not yet a reviewed partner tensor contract.

## Full Row Table

`Speedup` is `v1.8 prepared seconds / v2 prepared partner seconds`. A larger
number is better for v2.0. `Ratio` is the inverse, matching Goal1931.

| App row | Class | Partner | Size | v1.8 prepared s | v2 partner s | Ratio | Speedup | Interpretation |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `database_analytics` | `control` | none | n/a | n/a | n/a | n/a | n/a | Current fast path is a native compact-summary continuation; no reviewed partner columnar scan/grouped-reduction continuation yet. |
| `graph_analytics` | `control` | none | n/a | n/a | n/a | n/a | n/a | Needs split rows: visibility is RT-shaped, but BFS and triangle count are graph algorithms outside the current partner speedup contract. |
| `service_coverage_gaps` | `positive` | CuPy | 16,384 | 0.038096 | 0.000228 | 0.005983 | 167.1x | Fixed-radius count-threshold row; partner-owned threshold columns avoid dense pair materialization. |
| `event_hotspot_screening` | `positive` | CuPy | 16,384 | 0.094140 | 0.000188 | 0.001998 | 500.6x | Same fixed-radius pattern, with larger v1.8 native work and tiny partner continuation. |
| `facility_knn_assignment` | `positive` | CuPy | 524,288 | 1.553787 | 0.000480 | 0.000309 | 3238.1x | This is radius-threshold assignment evidence, not a full ranked KNN implementation claim. |
| `road_hazard_screening` | `positive` | CuPy | 2,048 | 0.004491 | 0.001108 | 0.246651 | 4.1x | Positive but small; prepared reuse and compact outputs matter, while tiny rows expose fixed overhead. |
| `segment_polygon_hitcount` | `positive` | Torch | 2,048 | 0.002544 | 0.000878 | 0.345241 | 2.9x | Positive compact count row; not the exact polygon area/Jaccard continuation. |
| `segment_polygon_anyhit_rows` | `positive` | Torch | 1,048,576 | 7.121871 | 1.582755 | 0.222239 | 4.5x | Seconds-scale same-contract any-hit row with strict row-count parity. |
| `polygon_pair_overlap_area_rows` | `control` | none | n/a | n/a | n/a | n/a | n/a | Candidate discovery is RT-shaped, but exact area refinement is not yet a reviewed partner continuation. |
| `polygon_set_jaccard` | `control` | none | n/a | n/a | n/a | n/a | n/a | Exact set union/reduction dominates; no public v2 partner speedup claim yet. |
| `hausdorff_distance` | `positive` | Torch | 524,288 | 1.326599 | 0.000368 | 0.000277 | 3608.3x | Fixed-radius threshold surrogate, not a claim about all exact Hausdorff formulations. |
| `ann_candidate_search` | `positive` | Torch | 524,288 | 1.328173 | 0.000350 | 0.000263 | 3799.2x | Candidate coverage threshold is an ideal partner-output contract. |
| `outlier_detection` | `positive` | CuPy | 524,288 | 1.357974 | 0.000439 | 0.000323 | 3096.5x | Native fixed-radius counts plus partner scalar reduction. |
| `dbscan_clustering` | `positive` | Torch | 524,288 | 1.337720 | 0.000436 | 0.000326 | 3069.0x | Core-point count evidence only; not full DBSCAN cluster expansion. |
| `robot_collision_screening` | `positive-subsecond` | CuPy | 8,388,608 poses | 0.524696 | 0.009835 | 0.018745 | 53.3x | Exact pose-flag parity and true device-column handoff, but v1.8 is still subsecond. |
| `barnes_hut_force_app` | `positive` | CuPy | 524,288 | 1.373772 | 0.000418 | 0.000304 | 3289.5x | Node coverage threshold evidence, not a full N-body force integration claim. |

## Family Analysis

### Fixed-Radius Threshold Family

Rows:

- `service_coverage_gaps`
- `event_hotspot_screening`
- `facility_knn_assignment`
- `hausdorff_distance`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `barnes_hut_force_app`

This is the strongest current v2.0 family. The winning shape is:

1. RTDL/OptiX does generic fixed-radius hit/count work.
2. v2.0 writes the compact decision columns into partner-owned device memory.
3. Torch or CuPy performs a small threshold, scalar, or summary continuation.
4. The app avoids dense all-pairs materialization.

At 524,288 queries by 524,288 search points, v1.8 prepared OptiX rows are
seconds-scale, while v2 prepared partner continuations are sub-millisecond for
the measured threshold outputs. This is why these rows show thousand-fold
speedups. The speedup is real for this contract, but it is not evidence for
ranked KNN, full DBSCAN labeling, arbitrary Hausdorff algorithms, or every
possible fixed-radius post-processing program.

### Segment / Polygon Compact Output Family

Rows:

- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

This family is positive but less spectacular. The small 2,048-row hitcount and
road-hazard rows show `2.9x` to `4.1x` speedups, because fixed overheads are
large relative to the app work. The 1,048,576-row any-hit artifact is more
important for release interpretation: it is seconds-scale on v1.8 (`7.12s`) and
faster on v2.0 (`1.58s`), with strict row-count parity.

The lesson is that v2.0 pays off here when the result is a compact flag/count
column. It should not be presented as evidence that exact polygon overlay,
area, or Jaccard computations are accelerated end to end.

### Robot Collision Family

Row:

- `robot_collision_screening`

This is the strongest true device-handoff story in the current packet. The
robot adapter uses caller-supplied partner device ray columns and produces
partner GPU pose flags from native generic any-hit ray flags. The artifact
records direct device-pointer observation and exact pose-flag parity through
8,388,608 poses.

The ratio is strong (`53.3x`), but the v1.8 prepared baseline is still only
`0.525s`. Therefore this row supports "large exact-parity scaling signal" and
"selected true zero-copy/direct-pointer contract" wording, not a seconds-scale
whole-app claim.

### Control Families

Rows:

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

These rows are not failures of v2.0; they are places where the current
application continuation has not yet been moved into a reviewed partner tensor
contract. They are not v2 partner speedup rows.

`database_analytics` still relies on compact-summary native continuation
evidence. A real v2.0-positive database row would need a partner columnar scan
or grouped-reduction contract that is app-agnostic and externally reviewed.

`graph_analytics` is too broad as a single row. Visibility edges can be
RT-shaped, but BFS and triangle counting are graph algorithms. Future reporting
should split the app into separate rows rather than hiding mixed behavior under
one name.

`polygon_pair_overlap_area_rows` and `polygon_set_jaccard` currently prove
candidate discovery and exact-control behavior, not full partner acceleration.
The exact area refinement and set-union reduction must move to bounded partner
continuations before these rows can become v2 speedup evidence.

## What A Learner Should Take Away

v2.0 is not "write arbitrary Python and it becomes GPU-fast." The productive
mental model is:

```text
RTDL generic primitive -> partner-owned device columns -> Torch/CuPy tensor continuation
```

The more an app can fit that shape, the better v2.0 looks. The more an app
requires app-specific exact continuation logic that remains outside Torch/CuPy
or returns to the host, the more it becomes a control row rather than a speedup
row.

## Release Claim Boundary

Allowed technical summary, pending final consensus:

```text
Current v2.0 evidence shows strong speedups for selected OptiX RTDL primitive
contracts that hand compact outputs to Torch or CuPy device tensors. The
strongest rows are fixed-radius threshold workloads; segment any-hit and robot
collision also show positive measured results. Database, graph, and exact
polygon metrics remain control rows until their app continuations are expressed
as reviewed partner tensor contracts.
```

Still blocked:

- v2.0 release authorization;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- arbitrary PyTorch/CuPy acceleration claims;
- package-install claims;
- using control rows as speedup evidence.

## Next Work

Before a final v2.0 release packet, this report needs external review. The
review should check that the row classifications are fair, that the fixed-radius
speedups are not overgeneralized, that the control rows stay out of marketing
claims, and that the source-tree-only package policy remains a separate
consensus question.
