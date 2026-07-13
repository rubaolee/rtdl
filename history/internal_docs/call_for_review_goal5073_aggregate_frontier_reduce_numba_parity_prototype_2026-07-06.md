# Call For Review: Goal5073 Aggregate Frontier Reduce Numba Parity Prototype

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5073_aggregate_frontier_reduce_numba_parity_prototype_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5069_aggregate_frontier_reduce_execution_contract_test.py`
- `tests/goal5070_non_force_genericity_proof_test.py`
- `tests/goal5072_aggregate_frontier_reduce_cpu_reference_test.py`
- `tests/goal5073_aggregate_frontier_reduce_numba_parity_test.py`

## Requested Verdict Labels

Use one:

- `approve_goal5073_optional_numba_cpu_parity_prototype`
- `approve_with_required_amendments`
- `block_goal5073_numba_parity_prototype`

## Context

Goal5072 implemented `aggregate_frontier_reduce_reference_3d` as the CPU reference oracle for the generic aggregate hierarchy execution contract.

Goal5073 adds an optional CPU Numba prototype. It uses the same generic contract, output schema, opening policies, and reducers. It should not be interpreted as a CUDA/backend/device-resident implementation.

## Review Questions

1. Does Goal5073 keep RTDL generic, with no RT-BarnesHut app identity in `src/rtdsl/aggregate_hierarchy.py`?
2. Is it correct to classify `numba` as `optional_numba_cpu_reference_prototype` rather than native/backend complete?
3. Does the implementation fail closed when Numba is unavailable, instead of silently falling back to the Python reference executor?
4. Do the tests prove parity against `aggregate_frontier_reduce_reference_3d` for both `LeafOnlyOpening + aggregate_count` and `SizeDistanceOpening + inverse_square_scalar_sum`?
5. Is the output schema preserved between reference and Numba paths?
6. Does the implementation avoid CUDA/OptiX/device-resident/performance claims?
7. Is installing Numba locally for verification acceptable, given the executor remains optional at runtime?
8. Are the existing backend statuses for `cuda/optix/embree/hiprt` still correctly left as `not_implemented_contract_only`?
9. Is the runtime-dependency metadata sufficient for users to understand that this is optional partner execution?
10. Should the next goal be app-owned integration into RT-BarnesHut bounded same-input parity mode, using only the public generic APIs?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
