# Goal5074 RT-BarnesHut App Generic Numba Parity Integration Result

Date: 2026-07-06

## Verdict Label

`completed_rt_barneshut_app_owned_generic_numba_parity_mode`

## Purpose

Goal5074 connects the RT-BarnesHut paper app to the public generic RTDL aggregate hierarchy executors added in Goals5072-5073.

The goal is app-owned integration:

- RT-BarnesHut prepared arrays are adapted to `AggregateHierarchy3D`;
- public RTDL reference executor produces oracle rows;
- public RTDL Numba executor produces candidate rows;
- the app compares those rows in a bounded parity mode.

This is not the patched author binary comparator, not paper completion, not CUDA/OptiX traversal, and not a performance claim.

## What Changed

Updated:

- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

## App-Owned Public API Route

New adapter functions:

```python
run_generic_aggregate_frontier_numba_parity(prepared, ...)
read_prepared_arrays_and_run_generic_numba_parity(path, ...)
```

New CLI mode:

```bash
python Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  --mode aggregate-numba-parity \
  --prepared-arrays-json <prepared.json> \
  --output <parity.json>
```

Route:

```text
RT-BarnesHut prepared arrays
-> aggregate_hierarchy_adapter.prepared_arrays_to_aggregate_hierarchy(...)
-> rtdsl.aggregate_frontier_reduce_reference_3d(...)
-> rtdsl.aggregate_frontier_reduce_numba_3d(...)
-> app-owned row comparison summary
```

## What This Proves

It proves that the RT-BarnesHut paper app can consume its prepared arrays through the public generic RTDL aggregate hierarchy surface and run a Numba parity candidate against the CPU reference oracle.

It also proves the Numba route is not only a unit-level toy: it is now wired through the paper app entrypoint over app-prepared arrays.

## What This Does Not Prove

Not claimed:

- patched author binary comparison;
- paper reproduction completion;
- whole-program parity;
- CUDA/OptiX/native traversal;
- device residency;
- performance improvement;
- author performance parity.

## Manual Smoke

Command shape:

```text
py Paper-reproduction-apps/rt-barneshut-paper/author_contract_reference.py --synthetic-count 32 --write-rtdl-prepared-arrays <prepared.json> --summary <summary.json>
py Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py --mode aggregate-numba-parity --prepared-arrays-json <prepared.json> --output <parity.json>
```

Observed summary:

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

## Verification

Combined RT-BarnesHut scaffold + aggregate hierarchy regression:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test tests.goal5073_aggregate_frontier_reduce_numba_parity_test
```

Result:

```text
Ran 62 tests in 11.648s
OK (skipped=1)
```

Syntax check:

```text
py -m py_compile Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py
```

Result:

```text
OK
```

Core app-identity scan:

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

The local Python runtime still prints:

```text
Could not find platform independent libraries <prefix>
```

The tests completed successfully despite this local environment warning.

## Boundary

The app-owned parity mode uses public RTDL APIs:

- `AggregateHierarchy3D`
- `prepare_aggregate_hierarchy_3d`
- `aggregate_frontier_reduce_spec_3d`
- `aggregate_frontier_reduce_reference_3d`
- `aggregate_frontier_reduce_numba_3d`

The RTDL core remains app-name-free. The app owns prepared-array reading, paper-specific comparator interpretation, and user-facing paper-app command modes.

## Next Step

Recommended next goal:

```text
Goal5075: bounded RT-BarnesHut same-input force-output bridge from generic aggregate rows
```

Goal5075 should decide whether generic scalar rows can be safely translated into the app's force-output format for a bounded comparison. It must keep the author binary comparator separate and must not claim paper completion unless the comparator gate itself is run and passes.
