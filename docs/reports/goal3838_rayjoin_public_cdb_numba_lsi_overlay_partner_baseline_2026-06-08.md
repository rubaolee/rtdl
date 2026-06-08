# Goal3838 RayJoin Numba LSI/Overlay Partner Baseline

Date: 2026-06-08

Status: internal current-head A5000 evidence.

## Purpose

Goal3834 closed the no-RawKernel Numba coverage gap for the public-CDB RayJoin
PIP scalar-count row. Claude's Goal3836 review accepted that work and called out
the remaining partner-coverage debt: LSI and overlay still had CuPy RawKernel
same-contract baselines but no equivalent Numba CUDA JIT route.

Goal3838 adds and measures those two routes:

- LSI segment-intersection scalar count;
- overlay active shape-pair scalar count.

This is partner-coverage work, not a native engine change. The RTDL/OptiX
primitive path remains the recommended route when the scalar-count primitive
already expresses the answer.

## Evidence

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`ae8d19c3`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Command:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py \
  --data-dir /root/rtdl_goal3293/data/rayjoin_public_cdb \
  --repeat 200 \
  --warmup 5 \
  --block-size 128 \
  --output docs/reports/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_a5000/summary.json
```

Artifact:

- `docs/reports/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_a5000/summary.json`

The artifact reports `all_counts_match: true` across Numba, CuPy, and
RTDL/OptiX for both rows.

## Results

| Case | Count | Numba median sec | CuPy median sec | RTDL/OptiX median sec | Numba vs CuPy | RTDL/OptiX vs Numba |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LSI county512/soil512 | 269 | 0.020659 | 0.021114 | 0.000079 | 1.022x | 262.643x |
| Overlay active count county512/soil512 | 174 | 0.048749 | 0.049503 | 0.000189 | 1.015x | 258.081x |

## Interpretation

Goal3838 closes the no-RawKernel partner-coverage gap for RayJoin scalar-count
rows:

- PIP: Goal3834 Numba route exists; CuPy remains faster on the bounded PIP row.
- LSI: Goal3838 Numba route exists and slightly beats the dense CuPy RawKernel
  baseline, but RTDL/OptiX is the clear recommended path.
- Overlay active count: Goal3838 Numba route exists and slightly beats the dense
  CuPy RawKernel baseline, but RTDL/OptiX is again the clear recommended path.

The engineering lesson is important: Numba is now available for users who want
Python-source custom CUDA logic, but the high-performance RTDL story for these
LSI/overlay scalar contracts is not "use partner code." It is "use the fused
generic RTDL/OptiX primitive."

## Claim Boundary

This report does not authorize:

- release action;
- public speedup wording;
- RayJoin paper reproduction claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- automatic partner selection.

It is internal current-head evidence that RayJoin's public-CDB LSI and overlay
scalar-count continuations now have same-contract no-RawKernel Numba routes.
