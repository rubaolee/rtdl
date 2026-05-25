# Goal2609 GPU-RMQ Non-Author Baselines

Date: 2026-05-25

## Scope

This run uses the user-provided pod for non-author-code evidence only. It does
not build or run `lakreis/GPU-RMQ`; author-code comparison remains pending for a
separate special pod.

The benchmark compares the current RTDL GPU-RMQ prepared RT path against two
same-input baselines:

- RTDL: `paper_rt_prepared_reuse`, using reusable app-side prepared scenes and
  generic OptiX closest-hit/grouped-argmin primitives.
- CPU baseline: standalone C++ sparse-table RMQ query path with OpenMP query
  parallelism, using 16 CPU threads. The sparse-table results are validated
  against an exact scan.
- CUDA baseline: standalone CUDA sparse-table query kernel. The sparse table is
  built on CPU and uploaded to GPU, so this is a query-only kernel baseline,
  not an end-to-end GPU preprocessing baseline.

CuPy was not installed on the pod, so the CUDA baseline is compiled directly
with `nvcc`. Because the pod driver rejected CUDA 12.8 PTX JIT, the baseline is
compiled as native A5000 SASS with `-gencode arch=compute_86,code=sm_86`.

## Pod Environment

- Host: `203.57.40.101:10082`
- GPU: NVIDIA RTX A5000
- Driver: 565.57.01
- OptiX SDK: `/workspace/optix-8.1`
- RTDL library: `/workspace/rtdl_goal2598/build/librtdl_optix.so`
- Remote repo HEAD recorded by probe: `dc6b91d29a37ad335e2ebe0cf553cd01606530fc`
- Artifact: `docs/reports/goal2609_gpu_rmq_non_author_baselines_2026-05-25.json`

## Results

All rows passed correctness checks:

- RTDL matched the app CPU reference.
- CPU sparse-table baseline matched exact scan.
- CUDA sparse-table baseline matched the CPU sparse-table baseline.

| Dataset | Values | Queries | Block | RTDL query median | CPU/OpenMP sparse query median | CUDA sparse query median | RTDL / CUDA |
|---|---:|---:|---:|---:|---:|---:|---:|
| repeated | 4,096 | 1,000 | 64 | 0.2557 ms | 0.0105 ms | 0.0121 ms | 21.08x slower |
| random | 16,384 | 4,000 | 256 | 0.4658 ms | 0.0788 ms | 0.0350 ms | 13.32x slower |
| repeated | 65,536 | 8,000 | 512 | 1.0332 ms | 0.2614 ms | 0.0715 ms | 14.44x slower |

## Conclusion

The current RTDL GPU-RMQ implementation is correct and uses the intended generic
OptiX grouped-argmin path, but it is not performance-competitive against a
direct CUDA sparse-table query kernel on these generated workloads. It is also
slower than a tuned 16-thread CPU sparse-table query baseline for this matrix.

This result is not surprising after Goal2608: RTDL is paying for RT
geometry/traversal and grouped-reduction machinery, while the CUDA baseline is a
direct array RMQ query kernel over a precomputed sparse table. The next RTDL
performance question is therefore not basic correctness; it is whether the
paper's RT-style query decomposition can be represented in RTDL with lower
launch/geometry/reduction overhead, and how close that can get to author code on
the special author-code pod.

## Claim Boundary

This report supports only non-author-code, same-generated-input evidence for
RTDL versus standalone CPU/CUDA baselines. It does not authorize claims against
the GPU-RMQ paper implementation or paper figures.
