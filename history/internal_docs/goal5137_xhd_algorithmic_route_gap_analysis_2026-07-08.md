# Goal5137 - X-HD Algorithmic Route Gap Analysis

## Verdict

`xhd_algorithmic_gap_matrix_ready__generic_api_path_identified`

## Why This Goal Exists

Goals5135-5136 proved Level B Stanford graphics correctness on bounded PLY
samples. They also proved that the current RTDL exact-reference route is not the
scalable route:

```text
sample1024 RTDL route ~= 3.75s
sample2048 RTDL route ~= 33.00s
```

Continuing to increase exact pairwise sample size is no longer useful. The next
question is whether the author source contains enough information to reproduce
the X-HD algorithmic route, and what RTDL system APIs would be needed.

## Short Answer

The author source is not the blocker. It is available and detailed enough.

The blocker is architectural: the author X-HD route is a fused CUDA/OptiX
algorithm with grid cells, radius-expanded cell MBR traversal, payload nearest
state, pruning, early break, heavy-cell offload, and iterative radius growth.
RTDL currently has an exact partner/reference nearest pipeline, not this
scalable in-traversal / continuation pipeline.

## Source Evidence

Inspected author checkout on POD:

```text
/tmp/xhd-goal5112/author
```

Key files:

```text
src/hd_impl/hausdorff_distance_rt.h
src/index/uniform_grid.h
src/rt/shaders/shaders_nn_uniform_grid.cu
src/loaders/ply_loader.h
src/loaders/translate_points.h
src/run_hausdorff_distance.cu
src/rt/rt_engine.h
```

The repository root in the inspected checkout has a README but no root
`LICENSE` file. A third-party `lbvh` subdirectory has its own license. This
reinforces the policy: use the author source as behavioral evidence, but do not
copy author implementation code into RTDL core.

## Copying vs Reimplementation

We can:

- read the author source;
- reproduce algorithm behavior;
- use file/function organization as evidence for phase boundaries;
- implement equivalent generic RTDL APIs independently.

We should not:

- paste author `HausdorffDistanceRT` or shader code into RTDL core;
- introduce an `xhd_*` or `hausdorff_rt_*` core primitive;
- claim a generic RTDL system improvement if the implementation is just the
  X-HD app hardcoded under a new name.

## Algorithmic Gap Matrix

Machine-readable matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_algorithmic_gap_matrix_2026-07-08.json
```

Human summary:

| Phase | Author evidence | RTDL current state | Required RTDL direction |
| --- | --- | --- | --- |
| Input load / preprocess | `ply_loader.h` subtracts per-input `vmin`; `run_hausdorff_distance.cu` records MBR | app bridge now matches author with explicit min-bound translation | keep app-owned |
| Initial HD bounds | `HDLowerBound` / `HDUpperBound` from MBRs | no public generic bound API | generic MBR distance-bound helper |
| Target uniform grid | `uniform_grid.h` grid resolution, cell ids, prefix sums, tight cell MBRs | no public device grid index for this route | generic point-grid / cell-MBR descriptor API |
| Cell MBR BVH / RT index | `BuildBVH` over cell MBRs expanded by radius | RTDL lacks public radius-expanded cell-MBR traversal | generic RT cell-MBR candidate primitive |
| Payload nearest search | shader keeps `cmin2`, `cmax2`, miss queue, status | current route materializes pairwise rows outside traversal | generic nearest-with-bounds traversal reducer |
| Prune / early break | shader prunes by MBR min/max distance and early-breaks by `cmax2` | no in-traversal reducer of this shape | dataflow pushdown / fused reducer API |
| Heavy-cell offload | shader appends `(query, cell)` to offload queues; CUDA continuation handles it | no generic RT-to-partner offload queue | generic continuation queue from RT traversal to CUDA partner |
| Radius iteration | adaptive/double/add radius growth, BVH update/rebuild | no generic iterative frontier controller | frontier/radius policy controller |
| Metrics | `RTTime`, `CUDATime`, `OffloadingSize`, `Radius`, `CMax2`, memory | app keeps phase fields, but no unified API | app-neutral phase/memory counters |

## What This Means

The exact-reference route has done its job: it validates values.

The scalable reproduction route must be a new generic RTDL system track:

```text
point columns
-> generic target grid
-> radius-expanded cell descriptors
-> RT traversal with nearest-state payload
-> miss frontier + heavy-cell offload queue
-> CUDA continuation
-> radius-growth controller
-> directed max-nearest result
```

That route is not X-HD-only. It is a generic spatial nearest-with-bounds
pipeline. X-HD is one app using it.

## Decision

Next goal should not be larger exact pairwise execution. Next goal should be:

```text
Goal5138 - Generic grid-cell candidate API design
```

That design should specify:

1. public schema for point-grid descriptors;
2. cell-MBR column output;
3. radius-expanded cell candidate traversal contract;
4. nearest-state reducer interface;
5. offload queue shape;
6. compatibility with existing partner continuation APIs;
7. no `xhd` or `hausdorff` identity in RTDL core.

## Claim Boundary

This goal does not claim:

- X-HD algorithmic route implemented;
- full-resolution reproduction;
- Figure 5 reproduction;
- performance ratio;
- author code copied into RTDL.

It claims only that the gap is now mapped and the next generic system API track
is clear.
