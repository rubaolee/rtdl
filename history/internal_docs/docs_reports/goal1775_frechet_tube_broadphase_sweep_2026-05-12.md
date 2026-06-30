# Goal1775 Frechet Tube Broadphase Sweep

Date: 2026-05-12
Status: diagnostic follow-up
Verdict: needs-new-primitive-or-scope-cut

## What Changed

The continuous Frechet learner app originally used axis-aligned boxes around
curve segments for the RTDL broadphase. On real GPS trajectories those boxes
were too loose. Goal1775 replaces those AABBs with oriented segment-tube
rectangles:

- each target segment becomes a generic four-vertex shape,
- the shape is aligned with the segment direction,
- the shape is extended by the Frechet radius along and across the segment,
- RTDL still sees only generic segment/shape any-hit work.

The app also gained `--candidate-expansion`, which expands RTDL candidate cells
by a Chebyshev neighborhood before Frechet filtering. This is an app-level
safety valve for boundary propagation around candidate cells.

## Pod Sweep

Dataset:

```text
Microsoft GeoLife GPS Trajectories 1.3
file A: 20081023025304.plt
file B: 20081026134407.plt
pod: RTX A5000, OptiX headers pinned to optix-dev v9.0.0
iterations: 8
```

## Correctness And Pruning

| Points per curve | Candidate expansion | Matches all-cells oracle | Candidate cells at final radius | Prune ratio |
| ---: | ---: | --- | ---: | ---: |
| 128 | 0 | yes | 14,015 / 16,129 | 13.11% |
| 128 | 1 | yes | 15,647 / 16,129 | 2.99% |
| 128 | 2 | yes | 16,041 / 16,129 | 0.55% |
| 256 | 0 | yes | 54,347 / 65,025 | 16.42% |
| 256 | 1 | yes | 62,210 / 65,025 | 4.33% |
| 256 | 2 | yes | 63,886 / 65,025 | 1.75% |
| 512 | 0 | no | 258,566 / 261,121 | 0.98% |
| 512 | 1 | yes | 246,930 / 261,121 | 5.43% |
| 512 | 2 | yes | 253,282 / 261,121 | 3.00% |

## Interpretation

The oriented tube broadphase is a correctness and modeling improvement over
axis-aligned boxes, but it still does not create a real Frechet speedup on this
GeoLife pair:

- At the final Frechet radius, the radius is large enough that most free-space
  cells survive.
- Candidate expansion restores correctness at 512 points, but it also reduces
  pruning.
- Python candidate-filtered DP is slower than all-cells C++ even when the
  broadphase prunes a modest number of cells.
- The C++ continuation is now the right baseline surface, but it does not yet
  consume an RTDL candidate mask; the default performance-safe path treats weak
  RTDL broadphase results as advisory and falls back to all cells.

## Conclusion

The current v1.8 app can demonstrate Python+RTDL programmability and
claim-sensitive OptiX execution, but continuous Frechet distance is not yet a
good RTDL speedup workload with only segment/shape any-hit broadphase.

The next real performance step should be one of:

- exact segment-distance free-space-cell filtering in a compiled continuation,
- a generic native primitive for bounded segment/segment distance candidates,
- batched threshold-decision workloads where the radius is fixed and much
  smaller than the full Frechet distance,
- or a scope cut that keeps continuous Frechet as a learner/correctness example
  rather than a public acceleration example.

Do not publish an RT-core speedup claim for continuous Frechet from the current
implementation.
