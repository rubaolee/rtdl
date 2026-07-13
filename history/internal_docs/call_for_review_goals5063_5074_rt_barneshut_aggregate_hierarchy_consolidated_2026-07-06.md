# Consolidated Call For Review: Goals5063-5074 RT-BarnesHut / Aggregate Hierarchy Re-architecture

Date: 2026-07-06

Please review the full RT-BarnesHut / aggregate hierarchy re-architecture line from Goal5063 through Goal5074 as one connected packet.

## Requested Overall Verdict Labels

Use one:

- `approve_goals5063_5074_rt_barneshut_aggregate_hierarchy_rearchitecture`
- `approve_with_required_amendments`
- `block_goals5063_5074_rearchitecture`

## Review Scope

This review should evaluate whether the work correctly moves RT-BarnesHut from an app-shaped diagnostic route toward a generic RTDL aggregate hierarchy language surface, while preserving the principle:

```text
RTDL is a generic system/language. RT-BarnesHut is an app on top of it.
```

The reviewer should judge:

- whether the RTDL core additions are generic;
- whether app-owned paper/comparator/prepared-array logic remains outside core;
- whether the new CPU reference executor and optional Numba executor are correctly scoped;
- whether the RT-BarnesHut app integration uses public RTDL APIs rather than private diagnostic kernels;
- whether correctness, claim boundaries, and release wording are honest.

## Files To Review

### Goal5063 - RT-BarnesHut Paper Reproduction Scaffold

- `history/internal_docs/call_for_review_goal5063_rt_barneshut_paper_reproduction_scaffold_2026-07-06.md`
- `history/internal_docs/goal5063_rt_barneshut_paper_reproduction_requirements_and_plan_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

### Goal5065 - Hierarchy Traversal API Design

- `history/internal_docs/call_for_review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`
- `history/internal_docs/goal5065_rt_barneshut_hierarchy_traversal_api_design_and_plan_2026-07-06.md`
- `history/internal_docs/goal5065_review_amendment_response_2026-07-06.md`
- `history/internal_docs/review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`

### Goal5066 - Generic Aggregate Hierarchy Contract Schema

- `history/internal_docs/call_for_review_goal5066_aggregate_hierarchy_contract_schema_2026-07-06.md`
- `history/internal_docs/goal5066_aggregate_hierarchy_contract_schema_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`

### Goal5067 - RT-BarnesHut App Adapter

- `history/internal_docs/call_for_review_goal5067_rt_barneshut_aggregate_hierarchy_adapter_2026-07-06.md`
- `history/internal_docs/goal5067_rt_barneshut_aggregate_hierarchy_adapter_result_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

### Goal5068 - Generic Descriptor Columns

- `history/internal_docs/call_for_review_goal5068_aggregate_hierarchy_descriptor_extension_2026-07-06.md`
- `history/internal_docs/goal5068_aggregate_hierarchy_descriptor_extension_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `tests/goal5068_aggregate_hierarchy_descriptor_extension_test.py`

### Goal5069 - Backend-Neutral Execution Contract

- `history/internal_docs/call_for_review_goal5069_aggregate_frontier_reduce_execution_contract_2026-07-06.md`
- `history/internal_docs/goal5069_aggregate_frontier_reduce_execution_contract_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `tests/goal5069_aggregate_frontier_reduce_execution_contract_test.py`

### Goal5070 - Non-Force Genericity Proof

- `history/internal_docs/call_for_review_goal5070_non_force_genericity_proof_2026-07-06.md`
- `history/internal_docs/goal5070_non_force_genericity_proof_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `tests/goal5070_non_force_genericity_proof_test.py`

### Goal5071 - Release Boundary Consolidation

- `history/internal_docs/call_for_review_goal5071_release_boundary_consolidation_2026-07-06.md`
- `history/internal_docs/goal5071_rt_barneshut_aggregate_hierarchy_release_boundary_consolidation_2026-07-06.md`

### Goal5072 - CPU Reference Executor

- `history/internal_docs/call_for_review_goal5072_aggregate_frontier_reduce_cpu_reference_executor_2026-07-06.md`
- `history/internal_docs/goal5072_aggregate_frontier_reduce_cpu_reference_executor_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5072_aggregate_frontier_reduce_cpu_reference_test.py`

### Goal5073 - Optional Numba CPU Parity Prototype

- `history/internal_docs/call_for_review_goal5073_aggregate_frontier_reduce_numba_parity_prototype_2026-07-06.md`
- `history/internal_docs/goal5073_aggregate_frontier_reduce_numba_parity_prototype_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5073_aggregate_frontier_reduce_numba_parity_test.py`

### Goal5074 - RT-BarnesHut App Integration Through Public Generic APIs

- `history/internal_docs/call_for_review_goal5074_rt_barneshut_app_generic_numba_parity_integration_2026-07-06.md`
- `history/internal_docs/goal5074_rt_barneshut_app_generic_numba_parity_integration_result_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

