# Goal2326 Contract-First Primitive Architecture Consensus

Date: 2026-05-18

Verdict: `accept-with-boundary`

## Decision

Goal2326 closes as an accepted contract-first architecture slice for RTDL's
public primitive and execution-report direction.

This is not a v2.0 release authorization and does not authorize public
performance, RT-core, whole-app speedup, or zero-copy claims.

## Consensus Inputs

| Source | Artifact | Verdict | Counted For Consensus |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal2326_contract_first_primitive_reconstruction_plan_2026-05-18.md` plus local implementation/tests | `accept-with-boundary` | yes |
| Claude | `docs/reviews/goal2326_claude_contract_first_primitive_architecture_review_2026-05-18.md` | `accept-with-boundary` | yes |
| Gemini | `docs/reviews/goal2326_gemini_contract_first_primitive_architecture_review_2026-05-18.md` | `accept-with-boundary` | yes |
| Gemini follow-up | `docs/reviews/goal2326_gemini_followup_post_fix_review_2026-05-18.md` | `accept-with-boundary` | supporting only |

The attempted Claude follow-up job hung with no stdout/stderr and is not counted
as an additional review. Gemini briefly created a Claude-named follow-up file;
that file was removed and is not counted.

## Accepted Scope

The accepted Goal2326 slice includes:

- `rtdsl.ExecutionPolicy`, `rtdsl.ExecutionReport`, `rtdsl.ExecutionResult`, and
  `rtdsl.run(...)` as the explainable execution substrate.
- `rtdsl.primitives` and selected top-level aliases as the contract-first public
  primitive facade.
- `rtdsl.adapters.*` modules grouped by generic contract families rather than
  app/domain families.
- Guard tests that block app-shaped public primitive names, app-shaped adapter
  module/export names, invisible execution decisions, and app-shaped core facade
  usage in v2 examples.
- A curated `dir(rtdsl)` learner surface that shows the generic v2 contract
  surface first while preserving historical compatibility attributes.

## Post-Review Fixes

Claude's blocker-grade item was resolved before closure:

- `rtdsl.adapters.prepared_handles` no longer re-exports
  `allocate_robot_collision_pose_partner_device_output_columns`.
- `tests.goal2326_adapter_partition_test` now scans adapter `__all__` symbols
  for app/domain fragments, including `robot` and `pose`.
- `ExecutionReport.memory_status` and `ExecutionReport.copy_status` now use the
  explicit sentinel `not_reported_by_runtime`.
- `tests.goal2326_execution_report_contract_test` covers that sentinel.
- `rtdsl.__dir__()` now presents the contract-first learner surface.
- `tests.goal2326_public_primitive_contract_test` verifies the curated
  `dir(rtdsl)` surface is generic.

## Remaining Boundaries

Goal2326 deliberately does not remove every historical compatibility export from
`rtdsl.__all__`. That cleanup remains a future deprecation slice because a
flag-day removal could break existing examples, tests, and user scripts.

The execution planner remains conservative: `backend="auto"` is explainable but
does not yet perform a full capability probe. Runtime memory and copy status are
reported as not supplied by the runtime layer, and all claim-boundary flags stay
false unless separately measured and reviewed.

## Validation

Windows local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2326_public_primitive_contract_test tests.goal2326_execution_report_contract_test tests.goal2326_adapter_partition_test tests.goal2326_examples_recipe_boundary_test tests.goal2324_examples_v2_0_directory_reorganization_test tests.goal1765_github_learner_readiness_double_check_test
$env:PYTHONPATH='src;.'; py -3 -m compileall -q src\rtdsl examples\v2_0 tests\goal2326_public_primitive_contract_test.py tests\goal2326_execution_report_contract_test.py tests\goal2326_adapter_partition_test.py tests\goal2326_examples_recipe_boundary_test.py
```

Result: `20` focused tests pass; compileall passes.
