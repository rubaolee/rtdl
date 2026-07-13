# Call For Review - Goal5402 Generic Status-State Machine Native Smoke

Please strictly review Goal5402.

## Files To Review

Result report:

```text
history/internal_docs/goal5402_generic_status_state_machine_native_smoke_result_2026-07-10.md
```

Implementation and tests:

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5402_status_state_machine_native_smoke.py
tests/goal5402_status_state_machine_native_smoke_test.py
```

POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5402_status_state_machine_native_smoke_pod.json
```

Prior decision/evidence:

```text
history/internal_docs/goal5399_xhd_status_machine_semantic_gap_decision_2026-07-10.md
history/internal_docs/goal5400_xhd_existing_status_stream_knob_matrix_result_2026-07-10.md
history/internal_docs/goal5401_generic_status_state_machine_spike_contract_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_pod.json
```

## Review Questions

1. Does Goal5402 implement a real native symbol and Python front door, rather
   than only a design contract?
2. Does the native smoke satisfy the Goal5401 contract's first semantic step:
   raw offload rows before continuation/reduce?
3. Does it report feedback telemetry on the synthetic fixture?
4. Does the POD artifact prove that the rebuilt native symbol executed on POD?
5. Are overflow and failure modes fail-closed enough at this stage?
6. Are the new native/public names app-neutral and free of X-HD / paper /
   figure identity?
7. Does the report correctly avoid claiming explicit `-lb` support, row/hash
   parity, Figure 7/11, performance parity, exact dataset reproduction, or full
   X-HD reproduction?
8. Is the next-goal recommendation appropriately bounded, or does Goal5402
   still need a stronger bounded app gate before any full Goal5387 oracle gate?

## Expected Answer Shape

Please respond with:

```text
Verdict:
  approve_goal5402_generic_status_state_machine_native_smoke
  OR approve_with_required_amendments
  OR revise_goal5402

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 8 review questions:
  ...
```

## Proposed Verdict

```text
approve_goal5402_generic_status_state_machine_native_smoke
```
