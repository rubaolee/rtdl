# Goal 14 Estimation Report: Exact-Scale Section 5.6 on the Current Mac

## Goal Definition

Goal 14 narrows the current paper-reproduction work to one question only: can RTDL repeat RayJoin Section 5.6 with the **same nominal data sizes** on the current Mac, and if so, what should we expect for runtime and interpretability?

This document is an **estimation report**, not a completion claim for the exact-scale run.

## Current Machine

- Platform: `macOS-26.3-arm64-arm-64bit-Mach-O`
- Chip: `Apple M4`
- Logical cores: `10`
- Physical cores: `10`
- Memory: `16.0 GiB`

## Paper Target

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
| `lsi` | `uniform` | 1,000,000 | 0.01 h | 0.03 h |
| `pip` | `uniform` | 1,000,000 | 0.29 h | 1.76 h |
| `lsi` | `uniform` | 2,000,000 | 0.01 h | 0.07 h |
| `pip` | `uniform` | 2,000,000 | 0.59 h | 3.52 h |
| `lsi` | `uniform` | 3,000,000 | 0.02 h | 0.10 h |
| `pip` | `uniform` | 3,000,000 | 0.88 h | 5.29 h |
| `lsi` | `uniform` | 4,000,000 | 0.02 h | 0.14 h |
| `pip` | `uniform` | 4,000,000 | 1.17 h | 7.05 h |
| `lsi` | `uniform` | 5,000,000 | 0.03 h | 0.17 h |
| `pip` | `uniform` | 5,000,000 | 1.47 h | 8.81 h |
| `lsi` | `gaussian` | 1,000,000 | 0.01 h | 0.03 h |
| `pip` | `gaussian` | 1,000,000 | 0.33 h | 1.95 h |
| `lsi` | `gaussian` | 2,000,000 | 0.01 h | 0.07 h |
| `pip` | `gaussian` | 2,000,000 | 0.65 h | 3.90 h |
| `lsi` | `gaussian` | 3,000,000 | 0.02 h | 0.10 h |
| `pip` | `gaussian` | 3,000,000 | 0.98 h | 5.85 h |
| `lsi` | `gaussian` | 4,000,000 | 0.02 h | 0.13 h |
| `pip` | `gaussian` | 4,000,000 | 1.30 h | 7.81 h |
| `lsi` | `gaussian` | 5,000,000 | 0.03 h | 0.17 h |
| `pip` | `gaussian` | 5,000,000 | 1.63 h | 9.76 h |

## Overnight Runtime Summary

- Estimated total `lsi` query wall time for all `uniform + gaussian` Section 5.6 cases: `1.01 h`
- Estimated total `pip` query wall time for all `uniform + gaussian` Section 5.6 cases: `55.70 h`
- Estimated total query wall time for the combined Goal 14 exact-scale Section 5.6 run: `56.71 h`

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

## Practical Recommendation

Goal 14 should remain an **estimation and readiness** goal for now. Before attempting exact-scale midnight runs on this Mac, RTDL should first add:

- packed or memory-mapped numeric dataset generation instead of Python object materialization,
- chunked probe processing so the build side can stay fixed while probe batches stream through Embree,
- separate reporting for generation time, Embree build time, and query time,
- and calibration runs at `100k`, `250k`, `500k`, and `1M` to validate the model before attempting `5M`.

## Bottom Line

- The current RTDL implementation does **not** yet support a trustworthy exact-size repetition of RayJoin Section 5.6 on this Mac.
- If the host-side memory model were removed as a blocker, the query-only estimate is roughly `1.01 h` for LSI and `55.70 h` for PIP across the full paper-style run.
- The reliable next step is not the midnight run itself; it is refactoring the Section 5.6 path so exact-scale inputs can be generated and consumed without Python-object explosion.
