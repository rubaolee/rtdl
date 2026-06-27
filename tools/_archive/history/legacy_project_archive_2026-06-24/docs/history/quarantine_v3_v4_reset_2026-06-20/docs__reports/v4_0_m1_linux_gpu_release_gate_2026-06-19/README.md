# RTDL V4.0 M1 Linux GPU Release Gate Artifacts

Status: current-head Linux GPU M1 release evidence gate passed for commit
`d99945e980b6c76baf9c5a0ec5f0ac5965c873ae`.

Host: `192.168.1.20` / `lx1`.

GPU: NVIDIA GeForce GTX 1070, compute capability 6.1.

This directory contains the child artifacts used by the aggregate gate report:

- `../v4_0_m1_linux_gpu_release_gate_2026-06-19.json` - aggregate gate report.
- `source_tree_runtime_preflight.json` - required runtime dependency and source-tree preflight.
- `cupy_stream_smoke.json` - CuPy caller-stream pointer/stream smoke.
- `cupy_no_host_stage.json` - transfer-counter no-host-stage probe for named CUDA columns.
- `cupy_stream_ordering.json` - same-stream and fixed-radius M1 prepare/query event-wait ordering probe.
- `numba_partner_surface.json` - bounded Numba `DeviceNDArray` M1 route probe.
- `dlpack_capsule.json` - bounded legacy DLPack capsule M1 route probe.
- `pytorch_cuda_tensor.json` - bounded PyTorch CUDA tensor M1 compatibility probe.
- `cupy_benchmark.json` - 262,144-row route-scoped benchmark probe against a simple CuPy baseline.
- `claim_boundary_scan.json` - current front-door claim scan.

The gate authorizes only the bounded fixed-radius M1 Python GPU operator
evidence: caller-owned CUDA columns in, RTDL/OptiX route, caller-owned CUDA
columns/tensors out.

It does not authorize V4.0 as the current front door, package/PyPI/wheel/stable
SDK wording, public true-zero-copy wording, async completion, public speedup,
RTX/RT-core speedup, or full PyTorch/Numba/DLPack surface claims.
