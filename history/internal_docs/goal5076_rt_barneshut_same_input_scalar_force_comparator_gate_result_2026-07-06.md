# Goal5076 RT-BarnesHut Same-Input Scalar Force Comparator Gate Result

Date: 2026-07-06

## Verdict Label

`completed_app_owned_same_input_scalar_force_comparator_gate`

## Purpose

Goal5075 added an app-owned bridge from generic aggregate reducer rows to RT-BarnesHut scalar force-output rows. Goal5076 turns that bridge into a bounded comparator gate:

```text
prepared aggregate arrays + expected scalar force file
  -> generic RTDL aggregate hierarchy API
  -> optional Numba aggregate-frontier reducer
  -> app-owned scalar force bridge
  -> force-file comparator
```

This is still an app-owned gate. It does not promote the RT-BarnesHut comparator, author prepared-state dump, force-output formatting, or author binary hooks into RTDL core.

## Implementation

Changed files:

- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.sh`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

New CLI mode:

```text
python Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  --mode aggregate-numba-force-compare \
  --prepared-arrays-json <prepared.json> \
  --expected-force-output <expected_forces.txt> \
  --force-output <candidate_forces.txt> \
  --output <summary.json>
```

New app-owned POD/local runner:

```text
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.sh
```

Default inputs for the shell runner:

- expected author force file: `Paper-reproduction-apps/rt-barneshut-paper/_runs/author_same_input/author_treelogy_forces.txt`
- author prepared arrays: `Paper-reproduction-apps/rt-barneshut-paper/_runs/author_same_input/author_treelogy_prepared_arrays.json`

These defaults are produced by the existing patched-author same-input route. They can be overridden with:

```text
AUTHOR_FORCE=<force file>
PREPARED_ARRAYS=<prepared arrays json>
```

## Comparator Contract

The new mode:

1. runs the Goal5075 generic aggregate force-output bridge,
2. writes a candidate scalar force file,
3. compares it to an expected scalar force file using the existing app-owned `compare_force_outputs.py`,
4. returns process status `0` only if the scalar force files match under the declared tolerance.

The emitted summary includes:

- `mode: aggregate_numba_force_compare`
- `same_input_author_comparator: true|false`
- `force_comparison`
- `candidate_force_output`
- `expected_force_output`
- `paper_reproduction_complete: false`
- `claim_boundary`

## Verification

### Full RT-BarnesHut Aggregate-Hierarchy Regression

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
Ran 65 tests in 21.216s
OK (skipped=1)
```

### Local Synthetic Comparator Smoke

Synthetic 32-body prepared arrays and expected scalar force rows were generated with `author_contract_reference.py`. The new CLI mode then produced candidate forces through the generic aggregate-hierarchy route and compared the files.

Observed summary fields:

```json
{
  "mode": "aggregate_numba_force_compare",
  "same_input_author_comparator": true,
  "paper_reproduction_complete": false,
  "generic_public_rtdl_api_used": true,
  "force_comparison": {
    "matched": true,
    "left_count": 32,
    "right_count": 32,
    "common_count": 32,
    "mismatch_count": 0,
    "max_abs_error": 0.0,
    "max_rel_error": 0.0
  }
}
```

### Compile And Core Scan

Command:

```text
py -m py_compile \
  Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py \
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

- The paper app now has a bounded scalar force comparator gate that can consume prepared arrays and an expected force file.
- The comparator route can be exercised locally with synthetic author-contract reference data.
- The same comparator route can be used on POD artifacts produced by the patched author binary.
- The route still uses public generic RTDL aggregate-hierarchy APIs for aggregate traversal.

## What This Does Not Prove

- It is not full RT-BarnesHut paper reproduction completion.
- The local synthetic smoke is not a patched-author binary run.
- It is not a performance claim.
- It is not a native CUDA, OptiX, or device-resident backend.
- It does not move author prepared-state reading, force formatting, or comparator logic into RTDL core.

## Next Recommended Goal

Run the new comparator gate on a POD using the patched-author same-input artifacts:

1. run `scripts/run_author_same_input.sh` to produce author force output and prepared arrays,
2. run `scripts/run_generic_aggregate_force_same_input_gate.sh`,
3. verify the summary reports `same_input_author_comparator: true`,
4. keep the result bounded as same-input scalar force comparison, not full paper reproduction.
