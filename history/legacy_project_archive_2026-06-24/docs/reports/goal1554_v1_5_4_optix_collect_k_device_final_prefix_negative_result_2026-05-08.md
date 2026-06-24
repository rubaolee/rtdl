# Goal 1554: OptiX COLLECT_K_BOUNDED Device Final Prefix Negative Result

## Verdict

Rejected as an implementation path.

The candidate revisited final-pair device prefixing after Goal 1552 device final counts. It preserved parity, but it added one final-prefix kernel launch and regressed the long target cases. The implementation was reverted.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `a0d0ec8e267877e3cf28179e4d575f27f6167337`
- Evidence type: uncommitted working-tree experiment copied to the pod for measurement only

Both runs used:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1 RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`

The rejected candidate additionally used:

`RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_PREFIX=1`

## Result

| candidates | final device prefix | total ms | merge-launch ms | merge launches | D2H transfers | metadata fields | parity |
|---:|:---:|---:|---:|---:|---:|---:|:---:|
| 4097 | off | 0.113065 | 0.033794 | 7 | 4 | 4 | accepted |
| 4097 | on | 0.108827 | 0.028724 | 8 | 4 | 4 | accepted |
| 65537 | off | 0.286533 | 0.082164 | 23 | 34 | 34 | accepted |
| 65537 | on | 0.298336 | 0.096662 | 24 | 34 | 34 | accepted |
| 131072 | off | 0.310298 | 0.089048 | 23 | 65 | 65 | accepted |
| 131072 | on | 0.322260 | 0.103215 | 24 | 65 | 65 | accepted |

The candidate improved only the smallest target and regressed both long targets. At `131072`, total time regressed from `0.310298 ms` to `0.322260 ms`.

## Decision

Do not add `RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_PREFIX`.

After Goal 1552, the final input counts are already on device. Moving final block-offset prefixing to a device prefix kernel still adds one kernel launch, and that launch is more expensive than the host-side final block-count prefix/upload work it replaces for the long cases that matter.

## Claim Boundary

This is a negative engineering result only. It does not change the accepted Goal 1552 device final counts path, does not authorize a public speedup claim, and does not publish a new feature.
