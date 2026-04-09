# Docs Index

This directory has two kinds of material:

- **live docs**: the current project story
- **reference/archive docs**: preserved reports, plans, and detailed history

If you are new to RTDL, read the live docs first.

RTDL’s primary target is non-graphical geometric-query work. The visual demo is
best read as a proof-of-capability application built on the same core:

- [Watch The Public Demo Video](https://youtube.com/shorts/O07Mg5luap8)
- [Project Front Page](../README.md)

## Start Here

Project-level front door:

1. [Quick Tutorial](quick_tutorial.md)
2. [RTDL v0.2 User Guide](v0_2_user_guide.md)
3. [RTDL v0.2 Release Reports](release_reports/v0_2/README.md)
4. [RTDL v0.2 Release Statement](release_reports/v0_2/release_statement.md)
5. [RTDL v0.2 Support Matrix](release_reports/v0_2/support_matrix.md)
6. [Release-Facing Examples](release_facing_examples.md)
7. [Feature Homes](features/README.md)
8. [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
9. [Current Milestone Q/A](current_milestone_qa.md)
10. [Future Ray-Tracing Directions](future_ray_tracing_directions.md)
11. [v0.1 Release Notes](v0_1_release_notes.md)
12. [v0.1 Reproduction And Verification](v0_1_reproduction_and_verification.md)
13. [v0.1 Support Matrix](v0_1_support_matrix.md)
14. [v0.1 Release Reports](release_reports/v0_1/README.md)
15. [RTDL v0.1 Archive](archive/v0_1/README.md)
16. [RayJoin Reproduction Performance Report](reports/goal104_rayjoin_reproduction_performance_report_2026-04-05.md)
17. [RayJoin Target](rayjoin_target.md)

Broader background:

1. [v0.1 Plan](v0_1_final_plan.md)
2. [Vision](vision.md)
3. [Dataset Summary](rayjoin_datasets.md)
4. [Public Dataset Sources](rayjoin_public_dataset_sources.md)

Language-level:

1. [RTDL Language Docs Index](rtdl/README.md)
2. [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
3. [Feature Guide](rtdl_feature_guide.md)
4. [Release-Facing Examples](release_facing_examples.md)
5. [Feature Homes](features/README.md)

Process-level:

1. [Development Reliability Process](development_reliability_process.md)
2. [AI Collaboration Workflow](ai_collaboration_workflow.md)
3. [Audit Flow](audit_flow.md)

## Live State Summary

Keep these current facts in mind while reading:

- the accepted bounded package remains the current v0.1 trust anchor
- current `main` is now the released v0.2.0 branch state
- the accepted v0.2 workload surface is exactly:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- RTDL should not be read only as a fixed workload list:
  - users can also write RTDL-plus-Python applications where RTDL provides the
    geometry-query core and Python handles surrounding logic
- the current small demonstration of that model is:
  - [examples/visual_demo/rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)
- the released `v0.2.0` surface remains the stable workload/documentation
  baseline on `main`
- the newer `v0.3` line is an application-style demo layer on top of that
  released core, not a separate replacement release
- the preserved flagship baseline for the stronger current v0.3 application-style demo line is:
  - [examples/visual_demo/rtdl_smooth_camera_orbit_demo.py](../examples/visual_demo/rtdl_smooth_camera_orbit_demo.py)
- the moving-star comparison path is still preserved here:
  - [examples/visual_demo/rtdl_orbiting_star_ball_demo.py](../examples/visual_demo/rtdl_orbiting_star_ball_demo.py)
- the current public-facing entry point for that line is:
  - [RTDL Visual Demo Video](https://youtube.com/shorts/O07Mg5luap8)
- the accepted local `4K` and supporting Linux backend artifacts remain
  preserved in the repo reports, but the front-surface docs now point readers
  to the single public video URL rather than local GIF previews
- current `main` also carries narrow generate-only support for the accepted
  v0.2 surface
- there are now two important performance stories:
  - the v0.1 long exact-source `county_zipcode` positive-hit `pip` trust-anchor
    surface
  - the v0.2 Linux/PostGIS-backed segment/polygon large-row surface through
    `x4096`
- the Jaccard line is supported, but under a narrower pathology/unit-cell
  contract than the segment/polygon families
- the bounded 3D visual-demo ray/triangle line is already closed on Linux
  across:
  - `embree`
  - `optix`
  - `vulkan`
- the polished public movie artifact is currently strongest on Windows Embree
- a finished accepted Windows `4K` artifact now also exists, with an explicitly
  documented temporal-blink caveat, but the preserved public-facing local
  counterpart is the cleaner HD `6s` cut
- Linux OptiX and Vulkan now also have saved small compare-clean supporting
  artifacts for the same visual-demo line
- Embree and OptiX are the mature high-performance backends on the accepted
  v0.1 and segment/polygon performance surfaces
- Vulkan is supported and parity-clean there, but slower
- the Jaccard line now also has Linux wrapper-surface consistency on Embree,
  OptiX, and Vulkan through documented native CPU/oracle fallback
- Linux is the primary validation platform
- this Mac is only a limited local platform
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
- preserved reproduction matrices and older plan docs

Use them when you need detailed historical or goal-specific context.
