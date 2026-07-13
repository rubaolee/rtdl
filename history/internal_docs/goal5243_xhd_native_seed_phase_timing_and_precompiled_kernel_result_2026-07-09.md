# Goal5243 - X-HD Native Seed Phase Timing + Precompiled CUDA Kernel Result

Date: 2026-07-09

Status: implemented, pending external review.

## Purpose

Goal5242 removed the nearest-continuation bottleneck for the Dragon -> scaled
AsianDragon Level-B same-source route. The remaining large phases were:

```text
frontier native OptiX launch ~= 1.16s
native CUDA local-grid seed ~= 0.85s
grid_cell_mbr prep ~= 0.61s
```

Goal5243 first instrumented the generic native CUDA local-grid seed phase, then
removed the runtime CUDA module compilation cost by moving the local-grid seed
kernel into the precompiled `librtdl_optix.so` CUDA helper path.

This is a generic RTDL system optimization:

```text
generic operation: local-grid nearest witness seed in 3-D
not X-HD-specific
not an author X-HD RT-core reimplementation
not a paper/Figure performance claim
```

## Implementation

Changed files:

```text
Makefile
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_cuda_helpers.cu
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
```

Implemented:

1. Native seed phase timing getter:

```text
rtdl_optix_seed_nearest_witness_local_grid_3d_get_last_phase_timings
```

2. Precompiled CUDA Runtime helper:

```text
rtdl_cuda_local_grid_nearest_seed_3d_precompiled
```

3. `run_local_grid_nearest_seed_3d_cuda` now uses the precompiled helper instead
   of compiling/loading `local_grid_nearest_seed_3d` from a runtime CUDA string.

4. `Makefile` now auto-detects GPU compute capability for `build-optix` when
   possible:

```text
OPTIX_CUDA_ARCH_DETECTED := sm_<detected compute capability>
OPTIX_CUDA_ARCH ?= $(OPTIX_CUDA_ARCH_DETECTED)
```

On the POD this resolved to:

```text
OPTIX_CUDA_ARCH_FLAGS = -arch=sm_89
```

This was needed because the POD uses CUDA toolkit 12.8 with NVIDIA driver
550.127.05. Without a concrete `sm_89` target, the precompiled runtime helper
hit a driver/toolchain PTX JIT incompatibility:

```text
CUDA error during launching local-grid nearest seed 3-D kernel:
the provided PTX was compiled with an unsupported toolchain
```

The explicit architecture build fixes that packaging/runtime issue.

## Verification

Local checks:

```text
py -m py_compile src/rtdsl/optix_runtime.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
py -m unittest tests.goal5200_native_local_grid_seed_test tests.goal5202_packed_coordinate_matrix_reuse_test tests.goal5238_xhd_author_ply_loader_translation_contract_test

Ran 9 tests OK
```

POD:

```text
host = 213.173.108.24
port = 13502
GPU = NVIDIA RTX 4000 Ada Generation
compute capability = 8.9
driver = 550.127.05
nvcc = CUDA 12.8.93
```

Native build:

```text
make build-optix
nvcc ... -arch=sm_89 ...
build/librtdl_optix.so built successfully
```

## Workload

Same workload as Goals5237-5242:

```text
input1 = dragon.ply
input2 = asian_dragon_scaled_1e-3.ply
source points = 437,645
target points = 3,609,600
preprocessing = translate_each_input_to_min_bound
direction = directed-a-to-b
grid_shape = 96,60,72
max_inline_points = 1024
local_grid_seed_executor = native_cuda
frontier_nearest_executor = auto
global_bound_early_break = false
validation = author-only
author HDResult = 0.06536787003278732
tolerance = 1e-6
```

## Results

### Before: runtime-compiled seed kernel

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_seed_phase_inline1024_runtime_module_pod_2026-07-09.json
```

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
direction_total = 2.8375020921230316s
route_wall = 2.8376277461647987s
total_wall = 3.589199312031269s

seed_outer = 0.8517266660928726s
seed_native_total = 0.698966517s
seed_context_ensure = 0.074045801s
seed_module_ensure = 0.496675326s
seed_kernel = 0.112516031s
seed_upload = 0.011703669s
seed_download = 0.001519385s
frontier_phase = 1.3245000839233398s
frontier_optix_launch = 1.164435831s
```

Key diagnosis:

```text
The local-grid seed cost was dominated by runtime CUDA module compile/load,
not by the CUDA kernel itself and not by host-device transfer.
```

