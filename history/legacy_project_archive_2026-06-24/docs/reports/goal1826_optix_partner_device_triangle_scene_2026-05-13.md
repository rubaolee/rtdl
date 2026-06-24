# Goal1826 - OptiX Partner Device-Triangle Scene Preparation

## Status

`accept-with-boundary`

Goal1826 extends the Goal1823 device-ray column bridge with partner-owned CUDA
triangle columns. The new path prepares an OptiX any-hit scene from CUDA device
columns without first staging triangle rows through Python/host memory.

This is still not true zero-copy:

- RTDL packs partner triangle columns on GPU into RTDL's internal triangle
  layout.
- RTDL also materializes AABBs for OptiX GAS construction.
- OptiX GAS construction necessarily creates backend-owned acceleration data.
- The path has compile/smoke evidence only until RTX pod validation runs.

## Native ABI

New native export:

```text
rtdl_optix_prepare_ray_anyhit_2d_device_triangles
```

Input columns:

- `ids`: CUDA `uint32`
- `x0`, `y0`, `x1`, `y1`, `x2`, `y2`: CUDA `float64`

The native layer launches `pack_triangle2d_device_columns`, which creates
RTDL-owned `GpuTriangle` and AABB buffers on GPU. The AABB buffer is then used
to build the existing OptiX custom-primitive GAS.

## Python API

New public helper:

```python
pack_optix_ray_any_hit_2d_device_triangle_inputs(triangle_columns)
```

New public prepared-scene constructor:

```python
prepare_optix_ray_triangle_any_hit_2d_device_triangles(triangle_columns)
```

Together with Goal1823:

```python
scene = prepare_optix_ray_triangle_any_hit_2d_device_triangles(triangle_columns)
count = scene.count_device_rays(ray_columns)
```

This is the first Python+partner+RTDL shape where both ray and triangle inputs
can enter OptiX from partner-owned CUDA columns. It remains a GPU-pack and GAS
build path, not a true zero-copy claim.

## Validation

Local validation covers:

- Python descriptor validation and fake native symbol wiring.
- Native source/prototype/report evidence.
- v2 gate wording that still blocks release readiness.

RTX pod validation remains required before this can count as hardware execution
evidence for the strict v2.0 birth gate.
