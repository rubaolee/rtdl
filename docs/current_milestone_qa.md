# Current Milestone Q/A

Date: 2026-04-08

## What is the current strongest RTDL result?

There are now two different “strongest” answers, and both matter.

For the released workload/performance story, the strongest live-branch result
is still the released v0.2 Linux segment/polygon surface:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- parity-clean against PostGIS through accepted large deterministic rows
- RTDL remains ahead of PostGIS on the accepted `x4096` rows

For the new application-story proof, the strongest current v0.3 result is:

- a real 3D RTDL-plus-Python visual demo line
- bounded Linux 3D backend closure across:
  - `embree`
  - `optix`
  - `vulkan`
- a public video entry point for that demo line:
  - [RTDL Visual Demo Video](https://youtu.be/Jfq6VsY-RR4)
- plus an accepted local Windows `4K` artifact preserved in the repo reports
- plus saved small Linux supporting artifacts preserved in the repo reports for:
  - OptiX
  - Vulkan

The archived v0.1 `county_zipcode` positive-hit `pip` line remains the trust
anchor and strongest older prepared/repeated raw-input performance story.

## Is Vulkan a failure?

No.

Vulkan is now:

- hardware-validated
- parity-clean on the accepted long exact-source prepared and repeated raw-input
  boundaries
- slower than PostGIS, OptiX, and Embree on those boundaries

So Vulkan is a supported portable backend, not the current flagship performance
backend.

## What is RTDL doing in Python?

Python owns:

- DSL authorship
- lowering/orchestration
- dataset ingestion
- cache management
- public API boundaries
- user application logic around RTDL kernels when needed

Recent performance work explicitly reduced Python hot-path cost by reusing
prepared and prepacked geometry automatically.

RTDL also already works well with Python user applications where:

- RTDL provides the geometry-query core
- Python provides grouping, summaries, reports, or visual output

Small example:

- [rtdl_lit_ball_demo.py](../examples/rtdl_lit_ball_demo.py)

Stronger current application-style example:

- [rtdl_orbiting_star_ball_demo.py](../examples/rtdl_orbiting_star_ball_demo.py)

## Does the CPU still matter when using OptiX or Vulkan?

Yes.

For the mature positive-hit `pip` story, the accelerator usually does
candidate generation and the CPU exact-finalizes the candidate subset for
trusted final truth.

## Are the internal oracles still important?

Yes.

Accepted oracle trust boundary:

- Python oracle on deterministic mini envelopes
- native C oracle on deterministic small envelopes

They matter for:

- quick verification
- demos
- trustable sanity checks

## Are all RTDL workloads equally mature?

No.

The current strongest mature surfaces are:

- released v0.2 segment/polygon workloads on Linux
- archived v0.1 positive-hit `pip` trust-anchor performance

Other workloads exist and work, but they are not all documented with the same
depth of performance closure yet.

The same applies to the v0.3 demo line:

- the bounded 3D ray/triangle backend surface is closed
- the preferred polished public artifact is currently the Windows Embree movie
- a finished Windows `4K` movie is now also accepted, but with an explicit
  left-bottom blink caveat
- Linux OptiX and Vulkan now also have saved small compare-clean supporting
  GIF artifacts
- but the movie itself should not be read as equally optimized across all
  backends

## Why do the reports distinguish prepared and repeated raw-input timing?

Because they measure different things.

- prepared:
  - backend execution after packing/binding work is already done
- repeated raw-input:
  - what ordinary RTDL calls achieve after runtime-owned caching kicks in

Mixing these would make the performance claims misleading.

## Can RTDL honestly claim performance now?

Yes, with explicit boundaries.

Safe current claims:

- RTDL backends beat PostGIS on the accepted Linux `x4096` segment/polygon
  rows for:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
- RTDL + OptiX and RTDL + Embree also beat PostGIS on the archived long
  exact-source `county_zipcode` positive-hit `pip` surface under the published
  prepared and repeated raw-input boundaries
