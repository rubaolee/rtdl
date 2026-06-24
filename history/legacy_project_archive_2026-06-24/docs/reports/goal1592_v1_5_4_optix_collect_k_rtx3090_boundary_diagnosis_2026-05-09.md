# Goal 1592: RTX 3090 Collect-K Boundary Diagnosis

## Verdict

The RTX 3090 boundary diagnosis supports a narrower interpretation of the candidate preset: it is most reliable at counts that cross payload-copy or segment-boundary transitions, especially `49153+`, `65537+`, and `69632+`. It does not support enabling the candidate preset broadly for all counts, and it does not authorize public speedup wording.

## Environment

- Host: `root@213.192.2.74 -p 40053`
- Checkout: `/root/work/rtdl_rtx3090`
- Commit: `0b6178a9ccbd3f11d1776ed5e4ad7440cad9b775`
- GPU: `NVIDIA GeForce RTX 3090`
- Driver: `580.126.20`
- CUDA toolkit: `/usr/local/cuda-12.4`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Runtime library path: `/usr/local/cuda-12.4/lib64`
- Architecture override: `RTDL_OPTIX_PTX_ARCH=compute_86`

## Scope

The accepted comparison is the same-contract optimized profile baseline versus `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`.

Baseline environment:

```bash
RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1
RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1
RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1
RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1
RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1
RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1
RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1
RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1
```

Candidate environment:

```bash
RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1
```

An earlier raw-default baseline sweep produced huge apparent speedups, but it is discarded because it did not use the same optimized baseline contract as Goal1586.

## Three-Round Boundary Summary

Negative delta means the candidate preset is faster than the optimized baseline.

| Candidate count | Avg delta ms | Faster rounds | Min delta ms | Max delta ms | Payload-copy change |
|---:|---:|---:|---:|---:|---|
| 49152 | -0.003374 | 2/3 | -0.008940 | 0.001309 | 1 -> 0 |
| 49153 | -0.006506 | 3/3 | -0.008999 | -0.001940 | 3 -> 1 |
| 49154 | -0.008970 | 3/3 | -0.016990 | -0.003380 | 3 -> 1 |
| 65535 | 0.001427 | 1/3 | -0.002310 | 0.004061 | 0 -> 0 |
| 65536 | -0.002940 | 3/3 | -0.004380 | -0.001949 | 0 -> 0 |
| 65537 | -0.022634 | 3/3 | -0.026421 | -0.020700 | 5 -> 0 |
| 65538 | -0.011660 | 2/3 | -0.024220 | 0.006409 | 5 -> 0 |
| 65552 | -0.013730 | 3/3 | -0.028081 | -0.005649 | 5 -> 0 |
| 69632 | -0.012973 | 3/3 | -0.017160 | -0.009150 | 4 -> 0 |
| 69633 | -0.010274 | 3/3 | -0.014870 | -0.006241 | 4 -> 1 |

All accepted profile artifacts reported parity pass and expected topology.

## Interpretation

The strongest signal is where the candidate preset eliminates several carry payload copies:

- `49153` and `49154`: payload copies drop from `3` to `1`, and all three rounds are faster.
- `65537`, `65552`, and `69632`: payload copies drop from `5` or `4` to `0`, and all three rounds are faster.
- `69633`: payload copies drop from `4` to `1`, and all three rounds are faster.

The weaker signal is where there are no payload-copy savings:

- `65535`: no payload-copy change and slower on average.
- `65536`: no payload-copy change but slightly faster in all rounds; the gain is small enough that it should remain a candidate observation, not a promotion rule by itself.

## Direction

The next implementation direction should be gated candidate enablement around the demonstrated transition regions rather than broad default promotion. A conservative next gate would prioritize counts with measured payload-copy reduction, for example `49153+` and `65537+` within the currently validated collect-k tiled path, then revalidate on RTX 3090 plus one Ada GPU before changing any default behavior.

## Claim Boundary

This is internal v1.5.4 experimental evidence only. It does not promote `COLLECT_K_BOUNDED`, does not change defaults, does not authorize public speedup wording, and does not publish a release.
