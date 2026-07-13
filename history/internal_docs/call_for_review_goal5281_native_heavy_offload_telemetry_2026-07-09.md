# Call For Review - Goal5281 Native Heavy/Offload Telemetry ABI Spike

Please strictly review Goal5281.

Files:

```text
history/internal_docs/goal5281_native_heavy_offload_telemetry_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json
tests/goal5281_native_heavy_offload_telemetry_contract_test.py
tests/goal5281_native_heavy_offload_telemetry_artifact_test.py
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
```

Context:

```text
Goal5279 added a generic heavy/offload worklist CPU reference.
Goal5280 added a non-X-HD retry/backlog consumer.
Goal5281 adds native/POD telemetry ABI evidence for generic offload frontier rows.
```

Requested verdict labels:

```text
approve_goal5281_native_heavy_offload_telemetry_abi
revise_goal5281_native_heavy_offload_telemetry_abi
block_goal5281_native_heavy_offload_telemetry_abi
```

Review questions:

1. Does the implementation preserve the existing v1 native telemetry ABI while
   adding a v2 symbol for the new fields?
2. Is the v2 symbol actually exported by the POD native build?
3. Does the POD artifact prove that v2 telemetry is collected at runtime rather
   than only declared in source?
4. Are `heavy_offload_peak_rows` and `heavy_offload_queue_peak_bytes` consistent
   with the observed offload frontier rows and the generic two-id queue shape?
5. Are the v2 field names and semantics generic, or are they secretly X-HD
   Figure 11 / author-specific?
6. Does the Python runtime correctly prefer v2 when available and keep v1
   fallback compatibility?
7. Does the artifact test protect the claim boundary that this is not Figure 11
   reproduction, not author memory parity, and not a performance claim?
8. Is the current `miss_queue_capacity = 0` statement acceptable for the current
   generic cell-MBR route, or must it be renamed / made more explicit before
   Goal5282?
9. Is Goal5282, the X-HD bounded mapping to author offload fields, now the
   correct next goal?
10. Are there any required amendments before Goal5281 can be marked externally
    reviewed and approved?

Expected answer shape:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to review questions:
1. ...
```

Claim boundary to enforce:

```text
Goal5281 may claim native/POD v2 generic offload telemetry exists.
Goal5281 may not claim X-HD Figure 11 reproduction, author memory parity,
same-denominator memory comparison, or any performance win.
```
