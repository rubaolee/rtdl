# Goal2301 Bounded Closed-Shape Point Probe

Date: 2026-05-17

## Purpose

Goal2295 showed that the current prepared closed-shape membership path was
dominated by OptiX candidate traversal/write time, not Python packing, upload,
or host exact refinement. Goal2299 then rejected the older boundary
ray/segment parity route as an exact but far slower fallback.

This goal tests and accepts a generic engine-side improvement for the current
closed-shape membership primitive: replace the infinite upward point probe with
a bounded vertical probe segment through the query point. The primitive remains
app-agnostic. It still uses point, closed-shape, membership, and positive-row
vocabulary; it does not add RayJoin, PIP, polygon, map, county, or join-specific
logic to the native API.

## Change

The OptiX PIP/closed-shape raygen program now traces a bounded vertical segment
from `py - 0.5` to `py + 0.5` instead of a ray with `tmax = 1.0e30`.

Rationale:

- Closed-shape membership only needs shapes whose AABB contains or locally
  crosses the query point.
- The old infinite vertical ray could traverse many shape AABBs above the
  point before the device prefilter rejected them.
- The bounded probe keeps the RT-core traversal contract but sharply narrows
  the candidate space for point-membership workloads.
- Host GEOS exact refinement remains the final inclusive truth source.

## Pod Evidence

Pod:

- SSH: `root@69.30.85.202 -p 22064`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Base commit: `9d159de6ae551f8f669cf0d44fd77e0b37e2eab9`
- Candidate source state: `9d159de6` plus the one-line bounded-probe source
  diff now committed by this goal.
- Build:
  `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8`
- Runtime:
  `PYTHONPATH=src:.`,
  `RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so`,
  `CUDA_HOME=/usr/local/cuda-12.8`,
  `RTDL_OPTIX_PTX_ARCH=compute_86`,
  `RTDL_OPTIX_PTX_COMPILER=nvcc`,
  `RTDL_NVCC=/usr/local/cuda-12.8/bin/nvcc`

Artifacts:

- `docs/reports/goal2301_bounded_point_probe_baseline_current_pod_2026-05-17.json`
- `docs/reports/goal2301_bounded_point_probe_candidate_pod_2026-05-17.json`
- `docs/reports/goal2301_bounded_point_probe_candidate_pip_count_phase_pod_2026-05-17.json`
- `docs/reports/goal2301_short_origin_inside_negative_pod_2026-05-17.json`
- `docs/reports/goal2301_tiny_crossing_negative_pod_2026-05-17.json`

## Result

Same 100,000-query RayJoin-exported PIP stream, same prepared
`point_closed_shape_membership_2d_optix` route, same expected exact count
`8686`.

| Mode | Current baseline median | Bounded probe median | Speedup |
| --- | ---: | ---: | ---: |
| Positive rows | 0.051157122 s | 0.018218992 s | 2.808x |
| Scalar count | 0.037854942 s | 0.007748827 s | 4.885x |

Candidate row/count values were stable across all seven repeats:

- Positive rows: `8686`
- Scalar count: `8686`
- `matches_prior_expected_count`: `true`

The focused count-phase artifact shows why this works:

- Raw candidate count: `8798`
- Emitted exact count: `8686`
- Candidate traversal/write phase: about `0.0031 s`
- Exact refine phase after warmup: about `0.0044 s`

Compared with Goal2295's current baseline, candidate traversal/write drops from
about `0.0375 s` to about `0.0031 s` while preserving exact output.

## Rejected Variants

Two more aggressive bounded probes were tested first and rejected:

- Origin-inside tiny segment: `py`, `tmax = 1.0e-5`.
- Tiny crossing segment: `py - 1.0e-4`, `tmax = 2.0e-4`.

Both returned zero PIP positives on the 100,000-query pod stream. That means
the final accepted probe must remain a real bounded segment, not a mathematical
point/epsilon query.

## Boundary

Accepted claim:

- For the measured RayJoin-exported 100,000-query PIP stream, the generic
  prepared closed-shape membership OptiX route is faster with the bounded point
  probe while preserving exact count parity.

Not claimed:

- No RayJoin paper reproduction.
- No claim that RTDL beats RayJoin.
- No broad whole-app acceleration claim.
- No true zero-copy claim.
- No v2.0 release authorization.

