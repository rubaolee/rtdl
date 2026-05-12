# Gemini Handoff: Review Goal1746-Goal1748 Embree v1.0 Baseline Recovery

Please perform a read-only independent review of the Goal1746-Goal1748 Embree v1.0 baseline recovery and schema-mapping work.

## Context

The user objected to skipping the long-running `ann_candidate_search` v1.0 Embree row. The skip has now been removed.

Current artifacts of interest:

- `scripts/goal1746_v1_0_embree_baseline_adapter.py`
- `tests/goal1746_v1_0_embree_baseline_adapter_test.py`
- `docs/reports/goal1746_v1_0_ann_candidate_search_embree.json`
- `docs/reports/goal1746_v1_0_embree_baseline_adapter_run_2026-05-12.json`
- `docs/reports/goal1747_v1_0_embree_baseline_recovery_consolidation_2026-05-12.md`
- `tests/goal1747_v1_0_embree_baseline_recovery_consolidation_test.py`
- `scripts/goal1748_v1_0_embree_schema_mapper.py`
- `docs/reports/goal1748_v1_0_embree_schema_mapping_2026-05-12.md`
- `docs/reports/goal1748_v1_0_embree_schema_mapping_2026-05-12.json`
- `tests/goal1748_v1_0_embree_schema_mapping_test.py`
- `scratch/goal1746_ann_rerank.log`

## Specific Questions

1. Confirm that `ann_candidate_search` is no longer skipped: the run summary should show `attempted: 14`, `completed: 14`, and no `skipped_by_request` rows.
2. Confirm that the reason for the earlier long run is accurately stated: `quality_summary` at `--copies 20000` performs exact Python quality evaluation over 60,000 queries by 120,000 search points, roughly 7.2 billion distance checks.
3. Confirm that the corrected `rerank_summary` v1.0 Embree row is a legitimate app-level baseline recovery surface, and that it completed successfully in the copied Linux log.
4. Audit Goal1748’s classifications:
   - 4 `phase_mapped_diagnostic`
   - 7 `timing_schema_mismatch`
   - 3 `missing_current_artifact`
5. Check that Goal1748 does not overclaim public speedup, release readiness, or exact same-contract performance comparison.

## Required Output

Write a review to:

`docs/reviews/goal1749_gemini_review_goal1746_1748_embree_recovery_2026-05-12.md`

Use one of the established verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict is `accept-with-boundary` if the recovery is valid but diagnostic ratios remain non-public and non-release evidence.
