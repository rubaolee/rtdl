# Goal2567: Grouped-Reduction Substrate Contract

Date: 2026-05-23

## Scope

Goal2551 identified duplicated grouped-reduction semantics across the benchmark
apps and runtime layers. Goal2567 adds the first shared Python contract layer:

- `GroupedReductionSpec`
- `GroupedReductionCapacityStatus`
- `grouped_reduction_contract_metadata`
- `grouped_reduction_spec_from_columnar_plan`
- `columnar_plan_to_grouped_reduction_spec`

This does not migrate native call paths. It gives existing paths a common
operation/capacity/status vocabulary before deeper runtime consolidation.

## Contract

The supported operation tokens are:

- `group_any`
- `group_count`
- `group_sum_i64`
- `group_sum_f64`
- `group_min_i64`
- `group_max_i64`
- `group_sum_count_i64`
- `group_stats_i64`

The shared output mode is compact rows. The shared overflow policy is
fail-closed: when capacity is exceeded, exact consumers must not see partial
rows.

## Boundary

This is an internal substrate contract only. It does not authorize backend
support by itself, no public speedup claim is made, and app/domain semantics
remain outside native engines.

## Validation

Added `tests/goal2567_grouped_reduction_substrate_contract_test.py`, covering:

- public exports;
- spec validation;
- columnar aggregate to grouped-reduction mapping;
- fail-closed capacity status behavior;
- shared module app-vocabulary absence;
- this report.

No pod was used.
