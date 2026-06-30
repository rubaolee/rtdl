# Goal3833: RayJoin Public-CDB Repeat-200 Current-Head Refresh

Date: 2026-06-07

Status: implemented and A5000-validated.

## Purpose

Goal3832 showed that the tiny default RayJoin PIP row is not a meaningful
stress row. Goal3833 refreshes the existing public-CDB same-contract RayJoin
probe on the current commit, using the Goal3593 harness with repeat-200 timing.

The question is narrow:

> On bounded public CDB slices, which user-visible route should a RayJoin-style
> reference implementation choose for PIP, LSI, and overlay active-count
> contracts?

This is not a RayJoin paper reproduction and not a public speedup claim.

## Artifact

`docs/reports/goal3833_rayjoin_public_cdb_repeat200_current_a5000/summary.json`

Pod commit:

`5cdb1cb5`

Command:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py \
  --data-dir /root/rtdl_goal3293/data/rayjoin_public_cdb \
  --cases all \
  --repeat 200 \
  --warmup 5 \
  --output docs/reports/goal3833_rayjoin_public_cdb_repeat200_current_a5000/summary.json
```

## Results

| Case | Count | CuPy median sec | CuPy total sec | RTDL/OptiX median sec | RTDL/OptiX total sec | RTDL/OptiX vs CuPy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pip_county512` | 1417 | 0.000435257 | 0.087464832 | 0.002076064 | 0.425690223 | 0.210x |
| `lsi_county512_soil512` | 269 | 0.021157210 | 4.222674809 | 0.000086707 | 0.017541061 | 244.008x |
| `overlay_county512_soil512` | 174 | 0.049669714 | 10.046211018 | 0.000188848 | 0.038203883 | 263.015x |

All counts matched. Minimum RTDL/OptiX-vs-CuPy ratio was `0.210x`; geomean was
`23.785x`.

## Interpretation

This current-head refresh confirms the older Goal3595 direction:

- PIP count remains CuPy-favorable for the bounded public-CDB slice.
- LSI count remains strongly RTDL/OptiX-favorable.
- Overlay active-pair dependency count remains strongly RTDL/OptiX-favorable.

The right RayJoin guidance is therefore mixed-route and explicit:

- recommend CuPy for bounded scalar PIP count on this slice;
- recommend RTDL/OptiX for LSI count and overlay active-count;
- keep route choice visible to the user; do not auto-dispatch or overclaim.

## Next Engineering Target

For RayJoin performance, the next major work is not repeating tiny fixtures. It
is larger public-CDB route evidence and, eventually, a generic exact
point-in-closed-shape count primitive if we want RTDL/OptiX to close the PIP
gap without leaning on CuPy.

## Boundary

Goal3833 does not authorize release action, package-install wording, public
speedup wording, whole-app RayJoin speedup wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is current-head internal route-selection evidence only.
