# Goal2782 Consensus - v2.5 Partner-Selection Guidance

Date: 2026-05-31

## Verdict

`accept`

Goal2782 is accepted as a narrow metadata/planner hardening step. It makes the
Goal2780 and Goal2781 performance lesson machine-readable: a Triton preview
kernel being available does not authorize automatic partner selection.

Goal2784 later refreshed the dense top-k row with improved, still-negative
evidence: the direct dense point top-k adapter removed dense score
materialization and reduced the measured RTX A5000 slowdown to 4.91x-10.04x
slower than Torch, so the advisory "do not auto-select Triton" decision remains.

Goal2786 later refreshed the dense vector-sum row with still-negative evidence:
the batched presegmented row-offset candidate was slower than the single-group
offset path, and the best Triton offset path remained 3.76x-16.86x slower than
Torch, so the advisory "do not auto-select Triton" decision remains.

Goal2787 later added a dense exact Hausdorff-style witness row with
still-negative evidence: the generic Triton grouped-argmin plus grouped-argmax
route is correct but 31.88x-45.15x slower than Torch on measured RTX A5000
shapes, so the advisory "do not auto-select Triton" decision applies to that
shape too.

Goal2788 later added a dense point-nearest Hausdorff-style row with
still-negative evidence: the fused dense point-nearest strategy removes dense
score-row materialization and improves on Goal2787, but remains 3.77x-30.73x
slower than Torch on measured RTX A5000 shapes, so the advisory "do not
auto-select Triton" decision remains.

## Evidence

Codex implementation and validation:

- added `src/rtdsl/v2_5_partner_selection_guidance.py`
- added `v2_5_partner_selection_guidance()`
- added `validate_v2_5_partner_selection_guidance(...)`
- added `plan_v2_5_partner_selection(...)`
- encoded measured negative guidance for:
  - `grouped_topk_f64` / dense exact top-k candidate ranking
  - `grouped_vector_sum_f64x2` / dense grouped 2D vector sum, refreshed by
    Goal2786
  - `grouped_argmin_f64` / dense exact Hausdorff-style argmin/argmax, added by
    Goal2787
  - `grouped_argmin_f64` / dense exact Hausdorff-style nearest then global max
    via dense-point-nearest adapter, added by Goal2788
- kept planner guidance advisory-only with no forced partner
- kept public speedup, RT-core, true-zero-copy, whole-app, and release claims
  blocked
- converted RT-core and whole-app claim blocks into explicit guidance fields
  after Claude flagged that those two were previously blocked only implicitly

Local Windows validation:

```text
tests.goal2782_v2_5_partner_selection_guidance_test
tests.goal2696_v2_5_partner_support_matrix_test
tests.goal2780_topk_adapter_triton_grouped_topk_test
tests.goal2781_grouped_vector_sum_adapter_test

Ran 18 tests in 0.046s
OK (skipped=2)

v2.5 preview slice through Goal2782
Ran 123 tests in 0.093s
OK (skipped=10)
```

Pod no-new-timing validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01

targeted Goal2782 slice
Ran 18 tests in 2.566s
OK

v2.5 preview slice through Goal2782
Ran 123 tests in 2.527s
OK
```

Independent Gemini review:

- `docs/reviews/goal2782_gemini_review_partner_selection_guidance_2026-05-31.md`
- verdict: `accept`
- confirms preview availability is distinct from partner selection, the
  Goal2780/Goal2781 ratio ranges are faithful to artifacts, claims remain
  blocked, and no new pod timing is needed for this metadata-consuming goal

Independent Claude review:

- `docs/reviews/goal2782_claude_review_partner_selection_guidance_2026-05-31.md`
- verdict: `accept`
- confirms the lesson is structurally encoded, ratio ranges are faithful to the
  pod artifacts, advisory-only behavior is enforced across construction,
  validation, and planning, and no new pod timing is needed
- noted that RT-core and whole-app claim blocks should be named fields rather
  than implicit consequences of `promoted_performance_path: False`; Codex
  applied that hardening before accepting the goal

## Boundary

This consensus does not authorize:

- public speedup claims
- RT-core speedup claims
- true zero-copy wording
- whole-app speedup claims
- v2.5 release readiness
- forced partner selection

The guidance is advisory only. Apps and benchmark harnesses must still choose
partners explicitly and keep same-contract evidence attached to any performance
claim.
