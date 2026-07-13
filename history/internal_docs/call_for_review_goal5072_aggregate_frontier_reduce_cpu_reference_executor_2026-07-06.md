# Call For Review: Goal5072 Aggregate Frontier Reduce CPU Reference Executor

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5072_aggregate_frontier_reduce_cpu_reference_executor_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`
- `tests/goal5069_aggregate_frontier_reduce_execution_contract_test.py`
- `tests/goal5072_aggregate_frontier_reduce_cpu_reference_test.py`

## Requested Verdict Labels

Use one:

- `approve_goal5072_cpu_reference_executor`
- `approve_with_required_amendments`
- `block_goal5072_cpu_reference_executor`

## Context

Goal5066-5071 created and consolidated a generic RTDL aggregate hierarchy contract line for RT-BarnesHut-related work:

- `AggregateHierarchy3D`
- generic descriptor columns
- `SizeDistanceOpening`
- `LeafOnlyOpening`
- aggregate reducer vocabulary
- backend-neutral execution contract
- app-owned RT-BarnesHut adapter

Goal5071 recommended implementing a CPU reference executor before a Numba prototype. Goal5072 implements that executor.

## Review Questions

1. Does Goal5072 correctly implement a generic CPU reference executor rather than an RT-BarnesHut-specific app path?
2. Is it correct that only `reference` is now `implemented_cpu_reference`, while `numba/cuda/optix/embree/hiprt` remain `not_implemented_contract_only`?
3. Does the executor support both required shapes: `SizeDistanceOpening + inverse_square_scalar_sum` and `LeafOnlyOpening + aggregate_count`?
4. Are the output rows aligned with `AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA`?
5. Does the executor fail closed on `max_output_rows` before materializing partial results?
6. Does the implementation avoid native/backend claims, device-resident claims, timing claims, and paper-reproduction claims?
7. Does `src/rtdsl/aggregate_hierarchy.py` remain free of app identity and native implementation terms?
8. Are the tests sufficient as a reference oracle for a later Numba/CUDA executor?
9. Is the change to `validate_aggregate_hierarchy_3d_contract()` appropriate now that CPU reference execution is authorized?
10. Should the next goal be a Numba parity prototype that uses this CPU reference executor as oracle?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
