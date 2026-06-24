# Goal3022: Hausdorff OptiX/CuPy Performance Probe After CUDA 12.6 Unblock

## Purpose

Goal3021 proved that the L4 pod can run the exact RT Hausdorff path once
`librtdl_optix.so` is rebuilt against CUDA 12.6. Goal3022 asks the next
performance question: after the toolchain is fixed and CuPy is installed, does
the current RT-core Hausdorff implementation compete with the direct dense
partner baseline?

The answer for the measured dense random 2D point sets is no. The RT path is
correct and uses RT traversal, but the CuPy grouped-grid rawkernel path is the
current fast reference implementation for this contract.

## Environment

Artifact:

`docs/reports/goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.json`

Collected from clean source commit:

`220971c0361b4fcab13571580ffa7889219b5e3c`

Pod:

`NVIDIA L4, 565.57.01`

Runtime/toolchain:

- CUDA prefix: `/usr/local/cuda-12.6`
- CuPy: `14.1.1`
- Numba: `0.65.1`

CuPy was installed into the existing isolated pod target directory,
`.pydeps_v26_numba_cuda`. This is a pod experiment dependency, not a package
install readiness claim.

## Measured Rows

The runner uses deterministic point generation, so methods at the same point
count use the same input sets. The `--compare` path validates scalar distance
parity against CuPy and OpenMP where recorded.

| Points | Method | Primary Seconds | CuPy Grouped Seconds | RT Cores | Threshold Iterations | Primary / CuPy |
| ---: | --- | ---: | ---: | --- | ---: | ---: |
| 512 | `cupy_grouped_grid_rawkernel` | `0.0007139332592487335` | `0.000706113874912262` | no | n/a | n/a |
| 512 | `rtdl_rt_grouped_adaptive_nearest_witness` | `0.7115871198475361` | `0.0007701590657234192` | yes | `2` | `923.9482485077731x` slower |
| 512 | `rtdl_rt_grouped_seeded_pruned_nearest_witness` | `1.0141381807625294` | `0.0007142871618270874` | yes | `0` | `1419.7905757797016x` slower |
| 1024 | `cupy_grouped_grid_rawkernel` | `0.001157231628894806` | `0.0011434704065322876` | no | n/a | n/a |
| 1024 | `rtdl_rt_grouped_adaptive_nearest_witness` | `0.734943076968193` | `0.001250673085451126` | yes | `4` | `587.6380370839229x` slower |
| 1024 | `rtdl_rt_grouped_seeded_pruned_nearest_witness` | `1.0318692661821842` | `0.0031529925763607025` | yes | `0` | `327.2666335844041x` slower |
| 2048 | `cupy_grouped_grid_rawkernel` | `0.0020523257553577423` | `0.0020744726061820984` | no | n/a | n/a |
| 2048 | `rtdl_rt_grouped_adaptive_nearest_witness` | `0.8507172502577305` | `0.0020268410444259644` | yes | `4` | `419.72568722016774x` slower |
| 2048 | `rtdl_rt_grouped_seeded_pruned_nearest_witness` | `1.1255020536482334` | `0.002042766660451889` | yes | `0` | `550.9694648135957x` slower |
| 4096 | `cupy_grouped_grid_rawkernel` | `0.003780316561460495` | `0.003743160516023636` | no | n/a | n/a |
| 4096 | `rtdl_rt_grouped_adaptive_nearest_witness` | `0.8692189827561378` | `0.0037407241761684418` | yes | `4` | `232.36649959218957x` slower |
| 4096 | `rtdl_rt_grouped_seeded_pruned_nearest_witness` | `1.147179689258337` | `0.003748953342437744` | yes | `0` | `305.9999910568072x` slower |

The earlier cold rows also include `rtdl_rt_grouped_reduced_nearest_witness`,
which remains the slowest RT variant because it performs `38` threshold-search
iterations at 512 and 1024 points.

## Findings

1. The CUDA 12.6 toolchain repair is real: all recorded RT rows execute with
   `rt_core_accelerated: true`.
2. Scalar Hausdorff distance parity is preserved for the recorded rows.
3. The current best RT method is
   `rtdl_rt_grouped_adaptive_nearest_witness`, not the older grouped-reduced
   threshold-search path.
4. The current fast reference implementation for dense random 2D exact
   Hausdorff is `cupy_grouped_grid_rawkernel`.
5. The current RT path is dominated by setup, radius orchestration, repeated
   witness traversal, and generic row handling. This is an implementation/design
   gap, not an RTDL correctness failure.

## Design Consequence

For dense 2D all-pairs exact Hausdorff, RTDL should not recommend the current
OptiX RT witness path as the performance path. A direct user-selected CuPy
partner implementation is the better v2.6 reference path today.

The next RT-core Hausdorff attempt needs a more serious generic primitive shape:

- a sparse candidate frontier or radius-plan producer that avoids repeated
  threshold search;
- device-resident candidate/witness continuation rather than repeated host
  orchestration;
- a way to prove that the BVH prunes enough candidates to beat a direct dense
  CUDA/CuPy all-pairs kernel.

These are generic runtime/primitive requirements. They must not become Hausdorff-specific native-engine customizations.

## Boundary

This report does not authorize v2.6 release, public speedup wording, RT-core
speedup wording, whole-app speedup wording, true-zero-copy wording,
package-install claims, automatic partner selection, or app-specific
native-engine behavior.

The allowed statement is narrow: after CUDA 12.6 rebuild, the L4 pod executes
the exact OptiX RT Hausdorff path correctly, but current dense exact Hausdorff performance favors the explicit CuPy partner path.
