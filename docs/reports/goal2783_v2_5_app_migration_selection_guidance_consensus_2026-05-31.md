# Goal2783 Consensus - v2.5 App Migration Selection Guidance

Date: 2026-05-31

## Verdict

`accept`

Goal2783 is accepted as a narrow planner-metadata hardening step. It wires the
Goal2782 measured negative guidance into the v2.5 benchmark-app migration plan
so dense top-k and dense vector-sum rows cannot be treated as automatic Triton
performance selections merely because preview kernels exist.

## Evidence

Codex implementation and validation:

- updated `src/rtdsl/v2_5_triton_app_migration.py`
- added per-app `partner_selection_guidance`
- added per-app `measured_negative_preview_guidance_count`
- added plan-level `partner_selection_guidance_integrated: True`
- added plan-level and per-app `auto_select_preview_partner_allowed: False`
- RTNN now records Goal2780 guidance for `grouped_topk_f64` /
  `dense_exact_topk_candidate_ranking`
- Barnes-Hut now records Goal2781 guidance for `grouped_vector_sum_f64x2` /
  `dense_grouped_vector_sum_2d`

Local Windows validation:

```text
tests.goal2783_v2_5_app_migration_selection_guidance_test
tests.goal2782_v2_5_partner_selection_guidance_test
tests.goal2676_v2_5_triton_partner_pivot_test
tests.goal2681_v2_5_triton_partner_adapter_front_door_test
tests.goal2723_v2_5_tiered_benchmark_manifest_test

Ran 33 tests in 0.048s
OK (skipped=3)
```

Independent Claude review:

- `docs/reviews/goal2783_claude_review_app_migration_selection_guidance_2026-05-31.md`
- verdict: `accept`
- confirms Goal2783 structurally wires Goal2782 guidance into the app migration
  planner, RTNN and Barnes-Hut point to the correct operations/workload shapes
  and evidence goals, advisory-only behavior blocks preview-partner auto-select,
  and the RTDL/OptiX traversal boundary remains intact

Claude noted two non-blocking naming observations:

- the tiered benchmark manifest uses conceptual `grouped_vector_sum` while the
  app migration plan uses concrete `grouped_vector_sum_f64x2`
- the RTNN manifest uses conceptual `bounded_topk_or_ranked_summary` while the
  app migration plan now uses concrete `grouped_topk_f64`

These are accepted as non-blocking because the app migration plan is the
contract-bearing structure for Goal2783; manifest tightening can be handled in
a later cleanup if the manifest validator begins enforcing operation names.

## Boundary

This consensus does not authorize:

- public speedup claims
- RT-core speedup claims
- true zero-copy wording
- whole-app speedup claims
- v2.5 release readiness
- replacing RTDL/OptiX traversal with partner code
- auto-selecting Triton from preview availability alone

Partner choice remains explicit and evidence-bound.
