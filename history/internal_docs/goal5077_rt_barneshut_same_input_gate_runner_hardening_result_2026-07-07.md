# Goal5077 RT-BarnesHut Same-Input Gate Runner Hardening Result

Date: 2026-07-07

## Verdict Label

`completed_cross_platform_same_input_force_gate_runner`

## Purpose

Goal5076 added the `aggregate-numba-force-compare` CLI mode. Goal5077 hardens the surrounding gate so it is reusable on local Windows, local Linux, and POD environments.

The key improvement is a Python gate runner:

```text
Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.py
```

The existing shell runner now delegates to this Python runner.

## Implementation

Changed files:

- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.sh`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

The Python runner accepts:

```text
--prepared-arrays <prepared.json>
--expected-force <expected_forces.txt>
--run-dir <gate output dir>
--python <python executable>
--rtol <relative tolerance>
--atol <absolute tolerance>
--theta <opening max-ratio>
--softening <softening>
```

Default app-owned POD inputs:

```text
Paper-reproduction-apps/rt-barneshut-paper/_runs/author_same_input/author_treelogy_prepared_arrays.json
Paper-reproduction-apps/rt-barneshut-paper/_runs/author_same_input/author_treelogy_forces.txt
```

These defaults are produced by `scripts/run_author_same_input.sh`.

## Claim Boundary

This goal is runner hardening.

It does not claim:

- patched-author binary comparison was run locally,
- full paper reproduction completion,
- performance,
- native/CUDA/OptiX implementation,
- device-resident implementation.

The runner simply makes the app-owned same-input scalar force comparator gate easier to execute consistently.

## Verification

### Full Local Regression

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
  tests.goal5073_aggregate_frontier_reduce_numba_parity_test
```

Result:

```text
Ran 67 tests in 27.958s
OK (skipped=1)
```

### New Tests

Added local tests for:

- Python runner success on synthetic prepared arrays and force rows,
- Python runner fail-closed behavior when required inputs are missing,
- scaffold file existence for the Python runner.

Observed synthetic gate output:

```text
summary.json
mode = aggregate_numba_force_compare
same_input_author_comparator = true
force_comparison.matched = true
force_comparison.mismatch_count = 0
gate_runner.mode = generic_aggregate_force_same_input_gate
```

Fail-closed behavior:

```text
missing prepared arrays -> exit code 2
```

### Compile And Core Scan

Command:

```text
py -m py_compile \
  Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.py \
  Paper-reproduction-apps/rt-barneshut-paper/scripts/compare_force_outputs.py
```

Result:

```text
PY_COMPILE_OK
```

Core identity scan:

```text
src/rtdsl/aggregate_hierarchy.py:
  no BarnesHut, Treelogy, RTBH, author-optix-payload, torch, rtdl_optix, or RayJoin leak
```

## What This Proves

- The same-input scalar force comparator gate has a cross-platform Python runner.
- The runner works locally using synthetic author-contract reference artifacts.
- The runner fails closed when required prepared arrays or force files are missing.
- The app/system boundary remains intact.

## What This Does Not Prove

- It does not prove patched-author binary parity on this local machine.
- It does not prove full paper reproduction completion.
- It does not prove performance.

## Next Recommended Goal

Goal5078 should run the same Python gate on a POD with patched-author artifacts:

1. run `scripts/run_author_same_input.sh`,
2. run `scripts/run_generic_aggregate_force_same_input_gate.py` or `.sh`,
3. preserve `summary.json`, expected force file, candidate force file, and prepared arrays summary,
4. require `same_input_author_comparator = true`,
5. keep `paper_reproduction_complete = false` unless separately reviewed.
