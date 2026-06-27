# Goal1823 - OptiX Partner Device-Ray Columns Partial ABI

## Status

`accept-with-boundary`

Goal1823 adds the first native OptiX execution step after the Goal1819/Goal1821
descriptor-only work. The new path accepts partner-owned CUDA ray columns,
packs them on GPU into RTDL's internal OptiX ray layout, and executes the
existing prepared-scene any-hit counter.

This is intentionally a partial bridge:

- Ray inputs are device-column descriptors from PyTorch/CuPy-style partners.
- Rays are not copied through host memory on this path.
- Rays are packed into an RTDL-owned GPU buffer before OptiX traversal.
- The triangle scene still uses the existing prepared OptiX scene path.
- True zero-copy, arbitrary partner acceleration, whole-app acceleration, and
  broad RT-core speedup claims remain blocked.

## Native ABI

New native export:

```text
rtdl_optix_count_prepared_ray_anyhit_2d_device_rays
```

The ABI is generic primitive terminology: prepared ray/primitive any-hit over
device ray columns. It does not contain application-specific names.

Input columns:

- `ids`: CUDA `uint32`
- `ox`, `oy`, `dx`, `dy`, `tmax`: CUDA `float64`

The native layer launches a small CUDA packing kernel named
`pack_ray2d_device_columns`, then reuses the existing
`count_prepared_ray_anyhit_2d_gpu_optix` traversal path.

## Python API

New public helper:

```python
pack_optix_ray_any_hit_2d_device_ray_inputs(ray_columns)
```

New prepared-scene method:

```python
PreparedOptixRayTriangleAnyHit2D.count_device_rays(ray_columns)
```

The Python layer validates that all ray columns are one-dimensional,
contiguous, on the same CUDA device, and have the exact dtype contract needed
by the native packing kernel.

## Claim Boundary

Allowed wording:

```text
RTDL has a partial OptiX partner path that can execute from partner-owned CUDA
ray columns against an already prepared OptiX scene, with GPU-side ray packing.
```

Blocked wording:

```text
RTDL v2.0 is released.
RTDL has true zero-copy partner execution.
RTDL has full direct device-pointer handoff for both rays and triangles.
RTDL has broad RT-core speedup evidence for arbitrary PyTorch/CuPy programs.
```

## Validation

Local Python validation covers:

- descriptor packing metadata and claim flags,
- dtype, shape, contiguity, and device mismatch rejection,
- fail-closed behavior when the native symbol is unavailable,
- successful Python call wiring when a fake native symbol is present,
- native source/prototype/report evidence.

Local Linux validation on `192.168.1.20` covered:

- applying the patch to a clean `origin/main` checkout,
- running the Goal1823 and Goal1821 focused tests,
- building `build/librtdl_optix.so` with
  `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`,
- confirming the exported symbol with
  `nm -D build/librtdl_optix.so`.

RTX hardware validation is still pending. The local Linux build is compile/smoke
evidence only; release evidence still requires an RTX-class pod run.
