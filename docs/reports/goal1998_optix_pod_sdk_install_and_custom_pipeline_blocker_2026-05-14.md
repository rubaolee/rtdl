# Goal1998: OptiX Pod SDK Install and Custom Pipeline Blocker

## Verdict

The pod blocker is no longer "OptiX SDK unavailable." The SDK was installed from
the documented `NVIDIA/optix-sdk` path, the RTDL OptiX library builds, and the
container can load `libnvoptix.so.1`. The remaining blocker is narrower:
custom-primitive OptiX ray/triangle any-hit modules fail during
`optixModuleCreate` with `Internal compiler error` on this pod.

This is not release performance evidence and does not authorize v2.0 speedup,
whole-app acceleration, or broad RT-core claims.

## Pod Environment

- Host: `root@213.173.109.6 -p 31938`
- Workspace: `/root/rtdl_goal1983`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- Driver: `565.57.01`
- CUDA toolkit used for the native build: `/usr/local/cuda`
- OptiX SDK install path: `/root/vendor/optix-sdk`
- Working SDK line: `v8.1.0`
- Rejected SDK line: `v9.0.0`, with `Unsupported ABI version`

## What Was Fixed

- The SDK install path from `refresh.md` works on this pod:
  `git clone --branch v8.0.0 https://github.com/NVIDIA/optix-sdk`, followed by
  a tag switch to `v8.1.0`.
- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk` builds
  `build/librtdl_optix.so`.
- `libnvoptix.so.1` was installed into the container library path through the
  `libnvidia-gl-565` payload.
- `optixModuleCreate` now reports its compiler log instead of collapsing all
  module creation failures to only `OptiX error: Internal compiler error`.
- Prepared 2-D ray/triangle scenes no longer eagerly compile the old exact count
  pipeline during scene construction. Pipeline compilation is now lazy, so a
  prepared scene only compiles the path the caller actually runs.

## Still Blocked

The generic all-witness paging smoke reaches real OptiX module creation, but the
driver compiler rejects the custom-primitive module:

```text
OptiX module compile error: Internal compiler error
COMPILE ERROR: Module compilation failed
```

This remained true after isolating the candidate all-witness path from the exact
ray/triangle intersection body and after moving the segment-ray columns for this
path to float32. The failure therefore appears to be in the pod's custom
primitive OptiX compilation lane, not in SDK discovery or `librtdl_optix.so`
loading.

As a control, the older collect-k probe completed:

```text
python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py ...
{"status": "goal1506_optix_collect_k_stage_profile_probe_recorded"}
```

That control means the pod is not completely unusable for CUDA-side native work,
but it does not prove the custom primitive RT traversal path required by the
new witness-pair adapter.

## Package Boundary

The pod has bind-mounted NVIDIA driver files. Installing `libnvidia-gl-565`
made `libnvoptix.so.1` visible, but full `apt -f install` repair still fails on
`libcuda.so.565.57.01` and `libnvcuvid.so.565.57.01` with:

```text
Invalid cross-device link
```

That is a container packaging constraint. It is distinct from the now-solved SDK
header problem.

## Next Action

Use a pod image where the NVIDIA user-space driver stack is mounted or installed
consistently enough for custom-primitive OptiX module compilation, then rerun the
Goal1997 smoke with:

```bash
RTDL_OPTIX_LIBRARY=/root/rtdl_goal1983/build/librtdl_optix.so \
PYTHONPATH=src:. \
python3 scratch/goal1997_pod_smoke.py
```

Until that passes, the generic witness-pair paging adapter remains locally
tested and structurally wired, but not accepted as pod-proven RT hardware
evidence.
