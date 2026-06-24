# Goal4419 / V3.0 M22 Hausdorff app device bridge

Status: `accept-with-boundary`

M22 carries the M21 app-agnostic bridge into the promoted Hausdorff/XHD benchmark app. The new app mode is `--backend optix_device_max_nearest`: RTDL/OptiX produces nearest-witness device columns from device query columns, then the selected partner performs a generic device-side global max reduction before compact materialization.

This is not a public speedup claim. It is benchmark-app integration evidence for the V3 device-continuation contract.

## What Changed

| Piece | Result |
|---|---|
| App mode | `optix_device_max_nearest` in `rtdl_hausdorff_distance_app.py`. |
| RTDL primitive | generic prepared point-group nearest-witness with caller-owned device query columns. |
| Partner rows | CuPy as the practical best CUDA partner, Numba as the no-C++/no-RawKernel reference. |
| App logic | Hausdorff direction selection and oracle validation remain app/Python logic. |
| Boundary | No app-specific native OptiX symbol or custom Hausdorff native callback was added. |

## Pod Evidence

Artifact: `docs/reports/goal4419_v3_0_m22_hausdorff_device_bridge_65536_2026-06-15.json`

Hardware: RTX 4000 Ada pod, driver 550 path. Workload: 16,384 tiled copies, 65,536 points per set, two directed Hausdorff passes, radius 0.4, 2 warmups, 5 repeats.

Command:

```bash
python scripts/v3_0_m22_hausdorff_device_bridge_measure.py \
  --copies 16384 \
  --radius 0.4 \
  --warmups 2 \
  --repeats 5 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4419_v3_0_m22_hausdorff_device_bridge_65536_2026-06-15.json
```

| Partner | Points per set | Directed hot median sum | Materialize median sum | Oracle | Boundary |
|---|---:|---:|---:|---|---|
| CuPy | 65,536 | 0.002885s | 0.000157s | matched, distance 0.299999952 | internal only |
| Numba | 65,536 | 0.004442s | 0.000328s | matched, distance 0.299999952 | internal only |

Preparation is separate from the hot device window. The two directed scene/query preparations summed to 1.067845s for the CuPy row and 0.560475s for the Numba row. Both directions used 65,536 point groups, one small group per authored tile, so the RT traversal workload is exact for the tiled fixture rather than a dense all-pairs partner-only computation.

## Interpretation

M22 is the first app-level consumer of M21. It proves that the Hausdorff app can stop choosing between a scalar threshold decision and dense partner-only exact witnesses: it now has a third route where RTDL owns the RT traversal and partner code owns the explicit device continuation. The required partner evidence covers both CuPy and Numba.

The result is a better architectural row, not a public performance row: RTDL/OptiX is doing the nearest-witness RT traversal, while the partner performs a tiny global max continuation over device-resident nearest distances. CuPy is the faster practical partner; Numba preserves the no-C++/no-RawKernel user path at the same contract.

Allowed wording: the Hausdorff app has an internal V3 route that uses RTDL/OptiX nearest-witness device columns plus CuPy/Numba device-side max reduction.

Forbidden wording: public speedup, whole-app speedup, RT-core efficiency parity, paper parity, automatic partner selection, or true-zero-copy public claims.
