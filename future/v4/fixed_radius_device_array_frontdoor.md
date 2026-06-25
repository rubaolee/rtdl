# V4 Fixed-Radius Device-Array Front Door

Status: measured V4 surface; final release authorization pending

This page documents the first measured V4 Tier-2 primitive surface:
fixed-radius count-threshold over caller-owned Torch CUDA point columns.

The goal is simple: users who already have GPU arrays should not be forced
through Python `Point` objects or app-shaped density rows. They hand RTDL device
columns, RTDL runs the fused OptiX count-threshold primitive, and the output
columns stay on device.

## API Shape

Use the V4 module surface directly:

```python
import rtdsl.v4_fixed_radius as rt_v4

with rt_v4.prepare_fixed_radius_count_threshold_2d_device_arrays_v4(
    point_columns,
    max_radius=0.35,
    partner="torch",
) as session:
    output_columns = session.allocate_outputs(query_count)
    result = session.run(
        point_columns,
        radius=0.35,
        threshold=3,
        output_columns=output_columns,
        return_metadata=True,
    )
```

Required input columns:

- `ids`: `torch.uint32`, CUDA, contiguous, one-dimensional
- `x`: `torch.float64`, CUDA, contiguous, one-dimensional
- `y`: `torch.float64`, CUDA, contiguous, one-dimensional

Output columns:

- `query_ids`
- `neighbor_counts`
- `threshold_flags`

## Minimal Example

Run the example on a CUDA/OptiX machine:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/path/to/librtdl_optix.so
python examples/v4/fixed_radius_torch_device_arrays.py --copies 8192
```

Dry-run locally without CUDA:

```bash
python examples/v4/fixed_radius_torch_device_arrays.py --dry-run
```

## Evidence

The measured RTX pod result is:

| copies | points | V4 wrapper median | prior Python-facing summary median | Route D rows median | gap reduction |
|---:|---:|---:|---:|---:|---:|
| 8,192 | 65,536 | 0.000278s | 0.284516s | 0.000629s | 1022.93x |
| 32,768 | 262,144 | 0.000311s | 1.193533s | 0.001542s | 3841.66x |
| 131,072 | 1,048,576 | 0.000546s | 5.290915s | 0.004641s | 9699.17x |

Source evidence:

- `future/v4/evidence/v4_section8_device_array_frontdoor_result_2026-06-24.json`
- `future/v4/evidence/v4_section8_device_array_frontdoor_report_2026-06-24.md`
- `future/v4/evidence/v4_fixed_radius_torch_device_arrays_example_result_2026-06-24.json`
- `future/v4/reviews/claude_v4_section8_fixed_radius_wrapper_surface_review_2026-06-24.md`

## Important Boundary

The V4 wrapper route is faster than the Route D row baseline under this
specific boundary because Route D includes host query upload and host row-result
download. The V4 route starts from GPU-resident Torch columns and leaves output
columns on device. This is the intended V4 product contract for GPU-array users,
not a pure kernel-to-kernel comparison.

CuPy is not measured in this evidence packet. The wrapper records Torch as the
measured partner and CuPy as declared but unmeasured.

## Non-Claims

This page does not authorize:

- final V4 release before Goal4642
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX claims
- app-specific native engine claims
- claims that Python `Point` row app routes are now fast
- treating this first primitive as sufficient for V4 release by itself
