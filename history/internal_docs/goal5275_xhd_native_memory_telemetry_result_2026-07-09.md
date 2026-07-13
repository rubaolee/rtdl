# Goal5275 - X-HD Native Memory Telemetry For RTDL Cell-MBR Route

## Status

`implemented_review_pending`

## Goal

Reduce the Figure 11 RTDL memory-accounting gap by exposing real native
OptiX/CUDA memory telemetry from the generic `cell-MBR nearest frontier` route.

This goal does **not** reproduce Figure 11.  It only replaces the previous
opaque/unavailable RTDL BVH field with a status-bearing native measurement when
the selected route actually uses the native OptiX cell-MBR frontier producer.

## What Changed

### Native backend

The native OptiX acceleration holder now records:

- `output_size_bytes`
- `temp_size_bytes`
- `aabb_size_bytes`
- `compacted_output_size_bytes`

The generic cell-MBR frontier workload now records thread-local telemetry for:

- OptiX GAS output buffer bytes
- transient GAS build workspace bytes
- AABB input buffer bytes
- route device buffers excluding the GAS
- row/query/cell/target/nearest buffer bytes
- attempted/emitted counts and mode bits

New optional native symbol:

```text
rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry
```

### Python runtime and partner wrapper

`src/rtdsl/optix_runtime.py` collects the optional telemetry when the symbol is
available and stores it under:

```text
native_memory_telemetry_collected
native_memory_telemetry
```

`src/rtdsl/partner_continuations.py` now forwards these fields through the
generic partner-continuation wrapper.  This was necessary because the first POD
probe showed the runtime had telemetry but the wrapper dropped it.

### X-HD memory accounting

`xhd_memory_accounting.py` maps native `accel_output_bytes` to the author-facing
`BVH` field with status:

```text
measured_native_optix_accel_output_buffer
```

It also exposes RTDL-only measured fields:

- `native_accel_build_temp`
- `native_accel_aabb_input`
- `native_route_device_buffers_excluding_accel`

These fields are explicitly **not** author Figure 11 parity.

## POD Build Evidence

POD:

```text
ssh root@213.173.108.24 -p 13502
GPU: NVIDIA RTX 4000 Ada Generation
CUDA nvcc: 12.0
OptiX SDK: /root/vendor/optix-dev
```

Build command:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/lib/cuda CUDA_INCLUDE=/usr/include CUDA_LIB=/usr/lib/x86_64-linux-gnu CXX_OPTIX=/usr/bin/nvcc NVCC=/usr/bin/nvcc
```

The first build attempt used `/usr/local/cuda` and failed due a CUDA 12.0 nvcc
versus CUDA 12.8 device-runtime mismatch.  The corrected system CUDA 12.0
include/lib path built successfully.

Exported symbol check:

```text
build/librtdl_optix.so
00000000000c21d0 T rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry
```

## POD Runtime Evidence

### Tiny 3D PLY

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_tiny3d_native_memory_telemetry_pod_2026-07-09.json
```

Summary:

```text
HDResult: 2.0
points: 2 -> 1
frontier rows / attempted: 0 / 0
total candidate evals: 2
native telemetry collected: true
BVH mapped bytes: 896
accel temp build bytes: 2688
accel AABB input bytes: 24
device buffers excluding accel: 568
```

### Stanford Dragon -> HappyBuddha sample256

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5275_stanford_sample256_native_memory_telemetry_pod_2026-07-09.json
```

Summary:

```text
HDResult: 0.07136699450130711
points: 256 -> 256
frontier rows / attempted: 0 / 0
total candidate evals: 405
native telemetry collected: true
BVH mapped bytes: 7552
accel temp build bytes: 14464
accel AABB input bytes: 3768
device buffers excluding accel: 169200
```

The frontier row count is zero in both probes because the current fast-scalar
route's initial nearest seed/global bound prunes the continuation frontier.
That does not invalidate the memory evidence: the native cell-MBR route still
builds the OptiX GAS and reports its output/temp/AABB/workspace bytes.

## Validation

Local tests:

```text
py -m unittest \
  tests.goal5275_xhd_native_memory_telemetry_contract_test \
  tests.goal5275_xhd_native_memory_telemetry_artifact_test \
  tests.goal5274_xhd_hd_exec_memory_accounting_integration_test \
  tests.goal5273_xhd_rtdl_memory_accounting_test

Ran 12 tests in 1.516s
OK
```

Compilation:

```text
py -m py_compile \
  src\rtdsl\optix_runtime.py \
  src\rtdsl\partner_continuations.py \
  Paper-reproduction-apps\x-hd-paper\scripts\xhd_memory_accounting.py \
  Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_cell_mbr_frontier_route_gate.py \
  tests\goal5275_xhd_native_memory_telemetry_contract_test.py
```

## Claim Boundary

Authorized claims:

- RTDL can now collect native OptiX GAS output-buffer telemetry for the generic
  3D cell-MBR nearest-frontier route when using a rebuilt backend.
- The hd_exec-compatible output can map that measured GAS output buffer to a
  status-bearing `BVH` memory field.
- The measurement is surfaced with explicit semantics and artifact tests.

Not authorized:

- Figure 11 is reproduced.
- RTDL memory equals author X-HD memory.
- `accel_output_bytes` is the author's exact BVH accounting denominator.
- transient build workspace is part of author Figure 11 BVH.
- WL Heavy Peak is measured.
- performance parity or speedup.

## Remaining Gap

Goal5275 closes the opaque RTDL BVH field for the native cell-MBR route in a
status-bearing way.  It does **not** close:

- author Figure 11 denominator alignment,
- WL Heavy Peak,
- exact GPU allocator peak accounting,
- paper dataset identity,
- full figure reproduction.

The next review decision should decide whether the current measured native
fields are sufficient for a bounded RTDL memory row, or whether a separate peak
allocator / heavy-worklist telemetry goal is required before any Figure 11
matrix can be attempted.
