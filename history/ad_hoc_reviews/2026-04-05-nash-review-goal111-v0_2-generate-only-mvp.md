# Nash Review: Goal 111 v0.2 Generate-Only MVP

Date: 2026-04-05
Reviewer: Nash
Verdict: APPROVE-WITH-NOTES

## Findings

- The revised proposal is now strong enough to proceed as a bounded product test. [goal_111_v0_2_generate_only_mvp.md](/Users/rl2025/rtdl_python_only/docs/goal_111_v0_2_generate_only_mvp.md) no longer permits a `cpu_python_reference`-only toy and now requires an explicit structured input contract, a normal executable `cpu` target, a dataset/output-linked verification path, and one concrete user scenario where generation beats examples/templates.
- The redundancy problem is reduced but not eliminated. [goal111_v0_2_generate_only_mvp_plan_2026-04-05.md](/Users/rl2025/rtdl_python_only/docs/reports/goal111_v0_2_generate_only_mvp_plan_2026-04-05.md) now frames the product-value test correctly: if the output is just the existing example with light substitutions, the MVP should be paused. That is the right bar. The remaining risk is that the eventual implementation still fails that bar in practice.
- Reusing `segment_polygon_hitcount` is acceptable for an MVP seed family, but only because the revised docs now treat that choice as a controlled test fixture rather than as proof of a broad generate-only mode. This is still strategically narrow and should stay narrow.
- One weakness remains in the product contract: “desired emitted fields or output mode” is specified, but the plan still does not say how much variation the generator must support before it counts as generation rather than parameterized template filling. That is no longer a blocker at the proposal stage, but it is the main place the implementation could still collapse into a thin wrapper.
- The revised goal is now kill-disciplined in the right way. The explicit kill criteria around hardcoded example selection, weak verification, and failure to beat examples/templates make the proposal honest enough to test without pretending it has already earned a permanent place in v0.2.