## Important Context

Goal5064 is a current-implementation/status report and does not have a separate call-for-review file.

The sequence intentionally proceeds in layers:

1. paper app scaffold and current implementation audit;
2. generic RTDL hierarchy contract;
3. app-owned adapter from RT-BarnesHut prepared arrays into generic schema;
4. generic descriptor promotion;
5. backend-neutral execution contract;
6. non-force genericity proof;
7. release-boundary consolidation;
8. CPU reference executor;
9. optional CPU Numba parity prototype;
10. RT-BarnesHut app integration through public generic APIs.

## Cross-Cutting Review Questions

Please answer these in addition to any per-goal findings.

1. Does the whole sequence preserve the principle that RTDL is a generic system/language and RT-BarnesHut is only an app?
2. Are the core RTDL additions generic enough: `AggregateHierarchy3D`, descriptor columns, opening policies, reducer vocabulary, execution contract, CPU reference executor, and optional Numba executor?
3. Does `src/rtdsl/aggregate_hierarchy.py` remain free of RT-BarnesHut app identity, author payload logic, Torch extension logic, native OptiX symbols, or paper comparator code?
4. Is the app-owned adapter boundary correct: prepared-array reader, paper comparator, force-output interpretation, and author-specific assets remain under `Paper-reproduction-apps/rt-barneshut-paper/`?
5. Does `LeafOnlyOpening + aggregate_count` sufficiently prove that the generic contract is not merely an inverse-square force-field wrapper?
6. Is the CPU reference executor a sound correctness oracle for future Numba/CUDA/OptiX executors?
7. Is the optional Numba executor correctly classified as `optional_numba_cpu_reference_prototype`, not CUDA/native/backend complete?
8. Does Goal5074 prove the RT-BarnesHut app can use public generic RTDL APIs, without claiming author-comparator completion or performance?
9. Are the tests sufficient for this re-architecture line, including app-level parity and core no-leak checks?
10. Are all performance, paper-reproduction, and author-parity claims properly bounded?
11. What required amendments, if any, must be completed before continuing to the next goal?
12. Should the next goal be a bounded force-output bridge from generic aggregate rows, or should another genericity/regression gate run first?

## Known Verification Evidence

The latest combined regression after Goal5074:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test tests.goal5073_aggregate_frontier_reduce_numba_parity_test
```

Result:

```text
Ran 62 tests in 11.648s
OK (skipped=1)
```

Manual Goal5074 CLI smoke:

```text
mode: aggregate_numba_parity
generic_public_rtdl_api_used: true
candidate_backend: numba
candidate_backend_status: optional_numba_cpu_reference_prototype
source_count: 32
mismatch_count: 0
max_abs_delta: 0.0
max_rel_delta: 0.0
paper_reproduction_complete: false
same_input_author_comparator: false
```

Core leak scan:

```text
src/rtdsl/aggregate_hierarchy.py
pattern: BarnesHut|Treelogy|RTBH|author-optix-payload|load_inline|import torch|rtdl_optix|rayjoin|RayJoin
result: 0 matches
```

Adapter native/backend leak scan:

```text
Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py
pattern: import torch|load_inline|ctypes|rtdl_optix
result: 0 matches
```

## Expected Review Output

Please provide:

- overall verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 12 cross-cutting review questions;
- short per-goal verdicts for Goals5063, 5065, 5066, 5067, 5068, 5069, 5070, 5071, 5072, 5073, and 5074.
