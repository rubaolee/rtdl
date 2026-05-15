# Archived Milestone Q/A

This page is preserved historical context for maintainers.

It is not part of the primary `v0.7.0` user-learning path and should not be
read as the front-door release summary. For current public status, use:

- [RTDL v0.7 Release Statement](release_reports/v0_7/release_statement.md)
- [RTDL v0.7 Support Matrix](release_reports/v0_7/support_matrix.md)
- [RTDL v0.6 Release Statement](release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](release_reports/v0_6/support_matrix.md)
- [Quick Tutorial](quick_tutorial.md)
- [Tutorials](tutorials/README.md)

Date: 2026-04-09

## What was the strongest RTDL result at that point?

There are now two different “strongest” answers, and both matter.

For the released workload/performance story, the strongest live-branch result
is still the released v0.2 Linux segment/polygon surface:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- parity-clean against PostGIS through accepted large deterministic rows
- RTDL remains ahead of PostGIS on the accepted `x4096` rows

For the new application-story proof, the strongest current v0.3 result is:

- a real 3D RTDL-plus-Python visual demo line
- that line sits on top of the same released `v0.2.0` RTDL core rather than
  replacing the workload/package story
- bounded Linux 3D backend closure across:
  - `embree`
  - `optix`
  - `vulkan`
- a public video entry point for that demo line:
  - [RTDL 4K Visual Demo Video](https://youtu.be/d3yJB7AmCLM)
- a saved work report for that 4K artifact:
  - [Hidden-Star 4K Render Work Report](reports/hidden_star_4k_render_work_report_2026-04-11.md)
- the repo’s primary preserved source artifact for that line:
  - [rtdl_hidden_star_stable_ball_demo.py](../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
- the earlier Linux OptiX and Vulkan smooth-camera support artifacts remain preserved as secondary comparison/support material, not as the primary hidden-star demo outputs

The archived v0.1 `county_zipcode` positive-hit `pip` line remains the trust
anchor and strongest older prepared/repeated raw-input performance story.

## Was Vulkan a failure at that point?

No.

Vulkan is now:

- hardware-validated
- parity-clean on the accepted long exact-source prepared and repeated raw-input
  boundaries
- slower than PostGIS, OptiX, and Embree on those boundaries

So Vulkan is a supported portable backend, not the current main performance
backend.

## What was RTDL doing in Python?

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

- [rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)

Preserved primary source baseline for the stronger current application-style example:

- [rtdl_hidden_star_stable_ball_demo.py](../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)

Preserved stable comparison baseline:

- [rtdl_smooth_camera_orbit_demo.py](../examples/visual_demo/rtdl_smooth_camera_orbit_demo.py)

Preserved moving-light comparison example:

- [rtdl_orbiting_star_ball_demo.py](../examples/visual_demo/rtdl_orbiting_star_ball_demo.py)

## Did the CPU still matter when using OptiX or Vulkan?

Yes.

For the mature positive-hit `pip` story, the accelerator usually does
candidate generation and the CPU exact-finalizes the candidate subset for
trusted final truth.

## Were the internal oracles still important?

Yes.

Accepted oracle trust boundary:

- Python oracle on deterministic mini envelopes
- native C oracle on deterministic small envelopes

They matter for:

- quick verification
- demos
- trustable sanity checks

## Were all RTDL workloads equally mature?

No.

The current strongest mature surfaces are:

- released v0.2 segment/polygon workloads on Linux
- archived v0.1 positive-hit `pip` trust-anchor performance

Other workloads exist and work, but they are not all documented with the same
depth of performance closure yet.

The same applies to the v0.3 demo line:

- the bounded 3D ray/triangle backend surface is closed
- the preferred polished public artifact is currently the Windows Embree movie
- the preferred preserved local counterpart now comes from the hidden-star RTDL-shadow line
- earlier smooth-camera Windows/Linux artifacts remain preserved as comparison/support material
- but the movie itself should not be read as equally optimized across all
  backends

## Why did the reports distinguish prepared and repeated raw-input timing?

Because they measure different things.

- prepared:
  - backend execution after packing/binding work is already done
- repeated raw-input:
  - what ordinary RTDL calls achieve after runtime-owned caching kicks in

Mixing these would make the performance claims misleading.

## Could RTDL honestly claim performance at that point?

Yes, with explicit boundaries.

Safe current claims:

- RTDL backends beat PostGIS on the accepted Linux `x4096` segment/polygon
  rows for:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
- RTDL + OptiX and RTDL + Embree also beat PostGIS on the archived long
  exact-source `county_zipcode` positive-hit `pip` surface under the published
  prepared and repeated raw-input boundaries
