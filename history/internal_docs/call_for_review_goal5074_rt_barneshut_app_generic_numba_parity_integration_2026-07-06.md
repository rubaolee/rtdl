# Call For Review: Goal5074 RT-BarnesHut App Generic Numba Parity Integration

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5074_rt_barneshut_app_generic_numba_parity_integration_result_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`
- `src/rtdsl/aggregate_hierarchy.py`

## Requested Verdict Labels

Use one:

- `approve_goal5074_app_owned_generic_numba_parity_integration`
- `approve_with_required_amendments`
- `block_goal5074_app_integration`

## Context

Goal5072 implemented the CPU reference executor for generic aggregate frontier reduce.

Goal5073 implemented the optional CPU Numba parity prototype.

Goal5074 connects those public APIs to the RT-BarnesHut app adapter and CLI over app-prepared arrays.

## Review Questions

1. Does Goal5074 keep the integration app-owned rather than moving RT-BarnesHut logic into RTDL core?
2. Does the app route use public generic RTDL APIs rather than private diagnostic kernels?
3. Is the `aggregate-numba-parity` CLI correctly scoped as a parity gate, not an author comparator?
4. Does the parity summary correctly report `paper_reproduction_complete: false` and `same_input_author_comparator: false`?
5. Does the adapter avoid Torch/CUDA/native/OptiX imports or symbols?
6. Does `src/rtdsl/aggregate_hierarchy.py` remain app-name-free?
7. Are the tests sufficient to prove app-prepared arrays can run through reference and Numba executors with `mismatch_count = 0`?
8. Is it acceptable that this goal makes no performance claim?
9. Does this integration preserve the distinction between public generic RTDL system work and RT-BarnesHut paper-app ownership?
10. Should the next goal be a bounded force-output bridge, or should another genericity/regression gate run first?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
