# Goal3835 RT-DBSCAN Numba Partner Refresh

Date: 2026-06-08

Status: internal current-head A5000 evidence.

## Purpose

The project requirement is that benchmark apps needing custom continuation
logic should not force users into CuPy RawKernel code. RT-DBSCAN already had
Numba prepared-grid and OptiX+Numba paths. Goal3835 refreshes current-head
A5000 evidence to check whether those paths are actually competitive.

This is not a new DBSCAN-specific native engine feature. The native side stays
generic: fixed-radius count-threshold/core-flag columns plus generic component
continuation.

## Evidence

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`05fb798c`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Commands used the existing repeat probe:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal2403_rt_dbscan_repeat_probe.py \
  --dataset clustered3d \
  --point-count 65536 \
  --repeat-count 10 \
  --mode partner_cupy_prepared_grid_components_3d \
  --mode partner_numba_prepared_grid_components_3d \
  --mode optix_rt_core_flags_cupy_prepared_grid_components_3d \
  --mode optix_rt_core_flags_numba_prepared_grid_components_3d
```

The same command was repeated at `--point-count 131072 --repeat-count 5`.

The repeat probe intentionally reports warm/steady behavior without a separate
warm-up phase. The 65,536-point Numba prepared-grid route includes a visible
first-use CUDA JIT cost before settling into the reported median; users should
expect that one-time compile cost on first execution.

Artifacts:

- `docs/reports/goal3835_rt_dbscan_numba_partner_refresh_a5000/summary.json`
- `docs/reports/goal3835_rt_dbscan_numba_partner_refresh_a5000_131k/summary.json`

Both artifacts report `signatures_match: true`.

## Results

| Point count | Route | Partner | Median seconds | Repeats | Signature parity |
| ---: | --- | --- | ---: | ---: | --- |
| 65,536 | prepared grid components | CuPy | 0.460022 | 10 | true |
| 65,536 | prepared grid components | Numba | 0.413086 | 10 | true |
| 65,536 | OptiX RT core flags + prepared grid components | CuPy | 0.388716 | 10 | true |
| 65,536 | OptiX RT core flags + prepared grid components | Numba | 0.340499 | 10 | true |
| 131,072 | prepared grid components | CuPy | 1.522646 | 5 | true |
| 131,072 | prepared grid components | Numba | 1.375083 | 5 | true |
| 131,072 | OptiX RT core flags + prepared grid components | CuPy | 1.008722 | 5 | true |
| 131,072 | OptiX RT core flags + prepared grid components | Numba | 0.913704 | 5 | true |

Relative speedups:

| Point count | Numba prepared grid vs CuPy prepared grid | OptiX+Numba vs OptiX+CuPy |
| ---: | ---: | ---: |
| 65,536 | 1.114x | 1.142x |
| 131,072 | 1.107x | 1.104x |

## Interpretation

RT-DBSCAN satisfies the current partner-choice requirement better than RayJoin
PIP:

- a Numba route exists;
- it uses Python + Numba CUDA JIT rather than CuPy RawKernel code;
- it preserves signature parity with the comparable CuPy paths;
- it is faster than the comparable CuPy prepared-grid continuation at both
  tested scales;
- the OptiX+Numba composition is the best tested path in this four-route packet.

This makes the RT-DBSCAN current recommendation:

```text
Use RTDL/OptiX fixed-radius core flags plus the prepared Numba grid component
continuation when CUDA + Numba is available.
```

CuPy remains useful as an opponent/baseline and as a mature CUDA-array partner,
but it is not the recommended reference implementation for this specific
current RT-DBSCAN prepared-grid continuation.

## Claim Boundary

This report does not authorize:

- release action;
- public speedup wording;
- RT-DBSCAN paper reproduction claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- automatic partner selection.

It is internal current-head evidence that the RT-DBSCAN benchmark app has a
high-performance Numba reference route for the current prepared-grid component
continuation contract.
