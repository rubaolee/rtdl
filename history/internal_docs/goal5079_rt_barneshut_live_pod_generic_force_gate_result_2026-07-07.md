# Goal5079 RT-BarnesHut Live POD Generic Force Gate Result

Date: 2026-07-07

## Verdict Label

`completed_live_pod_generic_aggregate_force_same_input_gate`

## Purpose

Goal5079 runs the RT-BarnesHut full POD gate against live patched-author artifacts after the Goal5063-5078 rearchitecture.

The specific question was:

> Can the RT-BarnesHut paper app use the generic RTDL aggregate-hierarchy API, plus app-owned prepared-state and force-output adapters, to reproduce the patched-author same-input scalar force output on the POD?

This goal is not a full paper-performance claim. It is a same-input correctness and phase-boundary gate.

## POD And Command

POD:

```text
ssh root@213.173.108.24 -p 13502
```

Remote runner command:

```text
py Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py \
  --host 213.173.108.24 \
  --port 13502 \
  --user root \
  --identity C:/Users/Lestat/.ssh/id_ed25519_rtdl_codex_current_pod \
  --remote-env CUDA_PREFIX=/usr \
  --run-id g5079cont
```

Pulled local artifact root:

```text
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled
```

Remote full gate summary:

```text
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/full_pod_reproduction_gate/summary.json
```

## Environment Remediation

The POD needed non-algorithmic environment repair before the gates could run:

- installed `ninja` for author CUDA/OWL build,
- installed OpenGL development packages required by the author source build,
- replaced incomplete local OptiX headers with NVIDIA public `optix-dev` v8.0.0 headers,
- installed Ubuntu `nvidia-cuda-toolkit` 12.0 and ran the gate with `CUDA_PREFIX=/usr` because the POD driver rejected CUDA 12.8 PTX,
- installed Python `numba` for the generic aggregate Numba parity path.

These changes do not alter the RT-BarnesHut algorithm or RTDL implementation. They are build/runtime environment fixes.

## Implementation Fix Required Before Passing

The first live generic aggregate force gate failed because `SizeDistanceOpening` reproduced the geometric opening rule but not the author's linearized payload traversal contract.

The repair was to add an app-neutral continuation-column opening policy to RTDL:

```text
ContinuationPayloadOpening(max_ratio=...)
policy = continuation_payload_opening
requires_continuation_columns = ("node_next_index", "node_rope_index")
app_specific_policy_allowed = false
```

Changed RTDL files:

- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`

Changed app/test files:

- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

The app adapter normalizes author binary continuation sentinels into generic `-1` stop values and selects `ContinuationPayloadOpening` only for the author-binary prepared-state contract.

Amendment note: at Goal5079 close, `ContinuationPayloadOpening` is app-neutral in RTDL core but should be treated as provisional generic until a non-RT-BarnesHut consumer proves the policy independently. Author binary parsing and sentinel normalization remain app-owned. Goal5081 adds the required non-RT-BarnesHut continuation-payload consumer proof.

## Local Regression

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
Ran 68 tests in 31.342s
OK (skipped=1)
```

Focused continuation/opening regression:

```text
Ran 29 tests
OK (skipped=1)
```

## Full POD Gate Result

Overall full gate status:

```text
passed_correctness_and_timing_gates__phase_boundary_review_required
```

All eight gates passed:

```text
local_contract_gate: passed
author_source_contract_gate: passed
pod_environment_preflight: passed
author_contract_rtdl_cuda_gate: passed
author_comparator_gate: passed
generic_aggregate_force_same_input_gate: passed
same_input_author_vs_rtdl_gate: passed
same_input_performance_gate: passed
```

## Key Evidence

### Patched-Author Same-Input Comparator

Artifact:

```text
_runs/author_comparator_gate/summary.json
```

Result:

```text
force_count = 32768
matched = true
max_abs_error = 0.0
max_rel_error = 0.0
```

This confirms the patched-author new-mode and treelogy same-input force files agree byte-for-comparison under the app comparator.

### Generic Aggregate Force Same-Input Gate

Artifact:

```text
_runs/generic_aggregate_force_same_input_gate/summary.json
```

Result:

