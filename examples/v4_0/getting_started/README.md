# V4.0 Getting Started Examples

Status: experimental V4.0 source-tree examples.

| File | Purpose |
| --- | --- |
| `v4_fixed_radius_cupy_hello.py` | smallest CuPy-owned CUDA column route |
| `v4_fixed_radius_numba_hello.py` | same route with Numba `DeviceNDArray` columns |
| `v4_fixed_radius_pytorch_hello.py` | same route with detached contiguous PyTorch CUDA tensors |

All three examples print JSON and keep claim-boundary flags in the output.
They are not package-install examples and not speedup examples.
