# Goal 14 Estimation Report: Five-Minute Section 5.6 Local Profiles

## Goal Definition

Goal 14 now narrows the current paper-reproduction work to one practical question only: what Section 5.6 profile sizes let `lsi` and `pip` finish in about **five minutes each** on the current Mac while preserving the paper's two-distribution, five-point experiment shape?

This document is an **estimation report**, not a completion claim for a full paper-scale run.

## Current Machine

- Platform: `macOS-26.3-arm64-arm-64bit-Mach-O`
- Chip: `Apple M4`
- Logical cores: `10`
- Physical cores: `10`
- Memory: `16.0 GiB`

## Paper Target Context

- Fixed build-side polygons: `R = 5,000,000`
- Probe-side series: `S = 1,000,000 .. 5,000,000`
- Distributions: `uniform`, `gaussian`
- Workloads: `lsi` and `pip`
- Planned paper-style launch count per case in this estimate: `1 warmup + 5 measured iterations`

## Estimation Method

The estimate is derived from the current accepted Section 5.6 Embree analogue (`R = 800`, `S = 160..800`) and converted to the paper scale using a conservative logarithmic build-size adjustment.

Two separate rates are used:

- `lsi`: seconds per probe segment from the largest measured case in each distribution, then scaled from `R = 800` to `R = 5,000,000` using a log build-size factor.
- `pip`: seconds per probe point from the largest measured case in each distribution, scaled by the same log build-size factor.

Current build-size adjustment factor from `800` to `5,000,000`: `2.31x`

## Query-Time Estimate

| Workload | Distribution | S polygons | Mean query estimate | Case estimate with 1 warmup + 5 measured runs |
| --- | --- | ---: | ---: | ---: |
| `lsi` | `uniform` | 1,000,000 | 0.00 h | 0.02 h |
| `pip` | `uniform` | 1,000,000 | 0.22 h | 1.29 h |
| `lsi` | `uniform` | 2,000,000 | 0.01 h | 0.04 h |
| `pip` | `uniform` | 2,000,000 | 0.43 h | 2.59 h |
| `lsi` | `uniform` | 3,000,000 | 0.01 h | 0.06 h |
| `pip` | `uniform` | 3,000,000 | 0.65 h | 3.88 h |
| `lsi` | `uniform` | 4,000,000 | 0.01 h | 0.08 h |
| `pip` | `uniform` | 4,000,000 | 0.86 h | 5.17 h |
| `lsi` | `uniform` | 5,000,000 | 0.02 h | 0.10 h |
| `pip` | `uniform` | 5,000,000 | 1.08 h | 6.47 h |
| `lsi` | `gaussian` | 1,000,000 | 0.01 h | 0.05 h |
| `pip` | `gaussian` | 1,000,000 | 0.20 h | 1.21 h |
| `lsi` | `gaussian` | 2,000,000 | 0.02 h | 0.09 h |
| `pip` | `gaussian` | 2,000,000 | 0.40 h | 2.41 h |
| `lsi` | `gaussian` | 3,000,000 | 0.02 h | 0.14 h |
| `pip` | `gaussian` | 3,000,000 | 0.60 h | 3.62 h |
| `lsi` | `gaussian` | 4,000,000 | 0.03 h | 0.18 h |
| `pip` | `gaussian` | 4,000,000 | 0.80 h | 4.83 h |
| `lsi` | `gaussian` | 5,000,000 | 0.04 h | 0.23 h |
| `pip` | `gaussian` | 5,000,000 | 1.01 h | 6.03 h |

## Overnight Runtime Summary

- Estimated total `lsi` query wall time for all `uniform + gaussian` Section 5.6 cases: `0.97 h`
- Estimated total `pip` query wall time for all `uniform + gaussian` Section 5.6 cases: `37.50 h`
- Estimated total query wall time for the combined Goal 14 exact-scale Section 5.6 run: `38.47 h`

These numbers exclude Python-side data construction, Embree scene build time, file serialization, OS memory pressure, and thermal throttling. On this fanless MacBook Air, they should be treated as optimistic lower bounds.

