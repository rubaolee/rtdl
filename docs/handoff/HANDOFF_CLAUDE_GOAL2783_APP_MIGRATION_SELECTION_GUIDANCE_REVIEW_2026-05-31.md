# Handoff - Goal2783 App Migration Selection Guidance Review

Please perform an independent read-only review of Goal2783 and write the result
to:

`docs/reviews/goal2783_claude_review_app_migration_selection_guidance_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/v2_5_triton_app_migration.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `docs/reports/goal2783_v2_5_app_migration_selection_guidance_2026-05-31.md`
- `docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md`
- `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`

## Review Questions

1. Does Goal2783 correctly wire Goal2782's measured negative guidance into the
   v2.5 app migration plan?
2. Do the RTNN and Barnes-Hut rows point to the right operations, workload
   shapes, and evidence goals?
3. Does the planner remain advisory only and block preview-partner auto-select?
4. Does this keep the native RTDL/OptiX traversal boundary intact?
5. Are the tests and report sufficient for this metadata/planner step?

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
