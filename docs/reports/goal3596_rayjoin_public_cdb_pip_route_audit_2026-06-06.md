# Goal3596 - RayJoin Public-CDB PIP Route Audit

Date: 2026-06-06

Status: internal route-selection audit

## Purpose

Goal3594/Gemini flagged the public-CDB PIP row as the remaining weak row in the Goal3593 evidence packet. Goal3596 audits existing v2.8 PIP routes before adding new implementation work.

The audited dataset is:

- `/root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start256_count512.cdb`

All runs used the clean A5000 checkout at:

- `ca5ae21260e28a0a011e242aa7cbe97d35d8690c`

## Results

| Route | Count | Median Sec | Total Sec | Same Positive-Membership Contract? | Result |
| --- | ---: | ---: | ---: | --- | --- |
| CuPy dense CUDA-core baseline, Goal3595 repeat-200 | 1417 | 0.000437917 | 0.087361970 | yes | fastest |
| RTDL/OptiX exact prepared count, repeat-100 | 1417 | 0.000802434 | 0.080236102 | yes | best RTDL-only route, still slower than CuPy |
| RTDL/OptiX + prepared CuPy refiner, Goal3595 repeat-200 | 1417 | 0.002150856 | 0.438148404 | yes | correct but slower than exact prepared count for scalar PIP |
| `device_filtered_validated` | 1429 vs exact 1417 | n/a | n/a | no | rejected |
| `device_filtered_prepared_points_validated` | 1429 vs exact 1417 | n/a | n/a | no | rejected |
| `point_id_count_device_columns_validated` | 1429 vs exact 1417 | n/a | n/a | no | rejected |
| validated modes with `crossing_only` boundary | 152 vs exact 1417 | n/a | n/a | no | rejected |

Point ordering did not improve the exact prepared route:

| Point order | Count | Median Sec | Total Sec |
| --- | ---: | ---: | ---: |
| `natural` | 1417 | 0.000808804 | 0.080831360 |
| `x_then_y` | 1417 | 0.000865134 | 0.086760972 |
| `y_then_x` | 1417 | 0.000840777 | 0.084037900 |
| `morton_xy` | 1417 | 0.000828597 | 0.082947867 |

The scalar count pipeline environment switch also did not help:

| `RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE` | Count | Median Sec | Total Sec |
| --- | ---: | ---: | ---: |
| unset | 1417 | 0.000802434 | 0.080236102 |
| `0` | 1417 | 0.000808207 | 0.080884392 |
| `1` | 1417 | 0.000812463 | 0.083020771 |

## Interpretation

For this bounded public-CDB PIP count, the best current user-facing route remains CuPy dense CUDA-core count. The best RTDL-only route is the exact prepared OptiX count, which is roughly `1.83x` slower than CuPy but roughly `2.67x` faster than the OptiX-candidate-plus-CuPy-refiner path for scalar count.

The validated fast device-filtered modes are correctly fail-closed for this dataset because they do not match exact positive-membership semantics. They should not be used as a PIP replacement here.

## Engineering Conclusion

No existing v2.8 switch closes the PIP gap. For the RayJoin public-CDB reference guidance:

- recommend CuPy for simple bounded PIP count;
- recommend RTDL/OptiX exact prepared count only when the user specifically wants a no-partner RTDL-only PIP count path;
- reserve the OptiX-candidate-plus-CuPy-refiner route for richer row/candidate workflows, not scalar count-only PIP.

The next real PIP improvement, if this remains a priority for v2.9, is a generic exact point-in-closed-shape count primitive that avoids the current candidate materialization plus exact-refine overhead while preserving boundary semantics. That would be a generic primitive, not a RayJoin-specific native path.

## Boundary

Goal3596 does not authorize release, paper reproduction, broad RT-core speedup, whole-app speedup, automatic dispatch, or zero-copy claims.