## Memory and Feasibility Estimate

The current RTDL path materializes Python objects before Embree sees the data. That is the main blocker for exact-scale repetition on this machine.

| Artifact | Count at paper scale | Rough current-Python footprint |
| --- | ---: | ---: |
| Build polygons | 5,000,000 | 2.79 GiB |
| LSI build segments | 20,000,000 | 3.20 GiB |
| PIP probe points at `S=5M` | 5,000,000 | 0.58 GiB |
| Probe polygons at `S=5M` | 5,000,000 | 2.79 GiB |
| LSI probe segments at `S=5M` | 20,000,000 | 3.20 GiB |

Interpretation:

- `lsi` exact-scale cases are likely to exceed safe memory on this 16 GiB machine once Python objects, tuples, IDs, derived segments, native buffers, and Embree acceleration structures are all present.
- `pip` exact-scale cases may fit at the low end of the size series, but the upper sizes are still likely to trigger heavy memory pressure or swap.
- Because the host-side object model is the bottleneck, the exact-scale run is **not currently reliable enough to schedule as-is**, even overnight.

## Can We Measure CPU vs GPU RT-Hardware Difference On This Mac?

Not with the current repository.

Why not:

- RTDL currently has `run_cpu(...)` and `run_embree(...)`, both CPU-side paths.
- There is no implemented Mac GPU ray-tracing backend in the repo today.
- Therefore the current codebase cannot produce a trustworthy CPU-vs-GPU-RT comparison on this machine.

What would be required to know that difference:

1. Implement a GPU backend with the same Section 5.6 generator and metrics contract.
2. Record build time, query time, and total wall time separately for CPU and GPU runs.
3. Run identical seeds, distributions, size series, and iteration counts on both backends.
4. Generate the same figure/report schema for direct comparison.

## Recommended Five-Minute Profiles

If the immediate objective is to keep both workloads near a five-minute query-only budget on this Mac, the following scaled profiles are the current recommended starting points:

- `lsi` recommendation: fixed `R = 100,000` polygons, varying `S = 100,000, 200,000, 300,000, 400,000, 500,000` polygons.
  - estimated total query-only time: `0.07 h`
  - estimated total query-only time in minutes: `4.34 min`
  - rationale: this is the largest five-point `lsi` series that still stays under the five-minute query-only target under the current calibration model.
  - caution: this is still an estimate; total wall time can be higher if Python materialization and background Mac usage add overhead.

- `pip` recommendation: fixed `R = 100,000` polygons, varying `S = 2,000, 4,000, 6,000, 8,000, 10,000` polygons.
  - estimated total query-only time: `0.06 h`
  - estimated total query-only time in minutes: `3.36 min`
  - rationale: this is the largest five-point `pip` series that stays near the five-minute query-only target under the current calibration model.
  - this profile is much smaller than paper scale because the current PIP path is substantially more expensive on this CPU-only Embree baseline.

## Practical Recommendation

Goal 14 should remain a **scaled local-execution** goal for now. The accepted next step is to run these five-minute profiles, not the paper-scale exact-size series. Before attempting exact-scale midnight runs on this Mac, RTDL would still need:

- packed or memory-mapped numeric dataset generation instead of Python object materialization,
- chunked probe processing so the build side can stay fixed while probe batches stream through Embree,
- separate reporting for generation time, Embree build time, and query time,
- and calibration runs at `100k`, `250k`, `500k`, and `1M` to validate the model before attempting `5M`.

## Bottom Line

- The current RTDL implementation does **not** yet support a trustworthy exact-size repetition of RayJoin Section 5.6 on this Mac.
- The full paper-scale query-only estimate is still roughly `0.97 h` for LSI and `37.50 h` for PIP across the complete Section 5.6 run.
- The practical Goal 14 target is now the five-minute local profile: `4.34 min` estimated query-only for LSI and `3.36 min` estimated query-only for PIP.
- The reliable next step is to run those scaled local profiles and record real wall-clock behavior on this Mac.
