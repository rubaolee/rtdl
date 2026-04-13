# Docs Index

This directory contains both live docs and preserved history.

If you are new to RTDL, do not start by browsing everything here. Start with
the current live path only.

## New User Path

Read these in order:

1. [Project Front Page](../README.md)
2. [Quick Tutorial](quick_tutorial.md)
3. [RTDL Tutorials](tutorials/README.md)
4. [Release-Facing Examples](release_facing_examples.md)
5. [v0.5 Release Statement](release_reports/v0_5/release_statement.md)
6. [v0.5 Support Matrix](release_reports/v0_5/support_matrix.md)

That is the intended public reading path.

## Environment Facts

- the checkout root is expected to be the current working directory for example
  commands
- the local Python package imported by examples is `rtdsl`
- Bash/zsh examples use `PYTHONPATH=src:. python ...`
- Windows `cmd.exe` examples use `set PYTHONPATH=src;.` before `python ...`
- Windows PowerShell examples use:
  - `$env:PYTHONPATH = "src;."`
  - then `python ...`
- Python `3.10+` is the expected floor

## Live Documentation

- [Quick Tutorial](quick_tutorial.md)
- [RTDL Tutorials](tutorials/README.md)
- [Release-Facing Examples](release_facing_examples.md)
- [v0.4 Application Examples](v0_4_application_examples.md)
- [RTDL Language Docs Index](rtdl/README.md)
- [Feature Homes](features/README.md)
- [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
- [Workloads And Research Foundations](workloads_and_research_foundations.md)
- [v0.5 Release Package](release_reports/v0_5/README.md)
- [v0.5 Release Statement](release_reports/v0_5/release_statement.md)
- [v0.5 Support Matrix](release_reports/v0_5/support_matrix.md)
- [v0.4 Release Package](release_reports/v0_4/README.md)
- [v0.4 Release Statement](release_reports/v0_4/release_statement.md)
- [v0.4 Support Matrix](release_reports/v0_4/support_matrix.md)

## Release Packages

- [v0.5 Release Package](release_reports/v0_5/README.md)
- [v0.5 Preview Package](release_reports/v0_5_preview/README.md)
- [v0.4 Release Package](release_reports/v0_4/README.md)
- [v0.3 Release Package](release_reports/v0_3/README.md)
- [v0.2 Release Package](release_reports/v0_2/README.md)
- [v0.1 Release Package](release_reports/v0_1/README.md)

## Historical And Maintainer Material

Use these only when you need deeper history, audit trails, or process detail:

- [Process Docs](ai_collaboration_workflow.md)
- [Audit Flow](audit_flow.md)
- [Historical Reports](reports/)
- [Older Release Archives](archive/v0_1/README.md)
- [Preserved Wiki Drafts](wiki_drafts/README.md)

## Live State Summary

Keep these current facts in mind while reading:

- current released version is `v0.5.0`
- current `main` carries the released `v0.5.0` line
- the accepted v0.2 workload surface is exactly:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- the earlier released engineering line on `main` was the `v0.4` nearest-neighbor surface:
  - `fixed_radius_neighbors`
  - `knn_rows`
- the released `v0.5.0` additions on `main` are:
  - `bounded_knn_rows`
  - 3D point nearest-neighbor support
  - Linux backend closure across CPU/oracle, Embree, OptiX, and Vulkan
- the released `v0.2.0` surface remains the stable workload/documentation
  baseline on `main`
- the released `v0.3.0` line is an application-style demo layer on top of that
  same released core, not a replacement for the bounded `v0.2.0` workload surface
- RTDL should not be read only as a fixed workload list:
  - users can also write RTDL-plus-Python applications where RTDL provides the
    accelerated compute/query core and Python handles surrounding logic
- the public example tree is now organized as:
  - top-level release-facing examples
  - `examples/reference/`
  - `examples/generated/`
  - `examples/visual_demo/`
  - `examples/internal/`
- the current small demonstration of that model is:
  - [examples/visual_demo/rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)
- the primary preserved source for the v0.3 visual demo line is:
  - [examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py](../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
- the public-facing entry point for that visual line is:
  - [RTDL 4K Visual Demo Video](https://youtu.be/d3yJB7AmCLM)
- the saved work report for that 4K artifact is:
  - [Hidden-Star 4K Render Work Report](reports/hidden_star_4k_render_work_report_2026-04-11.md)
- there are two important performance stories preserved in the repo history:
  - the v0.1 exact-source `county_zipcode` positive-hit `pip` trust-anchor
  - the v0.2 Linux/PostGIS-backed segment/polygon large-row surface
- the Jaccard line is supported under a narrower pathology/unit-cell contract
  than the segment/polygon families
- the bounded 3D visual-demo ray/triangle line is closed on Linux across:
  - `embree`
  - `optix`
  - `vulkan`
- Linux is the primary validation platform
- macOS is only a limited local platform
- PostGIS remains the external indexed comparison baseline
- the motivating application target is RayJoin:
  - Liang Geng, Rubao Lee, and Xiaodong Zhang,
    *RayJoin: Fast and Precise Spatial Join*,
    ICS 2024,
    DOI `10.1145/3650200.3656610`

## Reference Material

These are still useful, but they are not the primary current-state narrative:

- `docs/goal_*.md`
- `docs/reports/`
- older release packages
- preserved historical artifacts

Use them when you need detailed historical or goal-specific context.
