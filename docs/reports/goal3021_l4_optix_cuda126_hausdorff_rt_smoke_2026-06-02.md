# Goal3021: L4 OptiX CUDA 12.6 Hausdorff RT Smoke

## Purpose

Goal3021 follows the Goal3020 PTX/toolchain blocker. The same L4 pod could
build `librtdl_optix.so` with CUDA 12.8, but the generated PTX failed at
runtime because driver `565.57.01` could not load CUDA 12.8-generated PTX.

This goal records the clean workaround: install a side-by-side CUDA 12.6
toolkit slice on the pod, rebuild the RTDL OptiX library against CUDA 12.6, and
rerun the exact RT Hausdorff smoke.

## Pod Setup

Pod target:

`root@157.157.221.29 -p 29842`

GPU/driver:

`NVIDIA L4, 565.57.01`

Clean RTDL source commit:

`aa643d2c272a8106f33b939f688a1cb73f1bd48b`

The source tree was clean before the evidence run.

## CUDA 12.6 Side-By-Side Toolkit Slice

The pod already used NVIDIA's Ubuntu 24.04 CUDA network repository. After
refreshing the apt cache, the following minimal CUDA 12.6 packages were
available and installed side-by-side with the existing CUDA 12.8 toolkit:

```bash
apt-get install -y --no-install-recommends \
  cuda-nvcc-12-6 \
  cuda-nvrtc-dev-12-6 \
  cuda-cudart-dev-12-6 \
  cuda-driver-dev-12-6
```

Observed `nvcc` tail:

`Build cuda_12.6.r12.6/compiler.35059454_0`

## Rebuild

The RTDL OptiX library was rebuilt with:

```bash
PATH=/usr/local/cuda-12.6/bin:$PATH \
CUDA_HOME=/usr/local/cuda-12.6 \
LD_LIBRARY_PATH=/usr/local/cuda-12.6/targets/x86_64-linux/lib:/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH \
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.6
```

`ldd build/librtdl_optix.so` then resolved:

`libnvrtc.so.12 => /usr/local/cuda-12.6/targets/x86_64-linux/lib/libnvrtc.so.12`

## Smoke Command

The exact RT Hausdorff smoke was run with both RTDL OptiX library environment
names set:

```bash
PYTHONPATH=$PWD/.pydeps_v26_numba_cuda:$PWD/src:$PWD \
LD_LIBRARY_PATH=/usr/local/cuda-12.6/targets/x86_64-linux/lib:/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_PTX_COMPILER=nvcc \
RTDL_NVCC=/usr/local/cuda-12.6/bin/nvcc \
RTDL_OPTIX_PTX_ARCH=compute_89 \
python3 examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py \
  --points-a 512 \
  --points-b 512 \
  --method rtdl_rt_grouped_reduced_nearest_witness \
  --compare \
  --json-out /tmp/goal3021_hd_rt_grouped_reduced_cuda126_smoke.json
```

## Evidence

Artifact:

`docs/reports/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.json`

Primary RTDL result:

| Field | Value |
| --- | --- |
| Method | `rtdl_rt_grouped_reduced_nearest_witness` |
| Backend | `optix` |
| Exact value | `true` |
| RT-core traversal used | `true` |
| Distance | `0.14627873169442843` |
| Direction | `b_to_a` |
| Threshold iterations | `38` |
| Wall seconds | `1.6226482726633549` |

OpenMP comparison:

| Field | Value |
| --- | --- |
| Distance | `0.14627873169442843` |
| Matches primary scalar distance | `true` |
| Wall seconds | `0.15259814634919167` |

The OpenMP and RTDL witness target indices differ in this small random case,
while the scalar distance matches. This report therefore claims scalar exact Hausdorff distance parity only; it does not claim stable witness identity under
equal-distance ties.

## Result

The Goal3020 toolchain blocker is unblocked for this pod by using CUDA 12.6
instead of CUDA 12.8 for generated PTX. The exact RT Hausdorff path now executes
on the L4 pod and reports `rt_core_accelerated: true`.

## Boundary

This is RT-core runtime readiness evidence, not performance evidence.

The observed 512-point smoke is slower than the OpenMP comparison and also
lacked CuPy comparison dependencies on this pod. It does not authorize v2.6 release, public speedup wording, RT-core speedup wording, whole-app speedup wording, true-zero-copy wording, package-install claims, or app-specific native-engine behavior.

The next performance step is a larger same-contract run after installing the
comparison dependencies, or a reviewed RT Hausdorff algorithmic improvement that
reduces the repeated threshold-search cost.
