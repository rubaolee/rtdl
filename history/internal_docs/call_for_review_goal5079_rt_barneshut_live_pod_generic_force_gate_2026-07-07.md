# Call For Review: Goal5079 RT-BarnesHut Live POD Generic Force Gate

Date: 2026-07-07

## Requested Verdict Label

`approve_goal5079_live_pod_generic_force_gate_same_input_closed`

## Review Scope

Please review:

- `history/internal_docs/goal5079_rt_barneshut_live_pod_generic_force_gate_result_2026-07-07.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/full_pod_reproduction_gate/summary.json`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/generic_aggregate_force_same_input_gate/summary.json`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/same_input_rtdl_comparison_gate/summary.json`
- `Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/same_input_performance_gate/summary.json`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

## Context

Goals5063-5078 reorganized the RT-BarnesHut paper app around generic RTDL aggregate-hierarchy contracts.

Goal5079 is the first live POD run after that reorganization where:

1. the patched-author binary produces same-input prepared arrays and force output,
2. the generic RTDL aggregate-hierarchy path consumes the prepared arrays,
3. the app-owned bridge writes scalar force rows,
4. the app-owned comparator checks the generic output against patched-author output,
5. the full POD gate also runs the older author-policy CUDA diagnostic and timing gates.

## Key Result To Review

The full POD gate reports:

```text
overall_status = passed_correctness_and_timing_gates__phase_boundary_review_required
```

The generic aggregate force same-input gate reports:

```text
generic_public_rtdl_api_used = true
opening.policy = continuation_payload_opening
force_comparison.matched = true
force_comparison.mismatch_count = 0
force_comparison.max_abs_error = 1830.0
force_comparison.max_rel_error = 2.1112736725325853e-06
```

The older author-policy CUDA same-input route reports:

```text
matched = true
mismatch_count = 0
max_abs_error = 1139.0
max_rel_error = 2.6233255615631954e-06
```

The same-input performance gate reports a narrow resident-kernel ratio:

```text
RTDL resident_kernel_min_ms = 0.856544017791748
author rt_core_force_ms = 2.083
ratio = 0.4112069216475026
```

This ratio is narrow and requires phase-boundary review before any paper-performance claim.

## Review Questions

1. Does the live POD evidence prove the generic aggregate force same-input gate matched the patched-author force output?
2. Is `ContinuationPayloadOpening(max_ratio=...)` a legitimate generic RTDL opening policy over continuation columns, rather than an RT-BarnesHut-only core shortcut?
3. Is it acceptable that author binary sentinel normalization remains in the app adapter while RTDL core sees only `-1` stop values and continuation columns?
4. Does the result preserve the system boundary: RTDL as generic aggregate-hierarchy language, RT-BarnesHut as app-owned prepared-state/comparator/output logic?
5. Did the local regression evidence sufficiently cover the new opening policy and author-binary adapter behavior before the POD run?
6. Does the full POD gate correctly include the generic aggregate force same-input gate alongside the older author-policy CUDA diagnostic gate?
7. Do the same-input force comparisons use appropriate tolerance and report enough error detail?
8. Is the environment remediation properly classified as non-algorithmic build/runtime setup rather than result manipulation?
9. Does the performance section correctly avoid turning the narrow resident-kernel ratio into a whole-paper or whole-envelope performance claim?
10. Should `paper_reproduction_complete` remain false until a separate phase-boundary and paper-scope review explicitly closes it?
11. Are there any remaining blocking concerns before closing Goal5079 with the requested verdict?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 11 review questions
