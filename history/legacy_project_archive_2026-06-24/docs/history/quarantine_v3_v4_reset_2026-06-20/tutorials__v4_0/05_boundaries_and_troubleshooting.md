# Boundaries And Troubleshooting

Status: current V4.0.0 source-tree tutorial.

## What V4.0 M1 Is

V4.0 M1 is one current Python GPU operator route:

`fixed_radius_count_threshold_2d`

It proves the direction "caller framework arrays in, RTDL/OptiX route, caller
framework arrays out" for CuPy, Numba, and PyTorch evidence-backed inputs.

## What V4.0 M1 Is Not

It is not:

- a package install, PyPI, wheel, or stable SDK release;
- a public true-zero-copy claim;
- async or nonblocking completion;
- public speedup, RTX speedup, or RT-core speedup evidence;
- a full PyTorch, Numba, DLPack, JAX, C++, or Rust surface.

## Common Failures

Missing native library:

```text
build/librtdl_optix.so not found
```

Run:

```bash
make build-optix
```

Missing GPU framework:

```text
CuPy, Numba CUDA, or PyTorch CUDA is not available
```

Install the framework in your source-tree environment. This installs a Python
dependency; it does not install RTDL as a released package.

Bad input column:

```text
missing V4 query columns
V4 query column 'x' must use dtype float64
V4 query columns must live on the same CUDA device
```

Keep the contract exact: one-dimensional CUDA columns named `ids`, `x`, and `y`
with supported dtypes and one CUDA device per invocation.

Unexpected performance result:

Do not turn one local timing into public speedup wording. The V4.0 M1 benchmark
probe is route-scoped evidence only.

## Evidence Links

- [M8 evidence packet](../../docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md)
- [Final validation bundle](../../docs/reports/v4_0_m8_final_validation_bundle_2026-06-19.json)
- [Current claim boundaries](../../docs/learn/current_claim_boundaries.md)
