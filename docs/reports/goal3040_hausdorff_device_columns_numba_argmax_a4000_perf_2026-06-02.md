# Goal3040 - Hausdorff Device Columns plus Numba Argmax A4000 Timing

Date: 2026-06-02

## Purpose

Goal3040 measures the Goal3039 Hausdorff strategy on the RTX A4000 pod against
the current CuPy grouped-grid reference and the existing adaptive raw RT path.

This is same-value evidence only. It does not authorize public speedup wording.

## Environment

- Pod: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000, driver 580.159.03
- CUDA: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`
- Source commit: `1b455947a4d58ea371b2821779a0ca63648b49fd`
- Source dirty state: `[]`
- Numba CUDA binding: `NUMBA_CUDA_USE_NVIDIA_BINDING=1`
- Minor-version compatibility: disabled

Focused source validation passed on the pod:

```text
Ran 4 tests in 0.010s

OK
```

## Results

All rows matched the CuPy grouped-grid exact Hausdorff distance.

| Points per side | CuPy grouped-grid (s) | Adaptive raw RT (s) | Device columns + Numba argmax (s) | Device-column ratio vs CuPy |
| ---: | ---: | ---: | ---: | ---: |
| 2,048 | 0.002541 | 0.527363 | 1.362789 | 536.328x slower |
| 4,096 | 0.004778 | 0.052364 | 0.732571 | 153.308x slower |
| 8,192 | 0.008906 | 0.173520 | 0.676493 | 75.961x slower |

The full artifact is:

`docs/reports/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.json`

## Interpretation

The new composition is correct and confirms that RTDL can wire:

`OptiX RT traversal -> CuPy device columns -> Numba partner reduction`

as an app-level strategy. But the timing shows this is not the right performance
path for dense exact Hausdorff on this dataset family.

The weakness is structural:

- The strategy still writes one nearest-witness row per query in both
  directions.
- It then launches a small global reduction over only one score column.
- It does not keep X-HD-style active-set pruning or candidate-frontier logic
  resident on the device.
- The Numba reducer sees low occupancy at these row counts.

So the next performance step is not another wrapper around full witness columns.
The next primitive needs to keep the active set/candidate frontier and witness
selection device-resident, so the RT path avoids producing work for points that
cannot improve the directed Hausdorff maximum.

## Claim Boundary

Goal3040 does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- app-specific native-engine behavior

It is a negative but useful performance result.
