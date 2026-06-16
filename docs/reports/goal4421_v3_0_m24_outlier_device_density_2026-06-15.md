# Goal4421 / V3.0 M24 Outlier device-density bridge

Status: `accept-with-boundary`

M24 carries the existing generic prepared OptiX fixed-radius count-threshold device-column front door into the current outlier detection app. The new app backend is `optix_device_density`: RTDL/OptiX prepares the 2D point scene from caller-owned partner device columns, writes per-query `query_ids`, `neighbor_counts`, and `threshold_flags` back into partner-owned device columns, and the app converts those generic columns into outlier density rows only after the measured hot window.

This is an internal V3 integration step, not a public speedup claim.

## What Changed

| Piece | Result |
|---|---|
| App backend | `optix_device_density` in `rtdl_outlier_detection_app.py`. |
| RTDL primitive | `prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene` plus `fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns`. |
| Partners | CuPy and Numba: CuPy as the practical CUDA partner and Numba as the no-C++/no-RawKernel reference. |
| Generic adapter | The 2D prepared fixed-radius device-column output allocator now supports Numba-owned CUDA arrays. |
| App logic | Outlier labels, sorted app rows, oracle comparison, and JSON materialization stay in the app layer. |
| Boundary | This is not an outlier-specific native engine ABI, hidden partner choice, public speedup claim, or true-zero-copy claim. |

## Pod Evidence

Artifacts:

```text
docs/reports/goal4421_v3_0_m24_outlier_device_density_65536_2026-06-15.json
docs/reports/goal4421_v3_0_m24_outlier_device_density_524288_2026-06-15.json
```

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20 GB.

Commands:

```bash
python scripts/v3_0_m24_outlier_device_density_measure.py \
  --copies 8192 \
  --warmups 2 \
  --repeats 5 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4421_v3_0_m24_outlier_device_density_65536_2026-06-15.json

python scripts/v3_0_m24_outlier_device_density_measure.py \
  --copies 65536 \
  --warmups 1 \
  --repeats 3 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4421_v3_0_m24_outlier_device_density_524288_2026-06-15.json
```

| Points | Partner | Hot device-density median | Post-window row materialization | Prepare | Input column build | Oracle | Outliers |
|---:|---|---:|---:|---:|---:|---|---:|
| 65,536 | CuPy | 0.000268s | 0.077101s | 0.985567s | 0.352572s | matched | 16,384 |
| 65,536 | Numba | 0.000585s | 0.086364s | 0.002673s | 0.213260s | matched | 16,384 |
| 524,288 | CuPy | 0.000401s | 0.355653s | 1.006484s | 0.505336s | matched | 131,072 |
| 524,288 | Numba | 0.000837s | 0.345284s | 0.004487s | 0.388795s | matched | 131,072 |

Both scale rows passed:

```text
all_match_oracle: true
outlier_counts_match: true
inlier_counts_match: true
native_continuation_active: true
rt_core_accelerated: true
public_claim_authorized: false
```

Prepare timing is included for transparency, but not used as a CuPy-vs-Numba partner comparison: the runner executes CuPy first and Numba second in one process, so native initialization and cache effects are order-sensitive. The prepared hot-window rows are the cleanest measurement of the repeated device-column query operation.

## Interpretation

The outlier app now has a real RTDL+partner route for full per-point density labels without materializing fixed-radius neighbor rows. The prepared OptiX hot path writes only the generic count/threshold columns needed by the app. On the tiled workload, that prepared device-column operation is sub-millisecond at both 65,536 and 524,288 points. The visible app cost is now the deliberately post-window Python row materialization required to emit the traditional per-point density row schema.

This is the intended V3 lesson for this app: RTDL can keep the RT-heavy density predicate in the generic native/partner path, but public performance wording must distinguish device work from host JSON-row construction. If a downstream app can consume compact device columns directly, it should avoid materializing every per-point row in Python.

## Allowed Wording

The outlier detection app now has an internal V3 route that uses the generic RTDL/OptiX prepared fixed-radius count-threshold device-column front door and explicit CuPy or Numba partner columns to produce per-point outlier density rows.

## Forbidden Wording

Do not claim public speedup, broad RT-core superiority, whole-app acceleration, true zero-copy, automatic partner selection, or an outlier-specific native engine implementation from this milestone.
