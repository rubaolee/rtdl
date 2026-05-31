# Handoff: Goal2803 Barnes-Hut v2.5 Consolidated Harness Review

Please review Goal2803 as an independent external AI reviewer and write your review to:

`docs/reviews/goal2803_claude_review_barnes_hut_consolidated_harness_2026-05-31.md`

Scope:

- `scripts/goal2803_barnes_hut_v25_consolidated_harness.py`
- `tests/goal2803_barnes_hut_v25_consolidated_harness_test.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md`
- `docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness.json`

Review questions:

1. Does Goal2803 provide a real current consolidated harness for `barnes_hut`, not only historical report links?
2. Does it cover both the RT-assisted expanded-membership lowering and the partner grouped vector-sum continuation clearly?
3. Does the artifact preserve same-contract membership parity and record OptiX RT-core use for the generic membership subpath?
4. Does the vector-sum probe compare Torch and Triton honestly and keep Triton auto-selection blocked when appropriate?
5. Does the report avoid paper reproduction, authors-code comparison, public speedup, whole-app speedup, and native app-customization claims?
6. Is clean-from-Git validation correctly identified as pending if it has not yet been recorded?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. Please include any blocking issues first.
