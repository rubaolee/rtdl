# Goal5842R1 V2 Pre-Output Failure

Date: 2026-09-03

Source commit: `0d3c2fa8feb2d41d2acc23e956b90f255085abef`

Hardware: NVIDIA RTX A6000, compute capability 8.6, UUID
`GPU-6457d4af-a4bb-bff5-a9d2-02f251ceca27`, driver 550.127.08.

The clean Pod checkout passed the 148-test related regression set, with one
environment skip. The diagnostic runner then failed closed on its first scalar
execution before writing a result JSON. No timing row from this attempt is an
accepted result.

The native v7 operation succeeded and returned this receipt projection:

```text
schema_version=2
optix_launch_count=1
host_blocking_boundary_count=2
control_d2h_bytes=12
output_d2h_bytes=8
status_before_output=true
role_counters_materialized=false
prepared_input_reused=false
dynamic_device_upload_call_count=8
dynamic_device_upload_bytes=589824
dynamic_input_generation=1
callback_status_kernel_launch_count=0
checked_product_kernel_launch_count=0
compact_control_finalizer_kernel_launch_count=0
total_auxiliary_cuda_kernel_launch_count=0
execution_parameter_h2d_bytes=224
execution_parameter_h2d_copy_call_count=1
stream_ordered_memset_call_count=2
status_d2h_copy_call_count=1
output_d2h_copy_call_count=1
```

The Python validator incorrectly expected the native v5 offline-monitor
receipt (`control_d2h_bytes=4`, six auxiliary CUDA kernels, 200 parameter
bytes, four memsets). The selected v7 ABI uses the already implemented lean
online monitor: validation is fused into the generated execution path, its
fixed control contains three U32 fields, and no auxiliary status/reduction
kernels are launched. These observed values match the independently existing
v7 contract in `src/rtdsl/v4_rtdlexe.py`.

Repair scope is limited to binding the host validator and fault-injection
fixtures to the actual v7 receipt contract. The workload, samples, cache
policy, correctness oracle, native library, and Goal5842 V12 evidence remain
unchanged.
