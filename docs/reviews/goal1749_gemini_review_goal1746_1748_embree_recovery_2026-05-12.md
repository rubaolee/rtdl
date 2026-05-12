# Goal1749 Gemini Review: Goal1746-1748 Embree Recovery

## Verdict

accept-with-boundary: Direct inspection findings are preserved. The scratch log was ignored but corroborated by tracked reports.

## Review Summary

This review explicitly inspected the following files directly:
- `docs/reports/goal1746_v1_0_embree_baseline_adapter_run_2026-05-12.json`
- `docs/reports/goal1746_v1_0_ann_candidate_search_embree.json`
- `docs/reports/goal1747_v1_0_embree_baseline_recovery_consolidation_2026-05-12.md`
- `docs/reports/goal1748_v1_0_embree_schema_mapping_2026-05-12.json`
- `docs/reports/goal1748_v1_0_embree_schema_mapping_2026-05-12.md`

The file `scratch/goal1746_ann_rerank.log` was reported as ignored by the `.gitignore` or `.geminiignore` configuration, preventing direct inspection. However, relevant details were extracted from other provided artifacts.

## Goal1746 Embree Baseline Adapter Run Analysis

From `docs/reports/goal1746_v1_0_embree_baseline_adapter_run_2026-05-12.json`:
- `attempted`: 14
- `completed`: 14
- `skipped`: 0 (all attempted tasks were completed)

For `ann_candidate_search`, the `rerank_summary` command and elapsed time were derived from `docs/reports/goal1747_v1_0_embree_baseline_recovery_consolidation_2026-05-12.md` and `docs/reports/goal1746_v1_0_ann_candidate_search_embree.json`.
- `rerank_summary` command: `/usr/bin/python3 examples/rtdl_ann_candidate_app.py --backend embree --copies 20000 --output-mode rerank_summary`
- `elapsed seconds`: 37.262 seconds

## Goal1748 Embree Schema Mapping Analysis

From `docs/reports/goal1748_v1_0_embree_schema_mapping_2026-05-12.json`:
- `class_counts`:
    - `missing_current_artifact`: 3
    - `phase_mapped_diagnostic`: 4
    - `timing_schema_mismatch`: 7

## Tests and Scripts Inspection

The following related test and script files were identified and noted:
- `tests/goal1746_v1_0_embree_baseline_adapter_test.py`
- `tests/goal1747_v1_0_embree_baseline_recovery_consolidation_test.py`
- `tests/goal1748_v1_0_embree_schema_mapping_test.py`
- `scripts/goal1746_v1_0_embree_baseline_adapter.py`
- `scripts/goal1748_v1_0_embree_schema_mapper.py`

## Conclusion

The direct inspection confirms the recovery process of v1.0 Embree artifacts as reported. The classification of schema mapping indicates that while artifacts have been recovered, further work is required for direct timing comparisons and public performance claims, aligning with the `embree_schema_mapping_ready_without_public_speedup_claim` verdict from Goal1748. The `scratch/goal1746_ann_rerank.log` could not be directly inspected due to ignore patterns, but its critical information (command and elapsed time) was found in other artifacts. No "needs-more-evidence" is required as sufficient information was gathered for the review.