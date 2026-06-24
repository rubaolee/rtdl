# Goal3020: L4 OptiX Readiness and PTX Toolchain Blocker

## Purpose

Goal3020 records the pod-side OptiX setup attempt for the next RT-core
Hausdorff step.

## Pod

- SSH target used: `root@157.157.221.29 -p 29842`
- GPU/driver: `NVIDIA L4, 565.57.01`
- RTDL source commit for the successful build:
  `87681a6996cf83f44ff75004fb147efb3fd66014`

## What Worked

The pod had CUDA 12.8 installed at:

`/usr/local/cuda-12.8`

`nvcc` was not on `PATH`, but the compiler existed at:

`/usr/local/cuda-12.8/bin/nvcc`

OptiX SDK headers were installed with:

```bash
mkdir -p /root/vendor
git clone --depth 1 --branch v8.1.0 https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
ln -sfn /root/vendor/optix-sdk /opt/optix
```

The RTDL OptiX library then built successfully:

```bash
PATH=/usr/local/cuda-12.8/bin:$PATH \
CUDA_HOME=/usr/local/cuda-12.8 \
LD_LIBRARY_PATH=/usr/local/cuda-12.8/targets/x86_64-linux/lib:/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH \
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
```

Observed output:

- `build/librtdl_optix.so` was created;
- `ldd build/librtdl_optix.so` resolved `libnvrtc.so.12` from CUDA 12.8;
- `libnvoptix.so.1` existed under `/usr/lib/x86_64-linux-gnu`.

## What Failed

The existing exact RT Hausdorff grouped-reduced witness smoke failed:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python3 examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py \
  --points-a 512 \
  --points-b 512 \
  --method rtdl_rt_grouped_reduced_nearest_witness \
  --compare \
  --json-out /tmp/goal3020_hd_rt_grouped_reduced_smoke.json
```

Failure:

`CUDA driver error: the provided PTX was compiled with an unsupported toolchain.`

The retry with:

- `LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:...`;
- `RTDL_OPTIX_PTX_ARCH=compute_89`;
- `RTDL_OPTIX_PTX_COMPILER=nvcc`;
- `RTDL_NVCC=/usr/local/cuda-12.8/bin/nvcc`;

failed with the same unsupported-toolchain error.

## Diagnosis

The pod has driver `565.57.01` and CUDA/NVRTC `12.8`. The installed
`cuda-compat-12-8` package contains only docs in this container, so it does not
provide a compatibility `libcuda` path. Older CUDA 12.5/12.6/12.7 packages were
not available in the current apt cache.

Therefore this pod can build `librtdl_optix.so`, but cannot currently load the
generated CUDA 12.8 PTX for this RT Hausdorff path.

## Boundary

This is not an RTDL algorithm failure and not evidence against RT-core
acceleration. It is a pod driver/toolkit compatibility blocker for generated
PTX module loading.

The next RT-core Hausdorff step needs one of:

- a pod with a driver compatible with CUDA 12.8 generated PTX;
- an installable older CUDA/NVRTC toolkit compatible with driver 565;
- a reviewed native path that loads compatible CUBIN instead of PTX for this
  generated OptiX module path.
