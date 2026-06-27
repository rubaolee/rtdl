# Goal3866 RayJoin Representative Scale Profile

Date: 2026-06-08

Status: implemented and A5000-validated.

## Purpose

The current ten-app scale registry represented `spatial_rayjoin` with a short
prepared OptiX PIP-only count over the tiny in-repo fixture. That row stayed
green, but it did not match the stronger RayJoin evidence already produced by
Goals3833, 3834, 3838, and 3842.

Goal3866 replaces that narrow row with a representative mixed route over the
bounded public-CDB slices:

- PIP one-shot scalar count: Numba CUDA JIT, no CuPy RawKernel required.
- PIP repeated requests: RTDL/OptiX prepared point/closed-shape batch executor.
- LSI scalar count: RTDL/OptiX prepared segment-pair count, with Numba
  no-RawKernel reference context.
- Overlay active count: RTDL/OptiX prepared shape-pair active count, with Numba
  no-RawKernel reference context.

This keeps user route choice explicit. It does not add automatic dispatch and
does not add app-specific native engine logic.

## What Changed

Added:

- `scripts/goal3866_rayjoin_representative_scale_profile.py`
- `tests/goal3866_rayjoin_representative_scale_profile_test.py`

Updated:

- `src/rtdsl/current_benchmark_scale_profiles.py`

The script redirects inherited progress logs to stderr and emits one clean JSON
payload to stdout, so the existing file-backed scale-profile runner can parse it
without special handling.

## Expected A5000 Command

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal3866_rayjoin_representative_scale_profile.py \
  --repeat 50 \
  --warmup 5 \
  --pip-batch-single-repeat 12 \
  --pip-batch-repeat 8 \
  --pip-batch-request-counts 1 100
```

The script resolves the public-CDB directory from `RTDL_RAYJOIN_PUBLIC_CDB_DIR`,
`/root/rtdl_goal3293/data/rayjoin_public_cdb`,
`/root/rtdl/data/rayjoin_public_cdb`, or local `data/` fallbacks. The PIP
batch leg sets the Goal3842 public-CDB predicate epsilon (`1e-9`) so the
device-filtered inclusive count remains exact at `1417`.

## A5000 Result

Artifact:

`docs/reports/goal3866_rayjoin_representative_scale_profile_a5000/summary.json`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Commit:

`d598ed59`

Git status inside the measured clean checkout:

empty.

All counted contracts matched: `all_counts_match: true`.

| Contract | Numba median sec | RTDL/OptiX median sec | RTDL/OptiX vs Numba | Recommended route |
| --- | ---: | ---: | ---: | --- |
| PIP one-shot scalar count | `0.000513652` | `0.002453625` | `0.209x` | Numba CUDA JIT scalar count |
| LSI scalar count | `0.020609465` | `0.000090068` | `228.822x` | RTDL/OptiX prepared segment-pair count |
| Overlay active count | `0.048837483` | `0.000208054` | `234.734x` | RTDL/OptiX prepared shape-pair active count |

PIP repeated-request throughput through the RTDL/OptiX prepared batch executor:

| Request count | Median ms/request |
| ---: | ---: |
| `100` | `0.024185` |

## Interpretation

The current RayJoin benchmark app should not be summarized as one PIP-only row.
The correct reader-facing status is mixed and explicit:

- one-shot bounded public-CDB PIP is still best represented by the no-RawKernel
  Numba reference route;
- repeated PIP requests use the RTDL/OptiX prepared batch executor;
- LSI and overlay active-count are strongly RTDL/OptiX-favorable;
- route choice remains visible and user-controlled.

## Boundary

Goal3866 does not authorize release action, public speedup wording, whole-app
RayJoin speedup wording, broad RT-core wording, RayJoin paper-reproduction
wording, true-zero-copy wording, automatic partner selection, or app-specific
native-engine logic.
