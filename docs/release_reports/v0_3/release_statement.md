# RTDL v0.3 Release Statement

Date: 2026-04-09
Status: released as `v0.3.0`

## Statement

RTDL v0.3.0 is now released as a bounded extension of the RTDL repository:

- the stable `v0.2.0` workload/package surface remains intact
- the `v0.3.0` line adds a released RTDL-plus-Python application proof layer

This release does **not** redefine RTDL as a rendering engine. It proves,
under bounded and documented scope, that the same RTDL geometric-query core can
sit inside real Python-hosted 3D demo applications.

## What The Release Stands On

The `v0.3.0` release stands on:

- the already released `v0.2.0` workload surface:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- the modularized native backend layer:
  - oracle
  - Embree
  - OptiX
  - Vulkan
- a bounded 3D ray/triangle demo surface closed on Linux across:
  - `embree`
  - `optix`
  - `vulkan`
- a polished Windows Embree public video artifact for the hidden-star RTDL-shadow demo
- supporting Linux OptiX and Vulkan hidden-star artifacts for the same user-level scene
- final code/docs/release-surface audits and external review before tagging

## What The Release Adds

`v0.3.0` adds:

- a clear RTDL-plus-Python application story
- the hidden-star stable Earth demo as the main visual-demo source
- preserved cross-backend 3D demo artifacts
- release-surface cleanup that removes internal goal naming from the public example chain
- a cleaner public `examples/` layout:
  - top-level release-facing examples
  - `examples/reference/`
  - `examples/generated/`
  - `examples/visual_demo/`
  - `examples/internal/`

## What The Release Does Not Claim

RTDL v0.3.0 does not claim:

- that RTDL is a general-purpose rendering engine
- that every backend/workload/application path is equally mature
- that Linux GPU movie artifacts are equally polished as the Windows Embree artifact
- that the visual-demo line replaces the bounded `v0.2.0` workload definition
- exact computational geometry everywhere

## Relationship To v0.2.0

`v0.2.0` remains the stable workload/package core inside this release.

The right reading is:

- `v0.2.0`: stable workload/package surface
- `v0.3.0`: released proof that the same RTDL core can also power bounded Python-hosted applications

## Public-Facing Entry Point

Current public video:

- [RTDL Visual Demo Video](https://youtube.com/shorts/VnzVWAPln3k?si=O1iet-3uFm2gpPes)

Current main 3D demo source:

- [rtdl_hidden_star_stable_ball_demo.py](../../../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
