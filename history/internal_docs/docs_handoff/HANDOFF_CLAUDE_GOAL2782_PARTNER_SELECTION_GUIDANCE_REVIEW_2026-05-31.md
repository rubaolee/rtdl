# Handoff - Goal2782 Partner-Selection Guidance Review

Please perform an independent read-only review of Goal2782 and write the result
to:

`docs/reviews/goal2782_claude_review_partner_selection_guidance_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/__init__.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md`
- `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md`
- `docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md`
- `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`

## Review Questions

1. Does Goal2782 correctly encode the Goal2780/Goal2781 lesson that preview
   kernel availability is not partner-selection authorization?
2. Are the top-k and vector-sum slower-ratio ranges faithful to the artifacts?
3. Does the guidance remain advisory only, preserving explicit app/user partner
   choice and no forced partner?
4. Are public speedup, RT-core, true-zero-copy, whole-app, and release claims
   all blocked?
5. Does the validator fail closed enough for this narrow metadata/planner step?
6. Is it correct that no new pod timing is required for this goal?

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
