# Goal 1594: RTX 4090 Gated Collect-K Validation

## Verdict

RTX 4090 Ada validation passed for the corrected `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1` mode at commit `4fbd814cb575e72bd6d3c32ab12bd8e34eb3f65e`. The result confirms the same direction seen on RTX 3090: copy-reduction regions are consistently faster, while no-copy-reduction cases such as `65536` should not be promoted.

This evidence supports continuing the gated-candidate track. It does not promote `COLLECT_K_BOUNDED`, does not change default behavior, and does not authorize public speedup wording.

## Environment

- Host: `root@103.196.86.82 -p 54445`
- Checkout: `/root/work/rtdl_rtx4090_gated`
- Commit: `4fbd814cb575e72bd6d3c32ab12bd8e34eb3f65e`
- GPU: `NVIDIA GeForce RTX 4090`
- Driver: `550.127.05`
- Driver CUDA banner: `12.4`
- CUDA toolkit: `/usr/local/cuda-12.4`, `nvcc` release `12.4`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Runtime library path: `/usr/local/cuda-12.4/lib64`
- Architecture override: `RTDL_OPTIX_PTX_ARCH=compute_89`

## Build And Test

Build:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.4
```

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1593_v1_5_4_optix_collect_k_gated_candidate_test \
  tests.goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_test \
  tests.goal1506_v1_5_4_optix_collect_k_stage_profile_plan_test \
  tests.goal1590_v1_5_4_optix_cuda_toolchain_diagnostics_test
```

Result:

- `Ran 26 tests`
- `OK`

## Measurement Scope

The measurement compared the optimized baseline bundle against the gated candidate mode over three rounds.

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

Gated environment:

```bash
RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1
```

All baseline and gated artifacts reported accepted Goal1506 evidence, parity pass, and expected topology.

## RTX 4090 Results

Negative delta means the gated mode is faster than the optimized baseline.

| Candidate count | Avg delta ms | Faster rounds | Payload-copy change |
|---:|---:|---:|---|
| 49152 | -0.000360 | 2/3 | 1 -> 0 |
| 49153 | -0.001407 | 2/3 | 3 -> 1 |
| 49154 | -0.001160 | 2/3 | 3 -> 1 |
| 65535 | 0.002631 | 1/3 | 0 -> 0 |
| 65536 | 0.004917 | 0/3 | 0 -> 0 |
| 65537 | -0.013500 | 3/3 | 5 -> 0 |
| 65538 | -0.009906 | 3/3 | 5 -> 0 |
| 65552 | -0.013953 | 3/3 | 5 -> 0 |
| 69632 | -0.007417 | 3/3 | 4 -> 0 |
| 69633 | -0.007150 | 3/3 | 4 -> 1 |

## Interpretation

The Ada result agrees with the RTX 3090 direction:

- Strongest and most consistent wins occur where the gated mode removes carry payload copies.
- `65537`, `65538`, and `65552` are consistently faster with `5 -> 0` payload copies.
- `69632` and `69633` are consistently faster with `4 -> 0` or `4 -> 1` payload copies.
- `65536` has no payload-copy reduction and is slower in every RTX 4090 round.

The current gate still activates at some smaller copy-reduction counts where the improvement is noise-scale on RTX 4090, such as `49152` to `49154`. That is acceptable for an experimental opt-in mode, but it argues against default promotion without further tightening.

## Next Direction

The next engineering step should be a stricter gated policy that requires a larger predicted payload-copy reduction, for example focusing on reductions of at least four payload copies. That would preserve the strongest `65537+` and `69632+` evidence while avoiding weak/noisy lower-boundary cases.

## Claim Boundary

This is internal v1.5.4 experimental evidence only. It does not promote `COLLECT_K_BOUNDED`, does not change defaults, does not authorize public speedup wording, and does not publish a release.
