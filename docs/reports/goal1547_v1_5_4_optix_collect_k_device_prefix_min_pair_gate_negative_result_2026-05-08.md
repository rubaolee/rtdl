# Goal 1547: OptiX COLLECT_K_BOUNDED Device Prefix Min-Pair Gate Negative Result

## Verdict

Rejected as an implementation path.

The candidate tried to keep Goal 1545's long-count device-prefix compact benefit while avoiding the extra prefix launch on single-pair batched levels. The default gate skipped device prefix compact unless a batched level had at least two pairs. Parity stayed clean, but the measured result did not improve the accepted path.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `b2bc7023ce2ad1d6890d0aba0a8c51b285bbdfe5`
- Evidence type: uncommitted working-tree experiment copied to the pod for measurement only

Both runs used:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`

The legacy comparison additionally set the experimental override:

`RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_MIN_PAIRS=1`

## Result

| candidates | min-pair gate | total ms | merge-launch ms | merge launches | parity |
|---:|:---:|---:|---:|---:|:---:|
| 4097 | default gate | 0.156797 | 0.071116 | 6 | accepted |
| 4097 | legacy min=1 | 0.142450 | 0.060444 | 7 | accepted |
| 65537 | default gate | 0.426769 | 0.283407 | 22 | accepted |
| 65537 | legacy min=1 | 0.425527 | 0.284148 | 23 | accepted |
| 131072 | default gate | 0.479629 | 0.320588 | 23 | accepted |
| 131072 | legacy min=1 | 0.472856 | 0.316070 | 23 | accepted |

The gate reduced the modeled launch count for `4097` and `65537`, but the timing did not improve. The accepted Goal 1545 behavior remains the better measured default for this pod session.

## Decision

Do not add `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_MIN_PAIRS`.

The extra conditional policy makes the runtime more complex without an accepted measured win. The current evidence says the launch-count model alone is not a sufficient predictor for this subpath; timing is still dominated by orchestration and GPU-driver effects around very small kernels.

## Claim Boundary

This is a negative engineering result only. It does not change the accepted Goal 1545 device-prefix compact path, does not authorize a public speedup claim, and does not publish a new feature.
