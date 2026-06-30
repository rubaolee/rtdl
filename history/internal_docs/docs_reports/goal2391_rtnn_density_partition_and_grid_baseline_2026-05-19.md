# Goal2391 RTNN Density Partition And Grid Baseline

Date: 2026-05-19

Status: current RTNN campaign round closed with a sharper design conclusion.

## Purpose

Goal2391 finishes the remaining RTNN project actions after Goal2388:

1. Try adaptive/density-aware partitioning for clustered distributions.
2. Add a stronger CUDA-core baseline than all-pairs CuPy.
3. Keep RTNN as an active v2.x benchmark campaign while closing the current evidence round.

The result is mixed in the best possible way: it tells us exactly which idea works and which idea does not.

## What Changed

The RTNN harness now has two new commands:

- `run-rtdl-adaptive-3d-neighbors`: Python-level density-aware orchestration over generic prepared RTDL 3-D fixed-radius ranked-summary handles. It partitions query cells, builds radius halos, and runs the existing native generic prepared summary path. No RTNN-specific native ABI was added.
- `run-cupy-grid-3d-ranked-summary`: CuPy RawKernel CUDA-core uniform-grid fixed-radius ranked-summary baseline. It uses cell hashing, 27-cell traversal, and per-query bounded top-K insertion. It does not use RT cores and does not modify RTDL native code.

The new pod runner is `scripts/goal2391_rtnn_density_partition_pod_runner.sh`.

## Pod Environment

- GPU: NVIDIA RTX A5000, driver 570.211.01, 24564 MiB
- RTDL pod checkout started from commit `165c4a39`
- CUDA prefix: `/usr/local/cuda-12`
- OptiX SDK prefix: `/root/vendor/optix-sdk`
- Radius: `0.02`
- `k_max`: `50`
- Repeats: `3`

## Results

### Stronger CUDA-Core Baseline

The new CuPy grid baseline exactly matches the previous all-pairs CuPy bounded-neighbor counts for the 65k rows while being dramatically faster.

| distribution | count | all-pairs CuPy sec | grid CuPy sec | all-pairs / grid | bounded count match |
| --- | ---: | ---: | ---: | ---: | --- |
| uniform | 65,536 | 26.004428 | 0.000138 | 187865.3x | yes, 205,872 |
| clustered | 65,536 | 22.450877 | 0.047122 | 476.4x | yes, 2,891,523 |
| shell | 65,536 | 15.335754 | 0.002740 | 5596.3x | yes, 1,159,254 |

This is a much fairer CUDA-core opponent than all-pairs. It still is not a full RTNN paper reproduction, but it is closer to the algorithmic family RTNN teaches: spatial index, local cell traversal, bounded output.

### Clustered 262k Weak Row

| row | hot sec | relation |
| --- | ---: | --- |
| RTDL prepared OptiX ranked summary | 1.315511 | current RTDL baseline |
| RTDL Python adaptive partition, 8 divisions | 3.191942 | 2.43x slower than RTDL baseline |
| CuPy grid RawKernel baseline | 0.434877 | 3.03x faster than RTDL baseline |

The adaptive Python partitioning attempt is not an optimization. It preserves exactness and app-agnostic native ABI, but it creates 156 prepared partitions, duplicates halo search references, and pays many launches. It is valuable as a measured negative result.

The CuPy grid result is the new performance floor for dense clustered data. For this row, the current RTDL prepared OptiX summary path is not yet competitive with a generic CUDA-core grid partner.

## Design Insight

RTNN is teaching us that the next useful primitive is not "more Python partitioning." The next useful primitive is a generic density-aware fixed-radius runtime path:

- prepared search structure remains first-class;
- query batches remain explicit;
- output contract remains bounded ranked summary;
- density-aware scheduling must happen inside a lower-level runtime path or a first-class partner backend, not as hundreds of Python-created prepared handles;
- no RTNN-specific native ABI should be introduced.

That means RTDL's app-agnostic direction is still correct, but the runtime needs a stronger generic nearest-neighbor implementation for dense data. The language should be able to choose or expose an exact CUDA-grid partner path for dense clustered distributions and an RTDL/OptiX path where it wins.

## Claim Boundary

Authorized:

- Goal2391 adds a stronger exact CUDA-core grid baseline.
- Goal2391 measured and rejected Python-level adaptive RTDL partitioning as a dense-cluster optimization.
- Current RTDL still supports the generic prepared ranked-summary contract.
- Dense clustered RTNN-shaped rows now have a clear next v2.x runtime target.

Not authorized:

- Full RTNN paper reproduction.
- Broad RT-core nearest-neighbor speedup claim.
- Claim that Python-level partitioning improves RTDL.
- Claim that RTDL beats the stronger CUDA-grid baseline on dense clustered data.
- Release claim without the required release consensus.

## Closed For This Round

The current RTNN campaign is closed as a useful v2.2 benchmark round:

- RTDL can express the workload with generic prepared ranked summaries.
- The all-pairs CUDA baseline was too weak and has been replaced by a much stronger grid baseline.
- The clustered weak spot is no longer vague: it requires a lower-level generic density-aware runtime or partner-grid primitive.

Future work remains in v2.x, not v3.0 shader injection.
