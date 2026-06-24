# Goal2373 Parallel Exact-Refine Tuning Negative Result

Date: 2026-05-19

Status: negative tuning result; no source change retained.

## Purpose

Goal2371 added a native prepared 3D bounded-neighbor handle for the generic
fixed-radius neighbor primitive. Its pod evidence showed that reusable native
search structures work, but the large 262k row is still dominated by final row
download plus host exact refinement.

This goal tested whether a narrow host-side optimization, parallelizing the
direct-ID exact-refine materialization loop with `std::thread`, is enough to
improve the current v2.2 RTNN-informed path without changing the primitive
contract.

## Environment

- Pod SSH target: `root@69.30.85.177 -p 22055`
- Repository checkout: `/root/work/rtdl_goal2368`
- Base commit: `2a2069f5` (`Goal2371 add native prepared 3D neighbor path`)
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- CPU: Intel Xeon Gold 6342, 96 logical CPUs
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`
- Runner: `scripts/goal2371_native_prepared_frn3d_pod_runner.sh`

## Tested Variants

The experimental patch added a shared
`materialize_fixed_radius_neighbors_3d_direct_rows(...)` helper and routed both
the prepared and one-shot direct-ID paths through it. The helper preserved exact
double host filtering and generic ABI naming.

| Variant | 65k warm sec | 65k exact refine sec | 262k warm sec | 262k exact refine sec | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| Goal2371 tracked baseline | 0.007279 | 0.004501 | 0.090302 | 0.066530 | baseline |
| Parallel threshold 16,384, cap 32 | 0.014630 | 0.009117 | 0.078536 | 0.061759 | mixed; large improved, small regressed |
| Parallel threshold 131,072, cap 8 | 0.008676 | 0.005664 | 0.125670 | 0.103232 | reject |
| Parallel threshold 131,072, cap 32 | 0.014005 | 0.005332 | 0.094221 | 0.070040 | reject |
| Parallel threshold 131,072, cap 24, repeat 5 | 0.010901 | 0.006826 | 0.116610 | 0.089560 | reject |

All variants preserved row counts:

- 65k: `206434`
- 262k: `2512822`

## Conclusion

Naive host parallelization is not a reliable v2.2 improvement. It can improve
one large warm run, but it is sensitive to worker count, run order, local vector
copying, and NUMA effects. It also harms the smaller 65k regime where the
tracked Goal2371 serial exact-refine path is already fast.

No source change from this experiment should be retained.

## Design Lesson

The problem is not merely "use more CPU threads." The current primitive has a
deeper continuation-shape issue:

1. The GPU produces a compact bounded-neighbor row stream.
2. Millions of rows are downloaded to the host.
3. The host performs exact filtering/materialization before downstream partner
   code can reduce or consume the result.

For serious v2.2 RTNN-style performance, the next generic primitive should keep
more of this continuation device-resident:

- device-resident exact filter, when the requested output can tolerate the
  device coordinate contract;
- device-side row-summary continuation for count/reduce workloads;
- bounded output materialization policy that avoids downloading rows that the
  user only intends to reduce;
- an explicit claim boundary for device-distance versus host-exact-distance
  output.

This remains generic runtime work. It must not introduce native RTNN ABI names
or app-specific neighbor logic.
