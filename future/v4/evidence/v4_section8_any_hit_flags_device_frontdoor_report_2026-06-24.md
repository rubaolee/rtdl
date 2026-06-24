# V4 Section 8 Any-Hit Flags Device-Array Front Door

Date: 2026-06-24
Status: measured V4 development evidence, not a V4 release authorization

## What Was Validated

This run validates the third V4 Tier-2 device-array surface:

`v4_ray_triangle_any_hit_flags_2d_device_arrays`

The surface accepts caller-owned Torch CUDA triangle columns, triangle AABBs,
ray columns, and output flag columns. RTDL invokes the generic OptiX any-hit
primitive and writes one `uint32` hit/no-hit flag per ray into caller-owned GPU
memory.

## POD Result

Source JSON:

`future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json`

Parameters:

- Partner: Torch CUDA
- Warmup: 1
- Repeat: 5
- Ray/triangle counts: 8,192; 32,768; 131,072

| Rays | Triangles | Correct | V4 direct device-array median |
|---:|---:|:---:|---:|
| 8,192 | 8,192 | yes | 0.000261s |
| 32,768 | 32,768 | yes | 0.000282s |
| 131,072 | 131,072 | yes | 0.000288s |

The 8,192-row run also measured a fixture-analytic Torch device reference on
the same generated data. That reference median was 0.002446s, giving a 9.379x
ratio for this fixture. This is not a handwritten OptiX ceiling and not a broad
V4 speedup claim.

## Boundary Metadata

The measured route records:

- `native_direct_device_output_columns: true`
- `ray_results_downloaded_to_host_in_hot_path: false`
- `host_materialization_in_hot_path: false`
- `transfer_mode: device_ray_triangle_columns_output_flags_zero_copy`
- `true_zero_copy_authorized: true` for this internal measured device-column handoff

Still not authorized:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX wording
- CuPy performance claims

## Example

The user-facing example also ran on the POD and passed correctness:

`future/v4/evidence/v4_any_hit_flags_torch_device_arrays_example_result_2026-06-24.json`

