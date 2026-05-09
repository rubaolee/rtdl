# Goal 1597: RTX 3090 Threshold-4 Gate Validation

## Verdict

RTX 3090 validation agrees with the RTX 4090 threshold-4 result. The experimental `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1` policy keeps the strongest copy-reduction cases consistently positive and leaves weaker cases gate-off/noise-scale.

This is sufficient cross-architecture internal evidence for the current micro-goal. It does not promote `COLLECT_K_BOUNDED`, does not change default behavior, and does not authorize public speedup wording.

## Environment

- Host: `root@213.192.2.74 -p 40052`
- Checkout: `/root/work/rtdl_rtx3090_threshold4`
- Commit: `8589cf4ecdc617bc628a3ce0d9073eac277c24ea`
- GPU: `NVIDIA GeForce RTX 3090`
- Driver CUDA banner: `13.0`
- CUDA toolkit: `/usr/local/cuda-12.4`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Runtime library path: `/usr/local/cuda-12.4/lib64`
- Architecture override: `RTDL_OPTIX_PTX_ARCH=compute_86`

## Validation

Build:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.4
```

Focused tests:

- `Ran 26 tests`
- `OK`

Measurement:

- Five rounds.
- `31` repeats per case.
- Counts: `65536`, `65537`, `65538`, `65552`, `69632`, `69633`.
- All baseline and gated artifacts reported accepted Goal1506 evidence, parity pass, and expected topology.

## Results

Negative delta means gated mode is faster than the optimized baseline.

| Candidate count | Avg delta ms | Faster rounds | Payload-copy change | Interpretation |
|---:|---:|---:|---|---|
| 65536 | -0.002928 | 3/5 | 0 -> 0 | gate-off, noise-scale |
| 65537 | -0.016960 | 5/5 | 5 -> 0 | gate-on, accepted strong region |
| 65538 | -0.017864 | 5/5 | 5 -> 0 | gate-on, accepted strong region |
| 65552 | -0.014888 | 5/5 | 5 -> 0 | gate-on, accepted strong region |
| 69632 | -0.017704 | 5/5 | 4 -> 0 | gate-on, accepted strong region |
| 69633 | 0.000514 | 3/5 | 4 -> 4 | gate-off, noise-scale |

## Cross-Architecture Interpretation

The RTX 3090 result matches the RTX 4090 threshold-4 result:

- `65537`, `65538`, `65552`, and `69632` are consistently faster on both GPUs.
- `69633` is gate-off and noise-scale on both GPUs.
- `65536` remains a no-copy-reduction sentinel case and should not influence promotion.

This is a good stopping point for GPU switching on this micro-goal. The threshold-4 gated policy is internally validated as experimental. Any next promotion/default-change discussion should move to external review and broader design criteria rather than more ad hoc pod cycling.

## Claim Boundary

This is internal v1.5.4 experimental evidence only. It does not promote `COLLECT_K_BOUNDED`, does not change defaults, does not authorize public speedup wording, and does not publish a release.
