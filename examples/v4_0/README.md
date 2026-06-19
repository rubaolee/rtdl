# RTDL V4.0 Experimental Examples

Status: experimental V4.0 source-tree release-candidate examples.

These examples are for the V4.0 M1 Python GPU device-array operator route. They
do not replace `examples/current/`, which remains the learner-facing v3.0.2
example tree for the current user release.

## Start Here

| Example | Command |
| --- | --- |
| CuPy fixed-radius hello | `PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_cupy_hello.py` |
| Numba DeviceArray fixed-radius hello | `PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_numba_hello.py` |
| PyTorch CUDA tensor fixed-radius hello | `PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_pytorch_hello.py` |

## Boundary

These examples are source-tree examples only. They do not authorize package
install, PyPI, wheel, stable SDK, public true-zero-copy, async, public speedup,
RT-core speedup, or full framework-surface claims.

Read the paired tutorial track at [RTDL V4.0 Experimental Tutorial Track](../../tutorials/v4_0/README.md).
