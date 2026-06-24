# Goal3834 RayJoin Public-CDB Numba PIP Partner Baseline

Date: 2026-06-07

Status: internal evidence, accepted locally pending external review.

## Purpose

The RayJoin public-CDB route evidence from Goal3833 showed a mixed result:
RTDL/OptiX was strongly favorable for LSI and overlay active-count rows, while
bounded scalar PIP count was faster in the app-side CuPy RawKernel baseline.

That left a user-facing partner gap. If a user wants custom continuation logic
without writing a CuPy RawKernel string, the project should provide a Numba
reference route for the same-contract path. Goal3834 adds that route for the public
CDB PIP count row.

## What Changed

Added `scripts/goal3834_rayjoin_public_cdb_numba_pip_partner_baseline.py`.

The script implements a Numba CUDA JIT dense all-pairs scalar-count path for
the same-contract PIP path used by the Goal3589/Goal3593 CuPy baseline:

- input: points and closed shapes from `br_county_start256_count512.cdb`;
- output contract: `point_to_shape_positive_hit_count`;
- boundary semantics: same on-edge inclusive rule as the CuPy baseline;
- implementation style: Python + Numba CUDA JIT, no CuPy RawKernel string;
- native engine impact: none.

This is app-side benchmark/user code. It does not add app-specific logic to the
RTDL native engine.

## A5000 Evidence

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`e509112b`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Command:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal3834_rayjoin_public_cdb_numba_pip_partner_baseline.py \
  --data-dir /root/rtdl_goal3293/data/rayjoin_public_cdb \
  --repeat 200 \
  --warmup 5 \
  --output docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_a5000/summary.json
```

Main artifact:

`docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_a5000/summary.json`

## Results

All routes produced the same count: `1417`.

| Route | Partner | Median seconds | Total seconds over 200 repeats | Count | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Numba CUDA JIT dense PIP count | Numba | 0.000514 | 0.103460 | 1417 | Valid no-RawKernel partner route |
| CuPy RawKernel dense PIP count | CuPy | 0.000446 | 0.091241 | 1417 | Still fastest app-side CUDA-core route |
| RTDL/OptiX prepared PIP route | RTDL/OptiX + CuPy refiner | 0.002098 | 0.428390 | 1417 | Correct but not recommended for this bounded scalar PIP row |

Relative ratios:

- CuPy vs Numba: `0.868x` as recorded by the artifact, meaning Numba is about
  `1.15x` slower than CuPy on this row.
- Numba vs RTDL/OptiX: `0.245x` as recorded by the artifact, meaning Numba is
  about `4.08x` faster than the current RTDL/OptiX prepared PIP route for this
  bounded scalar count.

## Block-Size Calibration

The first implementation used the conventional block size 256. A small A5000
sweep over 128/256/512/1024 showed 128 was the fastest of the tested settings.

| Block size | Median seconds | Total seconds over 200 repeats | Count |
| ---: | ---: | ---: | ---: |
| 128 | 0.000514 | 0.104057 | 1417 |
| 256 | 0.000526 | 0.105851 | 1417 |
| 512 | 0.000537 | 0.109204 | 1417 |
| 1024 | 0.000538 | 0.109164 | 1417 |

The script default is therefore 128.

## Interpretation

Goal3834 closes a user-facing partner-coverage gap, not a performance headline.

For the RayJoin PIP scalar-count row:

- users now have a Numba route that avoids CuPy RawKernel code;
- CuPy remains the fastest current app-side CUDA-core route;
- RTDL/OptiX remains correct but not the recommended route for this bounded
  scalar PIP count;
- LSI and overlay active-count remain the RTDL/OptiX-favorable RayJoin rows
  from Goal3833.

This reinforces the route-choice rule: RTDL should provide high-performance
generic primitives, and benchmark apps should show clear recommended routes,
but the runtime must not silently auto-dispatch or hide partner selection from
the user. This is not automatic dispatch.

## Claim Boundary

This report does not authorize:

- release action;
- public speedup wording;
- RayJoin paper reproduction claims;
- RTDL beats RayJoin claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- automatic partner-selection claims.

The result is an internal v2.x benchmark-app hardening step: a no-RawKernel
Numba partner route for RayJoin PIP custom logic.

It is not a RayJoin paper reproduction.
