# Call For Review - Goal5275 X-HD Native Memory Telemetry

Please strictly review Goal5275:

```text
history/internal_docs/goal5275_xhd_native_memory_telemetry_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_tiny3d_native_memory_telemetry_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_stanford_sample256_native_memory_telemetry_pod_2026-07-09.json
tests/goal5275_xhd_native_memory_telemetry_contract_test.py
tests/goal5275_xhd_native_memory_telemetry_artifact_test.py
src/native/optix/rtdl_optix_core.cpp
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
```

## Context

Goal5273 defined an RTDL memory-accounting boundary for X-HD Figure 11 but left
BVH unavailable.  Goal5274 attached that status-bearing accounting to the
hd_exec-compatible output.  Goal5275 attempts to close the BVH opacity gap for
the generic native OptiX cell-MBR nearest-frontier route by exposing real native
memory telemetry.

The work must be reviewed harshly because a measured byte field can easily be
misread as author Figure 11 parity.  That is **not** the claim.

## Review Questions

1. Does the native implementation genuinely measure OptiX acceleration output,
   temp build workspace, AABB input, and route device-buffer bytes rather than
   inventing estimates?
2. Is the new optional symbol
   `rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry` wired
   safely and backward-compatibly?
3. Does Python runtime collection correctly tolerate old libraries that do not
   export the optional symbol?
4. Does `partner_continuations.py` actually forward the telemetry through the
   high-level generic route metadata?
5. Do the POD artifacts prove the rebuilt native library exports the symbol and
   that hd_exec-compatible JSON receives measured telemetry?
6. Is it acceptable that both POD probes have `frontier_row_count=0` because the
   initial seed/global bound prunes continuation rows, while the native GAS and
   device buffers are still measured?
7. Is mapping `accel_output_bytes` to the status-bearing author-facing `BVH`
   field honest, given that it explicitly excludes transient build workspace and
   is not author Figure 11 parity?
8. Do the artifact tests guard against losing telemetry between native runtime,
   partner wrapper, route summary, and memory accounting?
9. Does the packet avoid claiming Figure 11 reproduction, exact GPU allocator
   measurement, author memory parity, WL Heavy Peak measurement, or performance
   parity?
10. What is the next blocker after this: is a bounded RTDL memory row now
    defensible, or must peak allocator / heavy-worklist telemetry be implemented
    first?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5275_native_memory_telemetry | approve_with_required_amendments | reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
```

If approving, please include this exact label if appropriate:

```text
approve_goal5275_xhd_native_cell_mbr_memory_telemetry__figure11_still_not_reproduced
```
