# Goal 1546: OptiX COLLECT_K_BOUNDED Final Device Prefix Negative Result

## Verdict

Rejected as an implementation path.

Extending the Goal 1545 device-prefix compact idea into the final two-segment merge preserved parity in the working-tree experiment, but it regressed the larger measured target and added one more merge launch. The experiment should not be committed as runtime behavior.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- CUDA compatibility path: `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda-12.8/lib64`
- Base commit: `c50555fb32936ffce353b1b5e8ff20631e716ef6`
- Evidence type: uncommitted working-tree experiment copied to the pod for measurement only

Both runs used:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`

The rejected candidate additionally used:

`RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_FINAL_COMPACT=1`

## Result

| candidates | final device prefix | total ms | merge launches | parity |
|---:|:---:|---:|---:|:---:|
| 4097 | off | 0.143091 | 7 | accepted |
| 4097 | on | 0.138763 | 8 | accepted |
| 65537 | off | 0.428311 | 23 | accepted |
| 65537 | on | 0.430275 | 24 | accepted |
| 131072 | off | 0.475852 | 23 | accepted |
| 131072 | on | 0.492944 | 24 | accepted |

The small `4097` case improved in this session, but the long cases did not. The largest target, `131072`, regressed from `0.475852 ms` to `0.492944 ms`.

## Decision

Do not add `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_FINAL_COMPACT`.

The final pair has only one compact pair, so replacing the host-side block-offset prefix with a device prefix kernel removes little CPU work while adding another kernel launch. For the current architecture, the launch cost is larger than the saved host-prefix work on the long target that matters most.

## Claim Boundary

This is a negative engineering result only. It does not change the accepted Goal 1545 device-prefix compact path, does not authorize a public speedup claim, and does not publish a new feature.
