# Goal2388 RTNN-Inspired Fair-Fight Benchmark

Date: 2026-05-19

Status: evidence complete for the scoped v2.2 RTNN campaign row.

## Purpose

Goal2388 closes the five immediate next useful RTNN tasks:

1. Add a paper-facing benchmark harness shape instead of only small smoke rows.
2. Add a prepared and batched large-scale RTDL path for 3-D fixed-radius ranked neighbor summaries.
3. Exercise the device-resident top-K continuation added by Goals2381 and 2384.
4. Keep exact and approximate modes explicit: this report uses exact fixed-radius ranked-summary rows, not ANN mode.
5. Add a fair CUDA-core baseline and optional official RTNN comparison on the same pod.

This is not a full RTNN paper reproduction. It is a language/runtime benchmark showing whether RTDL v2.2 can express a serious RTNN-shaped workload through generic prepared 3-D fixed-radius neighbor primitives without adding RTNN-specific native ABI.

## Implementation

The runner `scripts/goal2348_rtnn_v2_2_external_runner.py` now supports:

- `generate --distribution uniform|clustered|shell` for deterministic large synthetic RTNN-shaped point clouds.
- `run-rtdl-batched-3d-neighbors` for prepared OptiX 3-D fixed-radius ranked-summary rows over explicit query batches.
- `run-cupy-3d-ranked-summary` for an exact CUDA-core all-pairs CuPy baseline over the same fixed-radius ranked-summary contract.

The pod runner is `scripts/goal2388_rtnn_fair_fight_pod_runner.sh`. It builds RTDL OptiX, probes/installs CuPy, optionally clones and builds the public RTNN implementation, runs three distributions, records all claim boundaries, and writes JSON artifacts under `docs/reports/goal2388_rtnn_fair_fight_pod/`.

No RTNN-specific native symbol, shader, or ABI was added to RTDL.

## Pod Environment

- RTDL commit: `7738e6fd30d9eb57869afb7c5b17b5187586392e`
- GPU: NVIDIA RTX A5000, driver 570.211.01, 24564 MiB
- CUDA prefix: `/usr/local/cuda-12`
- OptiX SDK prefix: `/root/vendor/optix-sdk`
- SSH target used for evidence: `root@69.30.85.177 -p 22055`
- Radius: `0.02`
- `k_max`: `50`
- RTDL query batch size: `65536`
- CuPy query batch size: `256`
- Repeats: `3`; tables report the artifact `elapsed_sec` field, which is the final repeat.

## RTDL vs CuPy Same-Family Fair Baseline

The CuPy baseline is a CUDA-core all-pairs exact fixed-radius ranked-summary baseline. It does not use RT cores, BVH traversal, or RTDL. It computes the same kind of per-query bounded ranked-neighbor summary, then returns aggregate checksums. It is intentionally not an optimized grid/BVH CUDA implementation.

Interpretation caveats: this is a same-family user-contract comparison, not a same-algorithm comparison. RTDL uses a prepared OptiX structure and 65,536-query batches; CuPy uses all-pairs CUDA-core blocks and 256-query batches to stay inside GPU memory. The table therefore supports a narrow claim about RTDL's prepared ranked-summary primitive beating this included CuPy all-pairs baseline on this pod. It does not prove a broad nearest-neighbor speedup over all possible CUDA-core implementations.

| distribution | count | RTDL prepared OptiX sec | CuPy CUDA-core sec | CuPy / RTDL | RTDL raw candidates | CuPy bounded neighbors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| uniform | 65,536 | 0.012051 | 26.004428 | 2157.8x | 205,874 | 205,872 |
| clustered | 65,536 | 0.204774 | 22.450877 | 109.6x | 2,891,523 | 2,891,523 |
| shell | 65,536 | 0.006513 | 15.335754 | 2354.7x | 1,159,254 | 1,159,254 |

The uniform row has a two-neighbor count difference between RTDL native double/OptiX-side thresholding and the CuPy float32 all-pairs baseline. This does not affect the performance conclusion, but it prevents using this row as a bitwise correctness oracle. Correctness of the ranked-summary native primitive remains covered by Goal2384 small-oracle tests.

## RTDL Scale Rows

RTDL also ran 262k-point rows on the same pod. These rows are not compared to CuPy because all-pairs CuPy at 262k would be too expensive for this bounded evidence run.

| distribution | count | RTDL prepared OptiX sec | raw candidates | emitted rows |
| --- | ---: | ---: | ---: | ---: |
| uniform | 262,144 | 0.041202 | 628,688 | 262,144 |
| clustered | 262,144 | 2.705786 | 3,176,792 | 262,144 |
| shell | 262,144 | 0.193032 | 2,960,627 | 262,144 |

The dense clustered row is the remaining weak spot. The prepared ranked-summary path stays generic and completes, but non-uniform density drives candidate work up sharply. The next runtime improvement is density-aware/adaptive prepared partitioning, not an RTNN-specific special case.

## Optional Official RTNN Rows

The public RTNN binary was built and run as an optional reference. Its contract is not the same as RTDL ranked-summary rows, so these rows are diagnostic rather than direct wins/losses.

| distribution | count | status | process sec | search compute ms | batch search ms | total search ms | note |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| uniform | 65,536 | ok | 1.428008 | 2.302 | 7.494 | 363.933 | different witness/materialization pipeline |
| uniform | 262,144 | ok | 2.025165 | 2.385 | 22.206 | 896.600 | different witness/materialization pipeline |
| clustered | 65,536 | ok | 1.343559 | 0.315 | 6.272 | 198.418 | different witness/materialization pipeline |
| clustered | 262,144 | OOM | 1.316509 | n/a | n/a | n/a | CUDA allocation failure in RTNN optional binary |
| shell | 65,536 | ok | 1.311399 | 6.586 | 18.470 | 236.818 | different witness/materialization pipeline |
| shell | 262,144 | ok | 1.436167 | 0.533 | 27.821 | 456.589 | different witness/materialization pipeline |

The official RTNN raw kernel timings show why the RTNN paper remains an important optimization guide. RTDL is not claiming to beat RTNN's paper implementation as a full reproduction. The useful language/runtime result is narrower: RTDL can express a generic prepared RT-core neighbor-summary workload and avoid the witness materialization costs when the user contract only needs one ranked summary row per query.

## Claim Boundary

Authorized:

- RTDL v2.2 has a generic prepared 3-D fixed-radius ranked-summary path.
- On the recorded RTX A5000 pod, the RTDL prepared OptiX ranked-summary row is much faster than the included CuPy all-pairs CUDA-core baseline for 65k synthetic uniform, clustered, and shell distributions.
- The result is app-agnostic at the native RTDL ABI level.

Not authorized:

- Full RTNN paper reproduction.
- Broad RT-core nearest-neighbor speedup claim.
- Claim that RTDL beats official RTNN on the RTNN paper's full contract.
- Claim that the CuPy baseline is the best possible CUDA-core grid/BVH implementation.
- Release claim without the required external review and consensus.

## Design Conclusions

The current v2.2 direction is right: prepared search-side structures, explicit batching, and device-side ranked-summary continuation are the minimum shape needed for serious nearest-neighbor applications.

Two design debts remain for the RTNN campaign:

- Adaptive/density-aware partitioning for clustered data.
- A stronger optimized CUDA-core baseline, ideally grid/BVH based, if we want a more aggressive CUDA-only comparison than all-pairs CuPy.

Both are v2.x runtime/language improvement work. Neither requires app-specific native ABI or future v3.0 user-defined shader injection.
