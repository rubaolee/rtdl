# Docs Index

This directory contains both live docs and preserved history.

If you are new to RTDL, do not start by browsing everything here. Start with
the current live path only.

## New User Path

Read these in order:

1. [Project Front Page](../README.md)
2. [Current Architecture](current_architecture.md)
3. [Capability Boundaries](capability_boundaries.md)
4. [Quick Tutorial](quick_tutorial.md)
5. [RTDL Tutorials](tutorials/README.md)
6. [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md)
7. [Release-Facing Examples](release_facing_examples.md)
8. [v0.7 Release Statement](release_reports/v0_7/release_statement.md)
9. [v0.7 Support Matrix](release_reports/v0_7/support_matrix.md)

If you need the previous graph release line, also read:

10. [v0.6 Release Statement](release_reports/v0_6/release_statement.md)
11. [v0.6 Support Matrix](release_reports/v0_6/support_matrix.md)

That is the intended public reading path.

## Evaluate RTDL In Ten Minutes

If your question is "does RTDL make my ray-tracing-style workload easier to
write?", use this short path:

1. read [Current Architecture](current_architecture.md) for the user contract
2. run [Quick Tutorial](quick_tutorial.md)
3. choose a feature from [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md)
4. run one runnable example from [Release-Facing Examples](release_facing_examples.md)
5. check the exact backend boundary in the [v0.7 Support Matrix](release_reports/v0_7/support_matrix.md)

The public promise is authoring-burden reduction: RTDL hides backend-specific
traversal and result plumbing behind one kernel shape while preserving bounded,
audited release claims.

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
- [Current Architecture](current_architecture.md)
- [Capability Boundaries](capability_boundaries.md)
- [RTDL Tutorials](tutorials/README.md)
- [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md)
- [Release-Facing Examples](release_facing_examples.md)
- [RTDL Language Docs Index](rtdl/README.md)
- [Feature Homes](features/README.md)
- [Workloads And Research Foundations](workloads_and_research_foundations.md)
- [v0.6 Release Package](release_reports/v0_6/README.md)
- [v0.6 Release Statement](release_reports/v0_6/release_statement.md)
- [v0.6 Support Matrix](release_reports/v0_6/support_matrix.md)
- [v0.7 Release Package](release_reports/v0_7/README.md)
- [v0.7 Release Statement](release_reports/v0_7/release_statement.md)
- [v0.7 Support Matrix](release_reports/v0_7/support_matrix.md)
- [Complete History Map](../history/COMPLETE_HISTORY.md)

## Release Packages

- [v0.6 Release Package](release_reports/v0_6/README.md)
- [v0.7 Release Package](release_reports/v0_7/README.md)
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
- [Historical Architecture Overview](architecture_api_performance_overview.md)
- [Historical v0.4 Application Examples](v0_4_application_examples.md)
- [Historical Reports](reports/)
- [Complete History Map](../history/COMPLETE_HISTORY.md)
- [Current v0.7 Goal Sequence](history/goals/v0_7_goal_sequence_2026-04-15.md)
- [Historical Goal Archive](history/goals/archive/)
- [Historical Docs Tree](history/)
- [Older Release Archives](archive/v0_1/README.md)
- [Archive Index](archive/README.md)
- [Historical Engineering Handoffs](engineering/handoffs/V0_4_FINAL_RELEASE_HANDOFF_HUB.md)
- [Preserved Wiki Drafts](wiki_drafts/README.md)

## Live State Summary

Keep these current facts in mind while reading:

- current released version is `v0.7.0`
- current `main` carries the released bounded `v0.7.0` DB line
- the previous released graph line was `v0.6.1`
- the accepted v0.2 workload surface is exactly:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- the earlier released engineering line on `main` was the `v0.4` nearest-neighbor surface:
  - `fixed_radius_neighbors`
  - `knn_rows`
- the released `v0.5` nearest-neighbor expansion added:
  - `bounded_knn_rows`
  - 3D nearest-neighbor support across the accepted backend matrix
- the released `v0.6.1` additions on `main` are:
  - `bfs`
  - `triangle_count`
  - RTDL-kernel graph execution across CPU/oracle, Embree, OptiX, and Vulkan
  - PostgreSQL-backed graph correctness anchoring
- the bounded `v0.7.0` DB release line adds:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
  - Embree / OptiX / Vulkan RT backends for that first bounded DB family
  - native prepared DB dataset reuse on Embree, OptiX, and Vulkan
  - PostgreSQL-backed cross-engine correctness on Linux
  - PostgreSQL-inclusive repeated-query performance gates on Linux
  - app-level and kernel-form v0.7 DB demos
  - release-readiness and staging-authorization evidence through Goal 492
  - the final `v0.7.0` release action recorded after explicit user authorization
- the released `v0.2.0` surface remains a stable historical
  workload/documentation baseline
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
- PostgreSQL remains the main external correctness baseline for the graph line
  and the bounded `v0.7.0` DB release line
- the current bounded v0.7 line is released as `v0.7.0`; claims remain bounded
  by the v0.7 release reports
- PostGIS remains part of the earlier non-graph release history
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
