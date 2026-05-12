# Goal1776 Frechet Masked C++ Continuation

Date: 2026-05-12
Status: implemented and pod-tested
Verdict: accept-with-boundary

## Purpose

Goal1775 showed that RTDL can produce candidate free-space cells, but the fair
C++ continuation was ignoring those masks. Goal1776 makes the learner-owned C++
continuation able to consume RTDL candidate masks for each threshold decision.

This tests the next logical question:

> If RTDL/OptiX gives the app a candidate cell mask, can a compiled Frechet
> continuation use that mask to beat compiled all-cells C++?

## Implementation

`examples/rtdl_continuous_frechet_distance_app.py` now supports:

- C++ all-cells distance search,
- C++ masked threshold decisions,
- Python orchestration that calls RTDL/OptiX per binary-search radius,
- candidate-mask files passed into the compiled C++ helper,
- the existing `--min-prune-ratio` guard so weak masks fall back to all-cells
  continuation by default.

The native RTDL engine remains app-agnostic. The C++ Frechet helper is
learner/app-owned code, not a native engine symbol.

## Pod Measurement

Dataset:

```text
Microsoft GeoLife GPS Trajectories 1.3
file A: 20081023025304.plt
file B: 20081026134407.plt
pod: RTX A5000, OptiX headers pinned to optix-dev v9.0.0
iterations: 8
oracle disabled for timing
repeats: 3
```

| Points per curve | Path | Median wall (s) | Result | Candidate cells |
| ---: | --- | ---: | ---: | ---: |
| 128 | C++ all-cells | 0.014186 | 12199.4 | all 16,129 |
| 128 | RTDL/OptiX mask + C++ decision, expansion 0 | 0.196552 | 12199.380 | 14,015 |
| 128 | RTDL/OptiX mask + C++ decision, expansion 1 | 0.354680 | 12199.380 | 15,647 |
| 256 | C++ all-cells | 0.046483 | 12217.6 | all 65,025 |
| 256 | RTDL/OptiX mask + C++ decision, expansion 0 | 0.765845 | 12217.571 | 54,347 |
| 256 | RTDL/OptiX mask + C++ decision, expansion 1 | 1.226353 | 12217.571 | 62,210 |
| 512 | C++ all-cells | 0.173657 | 12217.6 | all 261,121 |
| 512 | RTDL/OptiX mask + C++ decision, expansion 0 | 4.010848 | incorrect | 258,566 |
| 512 | RTDL/OptiX mask + C++ decision, expansion 1 | 7.320967 | 12217.571 | 246,930 |

## Interpretation

The masked C++ path is useful as an engineering probe, but it is not a speedup:

- The mask is still too dense on this real GPS pair.
- Expansion 1 restores correctness at 512 points, but keeps almost all cells.
- Running RTDL/OptiX once per binary-search radius plus writing mask files and
  launching the C++ helper per decision dominates the saved cell work.
- The default `--min-prune-ratio 0.25` guard is the correct public behavior:
  it avoids using masks this weak as Frechet filters.

## Conclusion

This closes the simple "just let C++ consume the RTDL mask" hypothesis. It does
not solve real-dataset continuous Frechet acceleration.

The remaining viable directions are algorithmic, not plumbing:

- fixed-radius/batched decision workloads that amortize RT setup over many
  trajectory pairs,
- a tighter generic segment-distance candidate primitive,
- a C++ continuation that computes exact free-space intervals and masks in one
  compiled pass,
- or keeping continuous Frechet as a v1.8 learner example rather than a public
  performance claim.

Do not publish continuous Frechet RT-core speedup wording from this path.
