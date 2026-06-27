# Goal1747 v1.0 Embree Baseline Recovery Consolidation

## Verdict

`embree_baseline_recovered_with_schema_boundary`

Goal1746 recovered real v1.0 Embree app-level artifacts for all 14 candidate rows from the v1.0 Goal1030 local baseline command manifest. This proves the earlier Goal1660 Embree gap was a tester/profiler command-shape gap, not a missing v1.0 Embree implementation gap.

The recovered artifacts do not automatically become direct Goal1660 phase-profiler comparisons. Most v1.0 Embree app CLIs emit app-level JSON schemas, while the current Goal1660 Embree artifacts emit newer profiler schemas. Timing comparability therefore needs per-row schema mapping before any speedup or regression statement.

## Recovered Rows

Recovered v1.0 Embree artifacts:

- `service_coverage_gaps`
- `event_hotspot_screening`
- `facility_knn_assignment`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `graph_visibility_edges`
- `graph_bfs`
- `graph_triangle_count`
- `hausdorff_distance`
- `ann_candidate_search`
- `barnes_hut_force_app`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

No row is skipped in the final recovery summary.

The earlier `ann_candidate_search` delay is now explained and resolved. The first command used `--output-mode quality_summary`, which runs the Embree candidate-subset KNN slice and then performs Python exact quality evaluation against the full search set. At `--copies 20000`, that means 60,000 query points by 120,000 search points, or roughly 7.2 billion Python distance checks. That path is not the right v1.0 Embree baseline recovery surface for the current Goal1660 comparison.

The recovered row now uses `--output-mode rerank_summary`, which measures only the v1.0 Embree candidate-reranking slice exposed by the app CLI. It completed successfully on the Linux validation host in 37.262 seconds and wrote:

```text
docs/reports/goal1746_v1_0_ann_candidate_search_embree.json
```

## Execution Summary

Linux host:

```text
lx1 / 192.168.1.20
```

Baseline checkout:

```text
/home/lestat/work/rtdl_goal1746_v1_0
```

Current artifact collection checkout:

```text
/home/lestat/work/rtdl_goal1746_current
```

Run summary:

```text
attempted: 14
completed: 14
skipped_by_request: none
```

The run log was copied to:

```text
scratch/goal1746_linux_run.log
scratch/goal1746_ann_rerank.log
```

The structured run summary was copied to:

```text
docs/reports/goal1746_v1_0_embree_baseline_adapter_run_2026-05-12.json
```

## Important Finding

The v1.0 tag did have many real Embree app/native paths. The original Goal1660 comparison under-counted Embree because it tried to reuse newer/current profiler command shapes against v1.0 scripts that were often OptiX-specific or did not expose `--backend embree`.

Goal1746 used older real v1.0 app CLIs instead. That recovered the missing Embree baseline artifacts without fabricating OptiX-only profiler rows.

For `ann_candidate_search`, the important distinction is command surface rather than implementation presence. v1.0 has a real Embree app path, but `quality_summary` asks Python to compute exact quality over the full search set after the native candidate slice. The corrected `rerank_summary` path is the recoverable Embree app-level artifact.

## Timing Schema Boundary

Recovered v1.0 rows are not automatically equivalent to the current Goal1660 phase-profiler rows:

- Some v1.0 app CLIs emit app-level summaries with no timing fields.
- Some emit `run_phases.*` timing fields.
- Current Goal1660 artifacts often emit `scenario.timings_sec.*`, `timings_sec.*`, or `phases.*`.
- Graph v1.0 rows were split into `graph_visibility_edges`, `graph_bfs`, and `graph_triangle_count`, while current Goal1660 has a combined `graph_analytics/embree` artifact.

Therefore:

- `artifact_recovered` is true for 13 rows.
- `direct_speedup_claim_authorized` is false for all recovered rows.
- `phase_mapping_required` is true before direct timing comparison.

## Next Work

The next goal should build a schema mapper that classifies each recovered row as:

- `direct_phase_comparable`
- `app_level_timing_only`
- `correctness_or_summary_only`
- `long_running_or_timeout`

Only rows classified as `direct_phase_comparable` should feed any v1.0 customized Embree versus current generic Embree timing table.

## Boundary

This consolidation recovers v1.0 Embree artifacts and clarifies the evidence gap. It does not authorize public speedup wording, does not replace the existing Goal1723/1726 OptiX comparison, and does not authorize v1.8 release/tag action.
