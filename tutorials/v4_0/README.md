# RTDL V4.0 Experimental Tutorial Track

Status: experimental V4.0 source-tree release-candidate learner path.

This track teaches the V4.0 M1 route without replacing the current v3.0.2
front door. Use it when you specifically want to study the experimental Python
GPU device-array operator path.

```text
CuPy, Numba, or PyTorch owns CUDA arrays.
RTDL borrows those arrays as device columns.
OptiX executes the fixed-radius count/threshold route.
The caller owns the output columns and stream.
```

The only V4.0 user-facing route in this track is
`fixed_radius_count_threshold_2d`. It returns one fixed output row per query:
`query_ids`, `neighbor_counts`, and `threshold_flags`.

## Tutorial Ladder

| Step | Tutorial | Outcome |
| --- | --- | --- |
| 1 | [Source-Tree GPU Setup](01_source_tree_gpu_setup.md) | Build the OptiX runtime and verify the V4 source-tree path. |
| 2 | [CuPy Fixed-Radius Route](02_fixed_radius_cupy.md) | Run the smallest V4 route with caller-owned CuPy input and output columns. |
| 3 | [Numba DeviceArray Route](03_numba_device_array_route.md) | Run the same route through `__cuda_array_interface__` with Numba device arrays. |
| 4 | [PyTorch CUDA Tensor Route](04_pytorch_cuda_tensor_route.md) | Run the same route with detached contiguous PyTorch CUDA tensors. |
| 5 | [Boundaries And Troubleshooting](05_boundaries_and_troubleshooting.md) | Keep claims, missing dependencies, streams, and unsupported cases straight. |

## Runnable Examples

Run examples from the repository root after the V4 source-tree runtime
requirements are present:

```bash
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_cupy_hello.py
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_numba_hello.py
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_pytorch_hello.py
```

These scripts print JSON with observed output columns and claim-boundary flags.

## Required Boundary

This tutorial track does not authorize:

- V4.0 as the current user front door;
- package install, PyPI, wheel, or stable SDK wording;
- public true-zero-copy, async, public speedup, RTX speedup, or RT-core speedup
  wording;
- full PyTorch, full Numba, full DLPack, or non-Python host support.

The current user release remains v3.0.2. V4.0 is an experimental source-tree
release candidate for one Python GPU operator route.

## Review Evidence

- [V4.0 M8 Release-Candidate Evidence Packet](../../docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md)
- [V4.0 Source-Tree Runtime Story](../../docs/engineering/rtdl_v4_0_source_tree_runtime_story_2026-06-19.md)
- [V4.0 Final Validation Bundle](../../docs/reports/v4_0_m8_final_validation_bundle_2026-06-19.json)
