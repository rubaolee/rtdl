# Goal1028 Claude Review

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-04-26
Source report: `docs/reports/goal1028_a5000_rtx_cloud_batch_report_2026-04-26.md`
Analyzer reports: `docs/reports/goal762_group_[a-h]_artifact_report.md`

---

## Verdict

**ACCEPT** — with four follow-up items noted below.

The report honestly summarizes the A5000 RTX cloud batch, accurately preserves all non-claim boundaries, correctly discloses the dependency repair event, and correctly identifies the missing baselines as a blocking condition before any public speedup claim. Goal1028 may be closed as evidence-collected, not claim-validated.

---

## Checks Passed

### 1. Honest status label
The top-level verdict is `evidence_collected_no_public_speedup_claim`. The report makes no assertion that RTX is faster than anything. This is the correct status given that no same-semantics baselines exist yet.

### 2. Hardware metadata present
GPU model, VRAM capacity, driver version, CUDA runtime, CUDA toolkit version, and OptiX header tag are all recorded. The commit SHA (`b70fe3f`) is also present. These are minimally required for later traceability.

### 3. Timings cross-check against analyzer reports — all match
Every median query time in the main App Evidence Table was verified against the corresponding Goal762 analyzer Artifact Table:

| Group | App / Path | Report time (s) | Analyzer time (s) | Match |
|---|---|---:|---:|---|
| A | robot_collision_screening / prepared_pose_flags | 0.000357 | 0.000357 | ✓ |
| B | outlier_detection / fixed_radius_density_summary | 0.000854 | 0.000854 | ✓ |
| B | dbscan_clustering / fixed_radius_core_flags | 0.000854 | 0.000854 | ✓ |
| C | database_analytics / sales_risk | 0.084712 | 0.084712 | ✓ |
| C | database_analytics / regional_dashboard | 0.118548 | 0.118548 | ✓ |
| D | service_coverage_gaps / gap_summary | 0.147815 | 0.147815 | ✓ |
| D | event_hotspot_screening / count_summary | 0.226937 | 0.226937 | ✓ |
| D | facility_knn_assignment / coverage_threshold | 0.000599 | 0.000599 | ✓ |
| E | road_hazard_screening / native_summary_gate | 0.134901 | 0.134901 | ✓ |
| E | segment_polygon_hitcount / native_experimental | 0.002926 | 0.002926 | ✓ |
| E | segment_polygon_anyhit_rows / bounded_gate | 0.004760 | 0.004760 | ✓ |
| F | graph_analytics / graph_visibility_edges_gate | 1.870180 | 1.870180 | ✓ |
| G | hausdorff_distance / directed_threshold | 0.004484 | 0.004484 | ✓ |
| G | ann_candidate_search / candidate_threshold | 0.000726 | 0.000726 | ✓ |
| G | barnes_hut_force_app / node_coverage | 0.001904 | 0.001904 | ✓ |
| H | polygon_pair_overlap_area_rows / optix_native | 4.250674 | 4.250674 | ✓ |
| H | polygon_set_jaccard / optix_native | 3.512444 | 3.512444 | ✓ |

All 17 entries match exactly. No inconsistency.

### 4. All group and analyzer statuses are ok
Every group summary shows `status: ok`, `failed_count: 0`. Every Goal762 analyzer report shows `status: ok`, `failure_count: 0`. Consistent throughout.

### 5. Non-claim boundaries preserved and accurate
Each app entry in the main report carries explicit claim-limit language. Spot-checked against the analyzer Non-claim and Baseline Review Contract columns — language is consistent and appropriately conservative. No analyzer report's claim limit is weaker than the corresponding main report entry.

### 6. GEOS dependency failure honestly disclosed
The report explicitly names the failed first run of Group F (missing `libgeos_c`), identifies it as a pod dependency failure rather than an OptiX traversal failure, and records that the passing rerun artifact replaced the failed one. The analyzer Group F report confirms `runner_status: ok`, `failure_count: 0`, consistent with the rerun having passed.

### 7. Missing-baseline gap correctly identified as a blocker
Next Actions item 2 explicitly requires same-semantics CPU/Embree/PostGIS baseline comparisons before any public speedup claim. The report does not pre-approve claims pending review; it defers to that step.

---

## Follow-Up Items (not blocking ACCEPT)

### F1. git_head not captured in cloud container
All eight Goal762 analyzer reports show `git_head: fatal: not a git repository`. The cloud pod did not have a git checkout; the commit SHA is recorded only in the main Goal1028 report. This is a traceability gap: if the main report were corrupted or replaced, there would be no independent record of which commit was running in the analyzers. **Recommendation:** include the commit SHA as an explicit field in the analyzer runner config so it can be injected at run time without requiring `git rev-parse`.

### F2. Group F and Group H build times not reported
- Group F (`graph_analytics`): `Input/prep pack` is blank in the analyzer; the main report correctly marks this as "not separately reported by analyzer."
- Group H (`polygon_pair_overlap_area_rows`, `polygon_set_jaccard`): `Input/prep pack` is 0.000000 in both cases. Zero prepare time is plausible only if the scene build is embedded in the query phase. If preparation genuinely happens at query time, the reported warm query median (4.25 s and 3.51 s respectively) already folds it in — but this should be confirmed, not assumed.

### F3. Large postprocess times for Group H not surfaced in main evidence table
The analyzer shows significant postprocess medians for Group H that the main App Evidence Table omits:
- `polygon_pair_overlap_area_rows`: 3.324128 s postprocess alongside 4.250674 s query
- `polygon_set_jaccard`: 5.403336 s postprocess alongside 3.512444 s query

When baselines are run, wall-time comparisons must include postprocess time or the comparison will be misleading. The main report should note this when constructing baseline contracts for these two apps.

### F4. Validation oracle absent for several groups
Groups C (database analytics), D partial (service_coverage_gaps, event_hotspot_screening), F (graph_analytics), and H (both polygon apps) show blank or zero validation/oracle times. The analyzers did not run independent CPU oracle checks for these paths in this batch. This is not a failure — oracle validation may be done separately — but it is a known evidence gap that should be tracked before a correctness claim is made for those subpaths.

---

## Summary

The Goal1028 report is accurate, internally consistent, and appropriately conservative. No inflated claims, no suppressed failure, no timing mismatch. The GEOS incident is properly disclosed. The four follow-up items are real gaps but none undermines the evidence-collection outcome. Goal1028 is closeable as `evidence_collected_no_public_speedup_claim`.