```text
generic_public_rtdl_api_used = true
source_contract = rt_barneshut_author_binary_prepared_state_v1
opening.policy = continuation_payload_opening
node_count = 1486
point_count = 32768
force_comparison.matched = true
force_comparison.mismatch_count = 0
force_comparison.max_abs_error = 1830.0
force_comparison.max_rel_error = 2.1112736725325853e-06
rtol = 0.0001
atol = 0.0001
```

The generic aggregate API route and app-owned force bridge match the patched-author same-input force output within the agreed tolerance.

The internal reference-vs-Numba parity also passed:

```text
comparison_to_reference_executor_force_rows.match = true
comparison_to_reference_executor_force_rows.mismatch_count = 0
comparison_to_reference_executor_force_rows.max_abs_delta = 0.0
comparison_to_reference_executor_force_rows.max_rel_delta = 0.0
```

### Legacy/Diagnostic Author-Policy CUDA Gate

Artifact:

```text
_runs/same_input_rtdl_comparison_gate/summary.json
```

Result:

```text
force_count = 32768
matched = true
mismatch_count = 0
max_abs_error = 1139.0
max_rel_error = 2.6233255615631954e-06
traversal_policy = author-optix-payload
```

This confirms the earlier CUDA diagnostic route remains correct after the generic aggregate API work.

### Same-Input Narrow Force Timing

Artifact:

```text
_runs/same_input_performance_gate/summary.json
```

Author treelogy timing:

```text
preprocessing_ms = 18.804
rt_core_force_ms = 2.083
execution_ms = 166.642
```

RTDL diagnostic timing:

```text
extension_compile_ms = 55.8721125125885
tree_prepare_cpu_ms = 252.25137174129486
tensor_prepare_host_to_device_ms = 160.36569327116013
resident_kernel_min_ms = 0.856544017791748
resident_kernel_mean_ms = 0.9283008098602294
```

Narrow resident-kernel ratio:

```text
rtdl resident_kernel_min / author rt_core_force = 0.4112069216475026
```

This ratio is a narrow force-kernel comparison only. It excludes RTDL extension compile, CPU tree/prepared-array processing, host-to-device tensor preparation, and force-file output. It also does not close whole-paper performance.

## What This Proves

- The full live POD gate can build and run the patched-author RT-BarnesHut artifacts.
- The app-owned patched-author comparator closes for same-input force files.
- The app-neutral RTDL aggregate-hierarchy route, using `ContinuationPayloadOpening`, matches the patched-author same-input scalar force output.
- At Goal5079 close, `ContinuationPayloadOpening` was provisional generic because the live consumer was RT-BarnesHut; Goal5081 supplies the non-RT-BarnesHut consumer proof.
- The older author-policy CUDA diagnostic same-input route still matches the patched-author force output.
- The force-kernel phase boundary is ready for human review.

## What This Does Not Prove

- It does not prove full RT-BarnesHut paper reproduction.
- It does not prove the original paper benchmark suite or all paper workloads.
- It does not authorize broad performance claims.
- It does not authorize claiming RTDL whole-envelope speedup over the author program.
- It does not move author binary parsing, comparator logic, or force-output formatting into RTDL core.

## System Boundary

RTDL core now exposes:

- generic `AggregateHierarchy3D`,
- generic `SizeDistanceOpening`,
- generic `LeafOnlyOpening`,
- generic aggregate frontier reducers/executors.

`ContinuationPayloadOpening` is app-neutral in core and provisional at the Goal5079 boundary. It becomes eligible for a stronger genericity claim only after the Goal5081 non-RT-BarnesHut consumer proof.

The RT-BarnesHut app owns:

- author prepared-state reading,
- author continuation sentinel normalization,
- scalar force-output scaling/formatting,
- same-input force comparator,
- patched-author build and gate orchestration.

This preserves the principle:

```text
RTDL is a generic system/language; RT-BarnesHut is an app on top of it.
```

## Next Recommended Goal

Send Goal5079 for external review.

If approved, the next technical direction should be decided explicitly:

1. close the bounded same-input RT-BarnesHut reproduction arc as correctness-ready but phase-boundary-review-limited, or
2. proceed to a new goal that compares whole-envelope timing and paper benchmark scope under a separately reviewed performance definition.
