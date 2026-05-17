# Goal2183 RayJoin Current Performance Synthesis

Date: 2026-05-16

Status: current evidence synthesis; not a release gate.

## Purpose

This report answers the practical question raised after the RayJoin paper
comparison: why did early RTDL runs not show RayJoin-paper-like speedups, and
what changed in the latest measurements?

The answer is now concrete:

- early runs were too small, unprepared, or bottlenecked by repeated reference
  materialization
- larger overlay rows now show a widening OptiX-over-Embree advantage
- sparse true-hit LSI strongly favors OptiX traversal over brute-force CUDA
- bounded PIP is parity-clean but remains Embree-favored at the measured scale

## Evidence Table

All rows below are same-contract RTDL rows from the current RayJoin lane. They
are not full RayJoin paper reproduction results.

| Goal | Case | Rows | CPU/native-oracle sec | Embree sec | OptiX sec | Prepared OptiX sec | CuPy sec | Main finding |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2181 | `pip_county512` | 1,430 | 0.016410 | 0.004546 | 0.004800 | n/a | n/a | Embree slightly faster than OptiX; both beat CPU/native-oracle |
| 2179 | `lsi_county256_soil256_count512` | 269 | n/a | 0.201283 | 0.003222 | 0.021942 | 0.040767 | OptiX hot path beats Embree by 62.472x and CuPy brute force by 12.653x |
| 2177 | `overlay_county256_soil256` | 56,876 | 2.185177 | 0.134782 | 0.073110 | 0.078009 | n/a | OptiX beats Embree by 1.844x |
| 2177 | `overlay_county384_soil384` | 130,320 | 11.283898 | 0.465292 | 0.177676 | 0.186106 | n/a | OptiX beats Embree by 2.619x |
| 2177 | `overlay_county512_soil512` | 233,766 | 35.656977 | 1.188169 | 0.322171 | 0.336156 | n/a | OptiX beats Embree by 3.688x |

## Why Early Runs Were Not Paper-Like

The early RTDL RayJoin probes did not resemble the RayJoin paper because they
were not yet measuring the same favorable conditions:

1. Small rows paid fixed OptiX launch and module warmup costs without enough
   candidate work to amortize them.
2. The runner repeatedly rebuilt CPU Python reference rows inside backend
   repeats, which polluted wall-clock test time and made larger runs painful.
3. Some paths lacked prepared or reusable build-side state.
4. Earlier summaries mixed cold-start effects with hot-repeat behavior.
5. Brute-force GPU baselines were not separated from indexed or spatially
   filtered GPU baselines.

Goals 2175, 2177, 2179, and 2181 repair that picture by using shared reference
rows, explicit warmup/repeat separation, and artifact-level claim boundaries.

## Design Lessons

### RTDL/OptiX wins when traversal rejects lots of work

The LSI row has 136,411,275 candidate segment pairs but only 269 true
intersections. CuPy brute force still evaluates the broad pair space. OptiX can
use RT traversal to reject most geometry cheaply. That is why hot one-shot OptiX
beats CuPy brute force by 12.653x on this row.

### Overlay improves with scale

The overlay row progression is the clearest scale signal:

- count256: OptiX vs Embree `1.844x`
- count384: OptiX vs Embree `2.619x`
- count512: OptiX vs Embree `3.688x`

That trend supports the conclusion that RTDL's generic OptiX overlay dependency
primitive becomes more useful as candidate volume grows.

### PIP is not automatically an RT win

`pip_county512` is parity-clean and both native backends beat CPU/native-oracle,
but Embree is slightly faster than OptiX. This keeps the public story honest:
RTDL does not claim that every RayJoin subproblem is accelerated by NVIDIA RT
cores at every scale.

### Prepared state is workload-shaped

Prepared OptiX remains useful as a runtime option, especially when build-side
state is reused across many probes. The current overlay/LSI rows also show that
one-shot OptiX can be faster in hot repeated measurements. The runtime should
choose based on workload shape, call count, and measured setup cost.

## Claim Boundary

This synthesis authorizes:

- a current RayJoin subproblem evidence summary
- a narrow statement that RTDL/OptiX now shows strong wins on sparse LSI and
  larger overlay rows
- a narrow statement that PIP remains an Embree-favored boundary row at the
  measured scale

This synthesis does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- whole-app RayJoin speedup claims
- claims against stronger CUDA/CuPy spatial-indexed baselines
- claims that OptiX wins every RayJoin subproblem

## Next Work

The next evidence step is a stronger GPU baseline and paper-protocol lane:

1. Add a spatially filtered CUDA/CuPy baseline for LSI and overlay rather than
   only brute-force CUDA.
2. Separate cold-start, warm-hot, and many-query prepared-state measurements.
3. Add larger or paper-aligned CDB slices where memory and runtime remain
   bounded.
4. Keep app policy in Python/partner code and preserve the app-agnostic native
   engine contract.
