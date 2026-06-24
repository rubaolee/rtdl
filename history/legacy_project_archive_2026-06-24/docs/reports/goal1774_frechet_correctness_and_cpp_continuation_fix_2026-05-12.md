# Goal1774 Frechet Correctness And C++ Continuation Fix

Date: 2026-05-12
Status: implemented and pod-tested
Verdict: accept-with-boundary

## Problem

Goal1773 found two issues in the first real-dataset continuous Frechet
benchmark:

- The RTDL/OptiX segment/expanded-shape broadphase was not selective enough on
  a GeoLife trajectory pair, so it did not beat a compiled C++ all-cells
  baseline.
- The candidate-filtered Python Frechet path could diverge from the all-cells
  result on larger real GPS curves.

The second issue is a correctness problem; the first is a performance boundary.

## Fixes

`examples/rtdl_continuous_frechet_distance_app.py` now has:

- `run_curves_app(curve_p, curve_q, ...)`, a public hook for real polylines
  instead of only synthetic authored curves.
- `--continuation cpp`, a learner-owned compiled C++ continuation for the
  Frechet all-cells free-space decision and distance search.
- `--no-oracle`, so performance runs do not include the Python all-cells oracle
  in the timed path.
- `--min-prune-ratio`, which makes RTDL broadphase candidates advisory unless
  they prune enough cells to be worth using as a filter.

If the RTDL broadphase is not selective enough, the app reports:

```text
RTDL broadphase was not selective enough for safe candidate filtering; using all free-space cells for the Frechet continuation.
```

This keeps correctness ahead of premature acceleration claims.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal1771_continuous_frechet_python_rtdl_learner_app_test

Ran 5 tests in 2.533s
OK
```

Pod validation used the same RTX A5000 pod, GeoLife pair
`20081023025304.plt` vs `20081026134407.plt`, 8 distance-search iterations,
and 5 repeats per row with oracle verification disabled for timing.

## Corrected Performance Result

| Points per curve | C++ all-cells no-oracle median wall (s) | RTDL/OptiX advisory broadphase + C++ continuation median wall (s) | RT / C++ speed | Broadphase pruning |
| ---: | ---: | ---: | ---: | ---: |
| 128 | 0.014270 | 0.031396 | 0.454x | 0.0% |
| 256 | 0.051883 | 0.128608 | 0.403x | 0.0% |
| 512 | 0.194968 | 0.558547 | 0.349x | 0.98% |

The app now produces matching distance estimates in these runs, but it does not
accelerate this GeoLife pair. The RTDL broadphase sees almost every cell, so
the C++ all-cells baseline remains faster.

## Interpretation

This is a real fix, but not a real Frechet speedup:

- Correctness is protected by the prune-ratio fallback.
- The Python-DP bottleneck is removed from the benchmark path by the optional
  C++ continuation.
- The current RT-shaped broadphase is too weak for these long, nearby GPS
  trajectories.

The next meaningful performance step is not more Python benchmarking. It is a
better algorithmic split, such as:

- a conservative free-space-cell test based on segment distance, not segment
  vs expanded AABB crossing;
- a batched many-trajectory-pair mode that amortizes OptiX launches;
- a native continuation over the candidate free-space graph, if that can be
  expressed without app-specific engine symbols;
- or treating continuous Frechet as a learner/correctness example rather than
  an RT-core speedup demo.

## Boundary

Do not publish a real-dataset continuous Frechet acceleration claim from the
current v1.8 learner app. It is now a better and safer learner app, with a fair
C++ continuation baseline and a guarded RTDL broadphase, but the measured
GeoLife result is still slower than compiled C++ all-cells.
