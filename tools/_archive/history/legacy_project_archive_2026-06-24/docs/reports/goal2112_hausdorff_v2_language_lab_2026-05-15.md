# Goal2112: Hausdorff Distance as a v2.0 Language Test

Date: 2026-05-15

Status: implemented and locally validated.

## Purpose

This goal treats RTDL v2.0 as a user-facing programming language/runtime stack,
not as a fixed collection of demos. The test is:

> Can a learner/user write a real exact 2-D Hausdorff Distance program with
> Python+partner+RTDL, validate it against independent C++/CUDA/CuPy baselines,
> and understand which parts do or do not use RT cores?

## Implemented lab

New runner:

`examples/rtdl_hausdorff_v2_language_lab.py`

The lab runs the same generated point sets through six methods:

| Method | Role | Exact? | Uses RTDL? | Uses partner? | Uses RT cores? |
| --- | --- | --- | --- | --- | --- |
| `openmp_cpu` | baseline | yes | no | no | no |
| `cuda_cpp` | baseline | yes | no | no | no |
| `cupy_rawkernel` | baseline | yes | no | yes | no |
| `rtdl_v2_user_cuda` | v2 language path | yes | yes | yes | no |
| `rtdl_rt_threshold_search` | v2 language path | interval | yes | no | yes |
| `rtdl_rt_nearest_witness` | v2 language path | yes | yes | no | yes |

The exact RT nearest-witness path now seeds its witness radius with the RTDL
threshold-search upper bound by default. This is still a user-level algorithmic
choice, not app logic in the engine: the engine exposes generic fixed-radius
decision and nearest-witness primitives, while the Hausdorff reduction remains
in Python.

## Local Linux validation

Host:

- Linux validation host: `192.168.1.20`
- GPU: GTX 1070 smoke host
- OptiX SDK: `/home/lestat/vendor/optix-dev`
- Build artifact: `build/librtdl_optix.so`

Artifacts:

- `docs/reports/hausdorff_v2_language_lab_local_optix_512.json`
- `docs/reports/hausdorff_v2_language_lab_local_optix_2048.json`
- `docs/reports/hausdorff_v2_language_lab_local_optix_8192.json`

All exact methods matched the OpenMP exact reference distance and witness
indices on all three sizes. The RT threshold-search path matched the exact
reference within the configured tolerance.

## Timing summary

These are local GTX 1070 smoke timings, not final release RTX timings.

| Size | OpenMP CPU | CUDA C++ | CuPy | RTDL+CuPy exact | RTDL/OptiX threshold | RTDL/OptiX exact witness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 x 512 | 0.000682 s | 0.001020 s | 0.000532 s | 0.000530 s | 0.539830 s | 0.469941 s |
| 2048 x 2048 | 0.004657 s | 0.001979 s | 0.001438 s | 0.001462 s | 0.639973 s | 0.589204 s |
| 8192 x 8192 | 0.065391 s | 0.010110 s | 0.009502 s | 0.009575 s | 1.075866 s | 1.125322 s |

## Interpretation

The language test passes:

- exact HD can be written as a Python+partner+RTDL v2.0 program;
- the result matches independent OpenMP, CUDA C++, and CuPy baselines;
- the same lab clearly distinguishes non-RT exact partner continuation from
  RTDL/OptiX traversal.

The performance result is more subtle:

- `rtdl_v2_user_cuda` is currently the fastest RTDL v2 exact HD path on this
  local smoke host.
- `rtdl_rt_nearest_witness` is now exact and really uses OptiX traversal, but it
  is not competitive with the CUDA/CuPy exact double-loop baselines on these
  point-cloud cases.
- Threshold seeding improved the exact RT witness path by using a tighter
  search radius instead of the dataset bounding-box diagonal, but it still does
  not implement the main X-HD acceleration layers.

## X-HD guidance for future work

The result confirms the paper's lesson: RT cores alone are not the whole
Hausdorff algorithm. For competitive RT-core HD, a user-level or future-library
algorithm needs:

- grid/cell grouping so traversal tests AABBs for point groups rather than
  point-sized primitives with a broad global radius;
- HD lower/upper estimators and early-break logic;
- reuse of prepared scenes and threshold bounds across both directions;
- heavy-cell CUDA/CuPy continuation when a cell contains too many candidate
  points;
- careful tie and witness rules so exactness remains auditable.

The engine should not gain a Hausdorff-specific primitive. The generic engine
surface that appears useful after this lab is:

- fixed-radius count/coverage decision;
- fixed-radius nearest-witness rows;
- bounded/streaming witness output;
- partner reductions over returned candidate/witness rows.

## Claim boundary

This goal supports a narrow claim:

> RTDL v2.0 can express and validate exact Hausdorff Distance programs, including
> one exact path that uses RTDL/OptiX traversal for nearest-witness discovery.

It does not support:

- a broad RT-core Hausdorff speedup claim;
- a claim that current RTDL matches X-HD;
- a v2.0 release claim by itself.

Those remain blocked pending X-HD-style algorithmic work and pod-scale RTX
evidence.
