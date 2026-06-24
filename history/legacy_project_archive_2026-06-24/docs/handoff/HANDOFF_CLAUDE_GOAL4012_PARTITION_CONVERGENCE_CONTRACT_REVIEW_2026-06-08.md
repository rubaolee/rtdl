# Handoff: Goal4012 Partition-Convergence Contract Review

Please perform a read-only independent review of Goal4012.

## Context

Goal4012 is the contract hardening step after:

- Goal4007 root-read telemetry;
- Goal4009 root path-halving rejection;
- Goal4011 partition-factor sweep.

The purpose is to update the fixed-radius graph component front-door candidate
so the next native/device-resident primitive cannot drift into a dense
cell-pair matrix or hidden root mutation.

## Files To Inspect

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal4012_partition_convergence_contract_after_factor_sweep_2026-06-08.md`
- `tests/goal4012_partition_convergence_contract_after_factor_sweep_test.py`
- `docs/research/future_version_to_do_list.md`
- Prior evidence reports:
  - `docs/reports/goal4007_grouped_union_root_read_telemetry_2026-06-08.md`
  - `docs/reports/goal4009_root_path_halving_candidate_rejection_2026-06-08.md`
  - `docs/reports/goal4011_grouped_union_partition_factor_sweep_2026-06-08.md`

## Questions

1. Does Goal4012 correctly incorporate the Goal4007/4009/4011 evidence into the
   `partition_convergence_hybrid` candidate contract?
2. Does it clearly reject dense all-cell-pair matrices and hidden root path
   halving while preserving the accepted grouped-stream runtime route?
3. Does it keep all claim boundaries fail-closed: no release, public speedup,
   broad RT-core, whole-app, true-zero-copy, hidden-dispatch, automatic-partner,
   or app-specific-engine claim?
4. Are the exposed metadata fields discoverable and app-agnostic enough for the
   next native implementation slice?

## Validation To Run

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal4012_partition_convergence_contract_after_factor_sweep_test `
  tests.goal4005_partition_convergence_candidate_front_door_contract_test `
  tests.goal4011_grouped_union_partition_factor_sweep_test `
  tests.goal4009_root_path_halving_candidate_rejection_test `
  tests.goal4007_grouped_union_root_read_telemetry_test
```

## Output

Write the review to:

`docs/reviews/goal4013_claude_review_goal4012_partition_convergence_contract_2026-06-08.md`

Use one of the project verdict values: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Please lead with findings by severity and be explicit if Goal4012 overclaims
runtime readiness or performance.
