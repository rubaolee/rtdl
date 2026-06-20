# RTDL V4.0.0 Support Matrix

Status: released support boundary for `v4.0.0`.

| Area | V4.0.0 support reading |
| --- | --- |
| Product surface | Python GPU device-array operator lane. |
| Released route | `fixed_radius_count_threshold_2d` only. |
| Backend | OptiX-backed source-tree runtime via `build/librtdl_optix.so`. |
| Inputs | CuPy CUDA arrays, Numba `DeviceNDArray`, detached contiguous PyTorch CUDA tensors for the exact route. |
| Outputs | Caller-owned fixed-size CUDA columns: `query_ids`, `neighbor_counts`, `threshold_flags`. |
| Streams | Caller stream propagation and fixed-radius prepare/query event ordering validated; native calls synchronize before return. |
| DLPack | Narrow legacy capsule evidence for the fixed-radius route; no full framework-neutral DLPack surface. |
| Packaging | Source tree and editable checkout hygiene only; no PyPI, wheel, or stable SDK. |
| C ABI | Active Phase 2 substrate remains experimental and is not the V4.0 public product. |
| Performance | 262,144-row route benchmark evidence exists; public speedup and RT-core speedup wording remain blocked. |
| V3 surface | Previous V3.0.2 benchmark-app and primitive/prepared docs remain available. |
