# Goal5075 RT-BarnesHut Generic Aggregate Force-Output Bridge Result

Date: 2026-07-06

## Verdict Label

`completed_app_owned_scalar_force_output_bridge_from_generic_aggregate_rows`

## Purpose

Goal5063-5074 established a generic RTDL aggregate-hierarchy route for the RT-BarnesHut reproduction app:

- RTDL core owns generic aggregate hierarchy descriptors, opening policies, and reference/optional Numba aggregate-frontier reducers.
- RT-BarnesHut owns author prepared-state reading, app comparator boundaries, and app output formats.

Goal5075 closes the next app-facing gap: convert generic aggregate reducer rows into the RT-BarnesHut scalar force-output shape without promoting Barnes-Hut force semantics into RTDL core.

## Implementation

Changed files:

- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

New app-owned adapter surface:

- `aggregate_rows_to_scalar_force_rows(rows, force_output_scale=0.1)`
- `write_scalar_force_rows(path, rows)`
- `run_generic_aggregate_frontier_numba_force_bridge(...)`
- `read_prepared_arrays_and_run_generic_numba_force_bridge(...)`

New app CLI mode:

```text
python Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  --mode aggregate-numba-force-output \
  --prepared-arrays-json <prepared.json> \
  --force-output <forces.txt> \
  --output <summary.json>
```

## Force Contract

The author-side force output for this app is scalar, not a 3D vector. The bridge therefore maps the generic inverse-square scalar reducer into app force rows:

```text
scalar_force = reducer_value_0 * 0.1
```

The `0.1` scale is kept in the app adapter as `DEFAULT_FORCE_OUTPUT_SCALE`, not in RTDL core. The emitted force file is an app-owned text sink:

```text
<source_id> <scalar_force>
```

## Generic-System Boundary

RTDL core remains app-neutral:

- no BarnesHut identity in `src/rtdsl/aggregate_hierarchy.py`
- no RTBH, Treelogy, author payload, torch extension, or native OptiX hook in the generic aggregate-hierarchy module
- reducer output remains generic aggregate rows
- scalar force formatting remains app-owned

The app bridge explicitly reports:

- `app_owned_force_output_bridge`
- `maps_generic_scalar_reducer_to_app_scalar_force_rows`
- `uses_public_generic_rtdl_aggregate_hierarchy_api`
- `not_author_binary_comparator`
- `not_paper_reproduction_completion`
- `not_performance_claim`

## Verification

### Full Regression

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
Ran 64 tests in 15.001s
OK (skipped=1)
```

### Force Bridge CLI Smoke

Synthetic 32-body prepared arrays were produced with the app author-contract reference helper, then passed through the public generic aggregate-hierarchy adapter and the new force-output bridge.

Observed summary:

```json
{
  "mode": "aggregate_numba_force_output",
  "force_output_exists": true,
  "generic_public_rtdl_api_used": true,
  "paper_reproduction_complete": false,
  "same_input_author_comparator": false,
  "bridge": {
    "mode": "generic_aggregate_frontier_numba_force_bridge",
    "candidate_backend": "numba",
    "comparison_to_reference_executor_force_rows": {
      "match": true,
      "mismatch_count": 0,
      "max_abs_delta": 0.0,
      "max_rel_delta": 0.0,
      "source_count": 32
    }
  }
}
```

The generated force file contained 32 scalar force rows.

### Compile And Leak Checks

Command:

```text
py -m py_compile \
  Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py \
  Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  src/rtdsl/aggregate_hierarchy.py
```

Result:

```text
PY_COMPILE_OK
```

Scans:

```text
src/rtdsl/aggregate_hierarchy.py:
  no BarnesHut, Treelogy, RTBH, author-optix-payload, torch, rtdl_optix, RayJoin leak

Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py:
  no torch extension, ctypes, or native OptiX hook
```

## What This Proves

- Generic aggregate rows can be converted by the app into scalar force output without adding Barnes-Hut force semantics to RTDL core.
- Optional Numba aggregate-frontier output and CPU reference aggregate-frontier output map to identical scalar force rows on the controlled synthetic route.
- The app CLI can now produce a bounded scalar force output file from prepared arrays through the generic aggregate-hierarchy API.

## What This Does Not Prove

- It is not a patched-author binary comparator.
- It is not full RT-BarnesHut paper reproduction completion.
- It is not a CUDA, OptiX, native, or device-resident backend.
- It is not a performance claim.
- It does not move author prepared-state reading into RTDL core.

## Next Recommended Goal

If continuing this RT-BarnesHut line, the next goal should be a bounded same-input comparator gate:

- run the author prepared-state dump and force dump on the same synthetic or recovered paper-scale input,
- run the generic aggregate hierarchy force-output bridge on the dumped prepared state,
- compare scalar force rows within the declared author-contract tolerance,
- keep all author binary, prepared-state, and force-output details in the paper app.
