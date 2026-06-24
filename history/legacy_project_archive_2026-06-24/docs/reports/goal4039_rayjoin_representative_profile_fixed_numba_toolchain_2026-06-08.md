# Goal4039 RayJoin Representative Profile With Fixed Numba Toolchain

Date: 2026-06-08

## Purpose

Goal4039 reruns the Goal3866 RayJoin representative mixed-route profile on the
current RTX 4000 Ada pod after fixing a Numba CUDA toolchain mismatch.

The first run failed before timing with
`CUDA_ERROR_UNSUPPORTED_PTX_VERSION` because Numba emitted PTX `8.7` while
the driver-side linker accepted only PTX `8.4`. The fix was to force Numba
through the existing CUDA 12.4 nvcc/NVVM package from the Goal3933 runtime:

```bash
export PYDEPS124=/root/goal3933_runtime.Phh4Zo/pydeps124
export CUDA_HOME=$PYDEPS124/nvidia/cuda_nvcc
export CUDA_PATH=$CUDA_HOME
export PYTHONPATH=$PYDEPS124:src:.
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/nvvm/lib64:$LD_LIBRARY_PATH
```

This is an environment repair and evidence refresh. It does not change the
RayJoin route policy and does not add app-specific engine logic.

## Pod Evidence

Pod:

`ssh root@213.173.108.27 -p 15138 -i id_ed25519_rtdl_codex`

GPU:

`NVIDIA RTX 4000 Ada Generation, 550.127.05`

Git head on the pod:

`f544d8b019842c99fdce67db4339e69622b5d06f`

Artifacts:

- `docs/reports/goal4039_rayjoin_representative_profile_fixed_numba_toolchain_pod.json`
- `docs/reports/goal4039_rayjoin_representative_profile_fixed_numba_toolchain_pod.log`

Command:

```bash
python3 scripts/goal3866_rayjoin_representative_scale_profile.py \
  --data-dir /root/rtdl/data/rayjoin_public_cdb \
  --repeat 10 \
  --warmup 2 \
  --pip-batch-single-repeat 5 \
  --pip-batch-repeat 4 \
  --pip-batch-request-counts 1 100
```

All counted contracts matched: `all_counts_match: true`.

## Results

| Contract | Numba median sec | RTDL/OptiX median sec | RTDL/OptiX vs Numba | Recommended route |
| --- | ---: | ---: | ---: | --- |
| PIP one-shot scalar count | `0.000428744` | `0.001860224` | `0.230x` | Numba CUDA JIT scalar count |
| LSI scalar count | `0.024250556` | `0.000092421` | `262.393x` | RTDL/OptiX prepared segment-pair count |
| Overlay active count | `0.039558355` | `0.000188209` | `210.183x` | RTDL/OptiX prepared shape-pair active count |

PIP repeated-request throughput through the RTDL/OptiX prepared batch executor:

| Request count | Median ms/request | Median total ms |
| ---: | ---: | ---: |
| `1` | `0.174955` | `0.174955` |
| `100` | `0.145265` | `14.526475` |

## Interpretation

The current RayJoin benchmark status remains mixed and explicit:

- bounded one-shot public-CDB PIP favors the no-RawKernel Numba reference route;
- repeated PIP requests use the RTDL/OptiX prepared batch executor;
- LSI scalar count and overlay active count are strongly RTDL/OptiX-favorable;
- route choice stays visible and user-controlled.

This refresh is useful because it proves the Goal3866/Goal3936 route decision on
a second current RTX 4000 Ada pod after a reproducible Numba toolchain repair.

## Boundary

Goal4039 does not authorize release action, public speedup wording,
whole-app RayJoin speedup wording, broad RT-core wording, RayJoin
paper-reproduction wording, true-zero-copy wording, automatic partner
selection, AMD performance wording, or app-specific native-engine logic.
