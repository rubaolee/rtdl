# Goal5082 ContinuationPayloadOpening Rope-Branch Hardening Result

Date: 2026-07-07

## Verdict Label

`completed_continuation_payload_rope_branch_behavior_hardening`

## Purpose

Goal5081's external verification approved the non-RT-BarnesHut consumer proof, but left one non-blocking note:

> Add a stronger fixture where an accepted aggregate uses `rope_index` and `next_index != rope_index`.

Goal5082 implements that strengthening. This is not a new paper claim and not a performance goal. It is behavior coverage for the generic continuation-payload opening policy.

## Implementation

Added:

```text
tests/goal5082_continuation_payload_rope_branch_test.py
```

The new fixture is a non-paper synthetic linearized cluster hierarchy:

- three points,
- four hierarchy nodes,
- `ContinuationPayloadOpening(max_ratio=1.0)`,
- `AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT`,
- no RT-BarnesHut prepared-state adapter,
- no author sentinel normalization,
- no force law,
- no paper comparator.

The key structure is:

```text
node_next_index[1] = 2
node_rope_index[1] = 3
```

For sources `0` and `1`, node `1` is accepted as an aggregate. Correct behavior then follows `rope_index` to node `3`, skipping node `2`.

Expected rows:

```text
(source_id, reducer_value_0, visited_node_count, aggregate_contribution_count, exact_contribution_count)

(0, 2.0, 3, 1, 1)
(1, 2.0, 3, 1, 1)
(2, 2.0, 4, 0, 2)
```

The test also constructs an alternate fixture where the rope successor is deliberately changed to the next successor. The projected rows differ. This proves the fixture distinguishes the `rope_index` branch from the `next_index` branch.

## Verification

### New Rope-Branch Test

Command:

```text
py -m unittest tests.goal5082_continuation_payload_rope_branch_test
```

Result:

```text
Ran 4 tests in 4.431s
OK
```

### Goal5081 + Goal5082 Continuation-Payload Tests

Command:

```text
py -m unittest \
  tests.goal5081_continuation_payload_genericity_proof_test \
  tests.goal5082_continuation_payload_rope_branch_test
```

Result:

```text
Ran 8 tests in 3.865s
OK
```

### Full RT-BarnesHut / Aggregate-Hierarchy Local Suite

Command:

```text
py -m unittest \
  tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test \
  tests.goal5066_aggregate_hierarchy_contract_test \
  tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test \
  tests.goal5068_aggregate_hierarchy_descriptor_extension_test \
  tests.goal5069_aggregate_frontier_reduce_execution_contract_test \
  tests.goal5070_non_force_genericity_proof_test \
  tests.goal5072_aggregate_frontier_reduce_cpu_reference_test \
  tests.goal5073_aggregate_frontier_reduce_numba_parity_test \
  tests.goal5081_continuation_payload_genericity_proof_test \
  tests.goal5082_continuation_payload_rope_branch_test
```

Result:

```text
Ran 76 tests in 30.944s
OK (skipped=1)
```

The repeated local message:

```text
Could not find platform independent libraries <prefix>
```

is the known local Python environment message and did not affect the test result.

## What This Proves

- `ContinuationPayloadOpening` has a non-RT-BarnesHut behavior test that distinguishes `rope_index` from `next_index`.
- The accepted-aggregate branch uses `rope_index` as intended.
- The reference and optional Numba executors agree on the rope-branch fixture.
- The earlier Goal5081 genericity proof is strengthened without adding app-specific code.

## What This Does Not Prove

- It does not prove full RT-BarnesHut paper reproduction.
- It does not prove performance.
- It does not authorize native/CUDA aggregate-hierarchy backend completion.
- It does not change phase-boundary review status.

## Next Recommended Step

No additional code hardening is required before a bounded RT-BarnesHut same-input closeout.

The next decision should be:

1. close the bounded same-input RT-BarnesHut line with the current claim boundary, or
2. open a separate phase-boundary acceptance/completion-audit goal.
