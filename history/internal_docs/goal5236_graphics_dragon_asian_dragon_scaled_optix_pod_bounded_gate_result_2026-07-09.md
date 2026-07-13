# Goal5236 Graphics Dragon -> AsianDragon Scaled OptiX POD Bounded Gate Result

Date: 2026-07-09

## Verdict

`implemented__current_source_rebuilt_optix_pod_bounded_gate_passed__review_pending`

Goal5236 reran the scaled Dragon -> AsianDragon bounded route on the POD with a
freshly uploaded current source snapshot and a freshly rebuilt
`librtdl_optix.so`. This avoids mixing current X-HD scripts with the old
`/tmp/rtdl_goal5144` OptiX library.

Two bounded source-subset gates passed against the full scaled AsianDragon
target:

```text
target = scaled public AsianDragon, 3,609,600 points
source = public Dragon, 437,645 points
backend = optix
source limits = 256, 1024
exact subset oracle = enabled
all cases matched = true
route_abs_diff = 0.0 for both cases
```

## Build / Version Hygiene

Remote POD:

```text
host = 213.173.108.24:13502
GPU = NVIDIA RTX 4000 Ada Generation
OptiX SDK header = /root/vendor/optix-dev/include/optix.h
CUDA = /usr/local/cuda-12.8
current source root = /tmp/rtdl_goal5236
rebuilt library = /tmp/rtdl_goal5236/build/librtdl_optix.so
rebuilt library sha256 =
  e29f6b523530fa8a5e382f3bb2d64fc93f2f14868a9bf1b9005fde8c649ab1bb
```

Current-source symbol evidence was present in the uploaded tree, including:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5
global_bound_early_break
frontier_inline_nearest
```

This is not evidence from the old `/tmp/rtdl_goal5144` snapshot.

## Inputs

The bridge was derived from the Goal5234 complete same-source bridge and only
rewired paths to the POD-local files:

```text
/tmp/xhd_goal5234/data/dragon.ply
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
```

The app-owned scaled candidate remains the Goal5234 scale contract:

```text
asian_dragon.ply -> asian_dragon_scaled_1e-3.ply
scale = 0.001
```

This is still Level-B same-source candidate evidence. It does not prove exact
paper input byte identity.

## Commands

The OptiX library was rebuilt on the POD with:

```bash
cd /tmp/rtdl_goal5236
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda-12.8
```

The bounded gates used:

```bash
export PYTHONPATH=/tmp/rtdl_goal5236/src:/tmp/rtdl_goal5236
export RTDL_OPTIX_LIB=/tmp/rtdl_goal5236/build/librtdl_optix.so

python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py \
  --bridge /tmp/xhd_goal5236/bridge_scaled_remote.json \
  --profile /tmp/xhd_goal5236/profile.json \
  --backend optix \
  --source-limits 256 \
  --grid-shape 32,32,32 \
  --source-selection-policy evenly-spaced \
  --translate-each-input-to-min-bound \
  --max-inline-points 512 \
  --initial-state local-grid-cell \
  --local-grid-seed-executor numba \
  --frontier-nearest-executor numba \
  --frontier-row-order native \
  --frontier-inline-nearest \
  --global-bound-early-break \
  --frontier-row-capacity 400000 \
  --max-exact-pair-evaluations 1000000000 \
  --tolerance 1e-9
```

The 1024-source run was identical except:

```text
--source-limits 1024
--max-exact-pair-evaluations 4000000000
```

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/
  xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset256_optix_pod_2026-07-09.json
  xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset1024_optix_pod_2026-07-09.json
```

## Results

### 256-source bounded gate

```text
source_limit = 256
exact pair evaluations = 924,057,600
matched = true
route_abs_diff = 0.0

route distance/source/target = 0.05981302471903363 / 62 / 769395
exact distance/source/target = 0.05981302471903363 / 62 / 769395

route direction_total = 5.7937067076563835s
exact oracle elapsed  = 16.447613544762135s
total wall            = 30.563447952270508s

frontier rows = 1,487
candidate distance evaluations = 3,006,455
global-bound early breaks = 22
explicit frontier row capacity = 400,000
suggested next explicit capacity = 2,231
```

### 1024-source bounded gate

```text
source_limit = 1024
exact pair evaluations = 3,696,230,400
matched = true
route_abs_diff = 0.0

route distance/source/target = 0.06520984417895137 / 121 / 394515
exact distance/source/target = 0.06520984417895137 / 121 / 394515

route direction_total = 1.22140172123909s
exact oracle elapsed  = 61.16541910171509s
total wall            = 70.79386930912733s

frontier rows = 6,533
candidate distance evaluations = 12,914,037
global-bound early breaks = 77
explicit frontier row capacity = 400,000
suggested next explicit capacity = 9,800
```

The 1024-source distance is close to the paper-log all-source value
`0.06536811590194702`, but it is still a bounded subset value and must not be
reported as all-source reproduction.

## Interpretation

Goal5236 materially improves the Dragon -> AsianDragon evidence over Goal5235:

1. It moves the bounded scaled route to the POD and uses the OptiX backend.
2. It proves the current X-HD route can consume the full 3,609,600-point scaled
   target with bounded source subsets.
3. It avoids the old-snapshot issue by rebuilding the OptiX library from the
   current source subset.
4. It shows exact scalar and final max-witness agreement against subset exact
   oracles at 256 and 1024 source points.
5. It shows explicit frontier capacity is not the current bounded blocker at
   these sizes.

## Important Caveats

`per_source_witness_exact=false` in both artifacts. The route proves exact final
directed-Hausdorff scalar and final max witness for these bounded source
subsets, not exact nearest witness for every source point.

The 1024-source route timing is much lower than the 256-source route timing
because runtime/JIT/warm-state effects differ between runs. Therefore:

```text
Do not report 1024/256 timing as a scaling speedup.
Do not use either bounded route timing as an author-vs-RTDL performance ratio.
Do not claim Figure 6 reproduction.
```

The run remains Level-B same-source candidate evidence:

```text
full_paper_reproduction_claimed = false
exact_paper_dataset_reproduction_claimed = false
figure_reproduction_claimed = false
full_all_source_route_run_claimed = false
performance_ratio_claimed = false
```

## What This Does Not Prove

Goal5236 does not prove:

```text
all-source Dragon -> AsianDragon HDResult
exact paper input byte identity
Figure 6 pruning effectiveness
author-vs-RTDL performance parity
full X-HD paper reproduction
per-source witness exactness
```

## Next Recommended Work

1. Strict external review of Goals5233-5236 as one Dragon -> AsianDragon
   packet.
2. Decide whether to run a larger bounded OptiX source subset, or attempt a
   streamed/all-source route without exact oracle.
3. If pursuing all-source, do not materialize a naive all-source frontier. The
   next implementation must be streaming/chunked or must prove capacity
   boundedness first.
4. Keep the Goal5234 scaled-input contract visible: public raw AsianDragon does
   not match the paper log; the scaled `0.001` public candidate does.