### After: precompiled seed kernel

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run1_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run2_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5243_dragon_asian_scaled_precompiled_seed_inline1024_run3_pod_2026-07-09.json
```

All three runs:

```text
matched = true
author_abs_diff = 2.3747470656587666e-09
frontier_rows = 0
per_source_witness_exact = true
```

Median:

```text
direction_total = 2.3074675127863884s
route_wall = 2.3075230717658997s
total_wall = 3.056991830468178s

seed_outer = 0.34925105422735214s
seed_native_total = 0.202945411s
seed_module_ensure = 0.0s
seed_kernel = 0.112926713s
seed_upload = 0.012182134s
seed_download = 0.001467224s
frontier_phase = 1.3098812401294708s
frontier_optix_launch = 1.166542624s
```

Improvement:

```text
seed_native_total: 0.698966517s -> 0.202945411s
seed_outer:        0.851726666s -> 0.349251054s
direction_total:   2.837502092s -> 2.307467513s
route_wall:        2.837627746s -> 2.307523072s
```

Ratio:

```text
direction_total improvement vs runtime-module Goal5243 baseline = 1.2297x
route_wall improvement vs runtime-module Goal5243 baseline = 1.2297x
```

## Position Against Prior X-HD Route Numbers

Best known Dragon -> scaled AsianDragon same-source route progression:

```text
Goal5239 original all-source RTDL route direction_total: 30.49027620255947s
Goal5240 auto continuation executor direction_total:      9.171282961964607s
Goal5241 generic grid + native seed direction_total:       3.0695155784487724s
Goal5242 inline threshold 1024 direction_total:            2.8061167374253273s
Goal5243 precompiled seed direction_total:                 2.3074675127863884s
```

Current same-workload improvement:

```text
Goal5239 -> Goal5243 direction_total = 13.21x faster
Goal5242 -> Goal5243 direction_total = 1.216x faster
```

## Denominator-Explicit Author Comparison

Author same-POD same-input evidence from Goal5239:

```text
author process wall = 2.6587867364287376s
author internal Running.AvgTime = 83.49680000000001ms
```

Labelled comparisons:

```text
RTDL Goal5243 route_wall / author process wall = 0.868x
RTDL Goal5243 total_wall / author process wall = 1.150x
RTDL Goal5243 direction_total / author internal Running.AvgTime = 27.64x slower
```

Interpretation:

```text
The current RTDL route is now near author process-wall scale for this one
same-source workload under a labelled denominator, and route_wall is below the
author process wall.

This does not mean author internal AvgTime parity. The author's paper-style
internal timed loop remains far faster under its denominator.
```

## Remaining Bottlenecks

After Goal5243:

```text
frontier phase ~= 1.31s
  frontier OptiX launch ~= 1.17s

grid_cell_mbr prep ~= 0.61s

local-grid seed outer ~= 0.35s
  seed CUDA kernel ~= 0.113s
  seed context/setup/outer overhead remains visible
```

Nearest continuation is no longer material:

```text
nearest_continuation ~= 0.00083s
frontier_rows = 0
```

## Claim Boundary

Allowed:

```text
For the single Dragon -> scaled AsianDragon same-source public workload, RTDL's
generic route now matches the author rerun HDResult within 2.4e-9 and runs with
median route_wall 2.3075s after precompiling the generic local-grid seed CUDA
kernel.
```

Forbidden:

```text
full X-HD paper reproduction
exact paper input byte identity
Figure 5-11 reproduction
author internal AvgTime parity
paper-log exact match
multi-workload Level-B completion
universal grid-shape claim
RTDL implements the author X-HD RT-core algorithm
```

Carry-forward caveats:

```text
This is exact-value-only for one workload.
It matches the author rerun, not the paper-branch log.
The prior public-data vs paper-log delta remains a dataset provenance signal.
```

## Next Recommended Goals

1. Decompose the remaining `frontier_rows` / OptiX inline-nearest phase:

```text
Why does the native frontier/inline-nearest path still cost ~=1.31s when
frontier_rows=0?
```

2. Build a generic prepared target-grid workspace:

```text
Reuse or prebuild grid cell MBRs, dense cell tables, target coordinate buffers,
and device-side row-index buffers where the product regime allows it.
```

3. Run a second Level-B public workload:

```text
Check whether 96,60,72 + max_inline_points=1024 is robust or workload-specific.
```

4. Keep the author denominator audit open:

```text
Do not compare RTDL route_wall to author internal AvgTime without explicitly
stating the denominator mismatch.
```
