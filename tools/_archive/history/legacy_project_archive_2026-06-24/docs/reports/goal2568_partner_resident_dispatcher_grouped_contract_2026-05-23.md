# Goal2568: Partner-Resident Dispatcher Grouped Contract Bridge

Date: 2026-05-23

## Scope

Goal2567 added a shared grouped-reduction contract. Goal2568 wires that
contract into the existing OptiX partner-resident grouped i64 dispatcher
metadata without changing native call paths or public runtime behavior.

## Change

The partner-resident grouped i64 dispatcher now records:

- `grouped_reduction_contract` from `GroupedReductionSpec`
- `grouped_reduction_capacity_status` from `GroupedReductionCapacityStatus`

It keeps existing metadata keys such as `reduction`, `semantic_aggregate`,
`native_reduction_symbol`, `native_launch_count`, and claim-boundary flags for
compatibility with existing reports and tests.

## Boundary

This is a Python metadata bridge only. It does not add new native symbols, does
not change CUDA execution behavior, and does not authorize public speedup,
whole-app, SQL/DBMS, or true zero-copy claims.

## Validation

Added `tests/goal2568_partner_resident_dispatcher_grouped_contract_test.py`,
covering:

- `sum_count` dispatcher metadata maps to `group_sum_count_i64`;
- count metadata maps to `group_count` without a value field;
- grouped capacity status records compact-row success;
- legacy metadata keys remain present;
- this report.

No pod was used.
