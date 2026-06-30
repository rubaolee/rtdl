# Goal2035 Fixed-Radius CUDA 12 OptiX Probe

Date: 2026-05-14

Status: development evidence, not v2.0 release authorization.

## Purpose

Goal2030 recorded that the fixed-radius v2 family could not produce fresh pod timing because generated OptiX PTX failed on the RTX A5000 pod:

`CUDA driver error: the provided PTX was compiled with an unsupported toolchain`

The pod had driver 570.211.01, CUDA 13.0 as `/usr/local/cuda`, and CUDA 12.8 installed separately. The failure was not a missing GPU or missing OptiX runtime; it was a toolchain compatibility problem.

## Result

The working repair recipe is:

```bash
make build-optix CUDA_PREFIX=/usr/local/cuda-12
export CUDA_HOME=/usr/local/cuda-12
export PATH=/usr/local/cuda-12/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:/usr/local/cuda-12/compat:${LD_LIBRARY_PATH:-}
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal2024_936aff2f/build/librtdl_optix.so
export RTDL_OPTIX_PTX_ARCH=compute_86
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_NVCC=/usr/local/cuda-12/bin/nvcc
export RTDL_NVCC_CCBIN=/usr/bin/g++
```

Important details:

- `CUDA_HOME` alone was not enough because the Makefile chooses `CUDA_PREFIX`, not `CUDA_HOME`.
- `LD_LIBRARY_PATH` alone was not enough when `librtdl_optix.so` was still linked to `libnvrtc.so.13`.
- Rebuilding with `CUDA_PREFIX=/usr/local/cuda-12` changed the library dependency to `libnvrtc.so.12`.
- For this pod, forcing the generated PTX path through CUDA 12 `nvcc` was also required; NVRTC still produced driver-rejected PTX.
- The pod has `/usr/bin/g++` and `/usr/bin/g++-13`, not `/usr/bin/g++-12`, so `RTDL_NVCC_CCBIN=/usr/bin/g++` was required.

## Probe Timing

Small correctness/perf probe:

| App | Query count | Search count | v1.8 prepared OptiX median s | v2 prepared OptiX+CuPy median s | Ratio | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| facility_knn_assignment | 256 | 1,024 | 0.001006 | 0.000537 | 0.534x | counts and summary match |

This is only a repair probe. It proves that the CUDA 13 PTX blocker is avoidable on this pod and that fixed-radius timing can run again under CUDA 12 + nvcc generated PTX.

## Larger Six-App Timing

After the small probe passed, the same CUDA 12 + nvcc recipe was run against the six fixed-radius rows with 8,192 query points, 32,768 search points, 3 repeats, and one partner (`cupy`).

| App | Direction | v1.8 prepared OptiX median s | v2 prepared OptiX+CuPy median s | Ratio | Parity |
| --- | --- | ---: | ---: | ---: | --- |
| facility_knn_assignment | forward | 0.017086 | 0.000304 | 0.0178x | counts and summary match |
| hausdorff_distance | forward | 0.022093 | 0.000299 | 0.0136x | counts and summary match |
| hausdorff_distance | reverse | 0.118601 | 0.000548 | 0.0046x | counts and summary match |
| ann_candidate_search | forward | 0.018282 | 0.000499 | 0.0273x | counts and summary match |
| outlier_detection | forward | 0.021583 | 0.000278 | 0.0129x | counts and summary match |
| dbscan_clustering | forward | 0.016753 | 0.000284 | 0.0169x | counts and summary match |
| barnes_hut_force_app | forward | 0.017262 | 0.000335 | 0.0194x | counts and summary match |

This result repairs the fresh-pod evidence gap for the fixed-radius threshold-proxy rows that Goal2030 had marked as blocked by PTX toolchain failure.

## Boundaries

- This does not authorize v2.0 release.
- This does not claim broad RT-core speedup.
- This does not claim fixed-radius true zero-copy.
- This does not replace a full all-app repeatable pod timing matrix, although it does provide fresh fixed-radius pod evidence for the six threshold-proxy rows.
- The source label is a copied-source pod label, not a clean package install claim.

## Next Work

- Add the recipe to pod setup notes if the larger run remains stable.
- Consider making CUDA/NVRTC/NVCC provenance explicit in pod artifact JSON.
