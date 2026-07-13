# Call For Review: Goal5071 Release Boundary Consolidation

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5071_rt_barneshut_aggregate_hierarchy_release_boundary_consolidation_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`
- `tests/goal5068_aggregate_hierarchy_descriptor_extension_test.py`
- `tests/goal5069_aggregate_frontier_reduce_execution_contract_test.py`
- `tests/goal5070_non_force_genericity_proof_test.py`

## Requested Verdict Labels

Use one:

- `approve_goal5071_release_boundary_consolidation`
- `approve_with_required_amendments`
- `block_goal5071_consolidation`

## Context

Goals5066-5070 converted the RT-BarnesHut hierarchy traversal discussion into generic RTDL contract surface:

- `AggregateHierarchy3D`
- traversal descriptors
- `SizeDistanceOpening`
- `LeafOnlyOpening`
- aggregate reducer vocabulary
- backend-neutral execution contract
- app-owned adapter
- non-force genericity proof

Goal5071 is not new implementation. It consolidates release boundary and next-step decision.

## Review Questions

1. Does the report accurately distinguish generic RTDL API additions from RT-BarnesHut app-owned pieces?
2. Does it correctly state that all aggregate frontier reduce backends are `not_implemented_contract_only`?
3. Does it avoid claiming paper completion, runtime execution, device residency, or performance?
4. Does it preserve the bounded same-input RT-BarnesHut status and broader prep+kernel performance caveat?
5. Is the public surface scan interpretation correct: core API app-name-free, public app docs allowed to mention Barnes-Hut?
6. Does the app-owned list correctly keep comparator, payload, prepared dump reader, and diagnostic CUDA extension outside RTDL core?
7. Does the non-force proof (`LeafOnlyOpening + aggregate_count`) sufficiently address the prior review demand for a substantially different reducer/opening?
8. Are the verification commands and results sufficient for this consolidation goal?
9. Is the recommendation correct: implement a CPU reference executor before a Numba prototype?
10. If CPU reference first is approved, should the next goal require both `SizeDistanceOpening + inverse_square_scalar_sum` and `LeafOnlyOpening + aggregate_count` to prevent app-shaped implementation?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
