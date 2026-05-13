# OptiX Partner Zero-Copy Any-Hit Preview

This advanced tutorial shows the current v2.0 partner zero-copy preview shape
for one primitive. It is the first documented Torch/CuPy CUDA input-plus-output
zero-copy slice:

```text
Torch/CuPy CUDA columns -> RTDL direct device handoff -> OptiX prepared
2-D ray/triangle ANY_HIT -> Torch/CuPy CUDA output flags
```

This is not the v2.0 release. It is a measured preview slice for the OptiX
prepared 2-D ray/triangle any-hit primitive.

## What This Path Proves

For this exact primitive, RTDL can:

- read partner-owned CUDA ray columns;
- read partner-owned CUDA triangle columns;
- build OptiX GAS from a partner-owned CUDA AABB tensor;
- write one `uint32` any-hit flag per ray into a partner-owned CUDA output
  vector.

The RTX A4500 pod artifacts for Goal1838 validated both partners:

| Partner | Output flags | Status |
| --- | --- | --- |
| CuPy CUDA | `[1, 0]` | pass |
| Torch CUDA | `[1, 0]` | pass |

## What You Provide

The ray columns are:

```python
rays = {
    "ids": ...,
    "ox": ...,
    "oy": ...,
    "dx": ...,
    "dy": ...,
    "tmax": ...,
}
```

The triangle columns are:

```python
triangles = {
    "ids": ...,
    "x0": ...,
    "y0": ...,
    "x1": ...,
    "y1": ...,
    "x2": ...,
    "y2": ...,
}
```

The AABB tensor is a contiguous CUDA `float32[N, 6]` matrix in OptiX
`OptixAabb` order:

```text
minX, minY, minZ, maxX, maxY, maxZ
```

The output buffer is a contiguous CUDA `uint32[ray_count]` vector.

## Code Shape

The current public preview API is intentionally explicit:

```python
scene = rt.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
    triangles,
    triangle_aabbs,
)

try:
    result = scene.write_device_any_hit_flags(rays, output_flags)
finally:
    scene.close()
```

`output_flags` remains owned by Torch or CuPy. The returned `result` contains
metadata for the handoff; it is not the data result. Read the CUDA output buffer
with your partner framework when you need to inspect values.

The validation runner used for the pod evidence is:

```bash
PYTHONPATH=src:. python scripts/run_goal1828_optix_device_column_pod_validation.py \
  --partner cupy \
  --goal Goal1838 \
  --output-flags \
  --output docs/reports/goal1838_optix_partner_owned_output_flags_pod_validation.json
```

Use `--partner torch` for the PyTorch version.

## Boundaries

This path authorizes only the exact measured claim:

```text
OptiX prepared 2-D ray/triangle any-hit can read Torch/CuPy CUDA input columns
and write Torch/CuPy CUDA output flags without RTDL-owned input or output
staging buffers.
```

It does not authorize:

- v2.0 release readiness;
- broad RT-core speedup;
- whole-app acceleration;
- arbitrary PyTorch/CuPy acceleration;
- package-install support;
- a claim that OptiX creates no native acceleration state.

OptiX still creates native GAS state. The zero-copy claim applies to the
partner-owned input and output buffers for this primitive path.

## Read The Evidence

- [Goal1834 whole-primitive input zero-copy](../reports/goal1834_optix_whole_primitive_input_zero_copy_2026-05-13.md)
- [Goal1836 CuPy input conformance](../reports/goal1836_optix_cupy_whole_primitive_input_zero_copy_conformance_2026-05-13.md)
- [Goal1838 partner-owned output flags](../reports/goal1838_optix_partner_owned_output_flags_zero_copy_2026-05-13.md)
- [Goal1840 v2.0 progress packet](../reports/goal1840_v2_0_progress_so_far_external_review_packet_2026-05-13.md)
