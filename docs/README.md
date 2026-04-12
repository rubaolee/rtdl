# Docs Index

This directory has two kinds of material:

- **live docs**: the current project story
- **reference/archive docs**: preserved reports, plans, and detailed history

If you are new to RTDL, read the live docs first.

Quick environment facts before you start:

- this checkout currently identifies itself as `v0.4.0`
- the live released surface on `main` is now the `v0.4` nearest-neighbor line
- clone the repo as `rtdl`
- the local Python package imported by the examples is `rtdsl`
- `PYTHONPATH=src:.` is what makes `src/rtdsl/` importable from the checkout
- Python `3.10+` is the expected floor
- `numpy` is recommended for the smoother demo/application examples

RTDL’s current released surface is strongest on geometric and nearest-neighbor
workloads, but the language/runtime goal is broader than those workloads
alone. The visual demo is best read as a proof-of-capability application built
on the same core:

- [Watch The Public 4K Demo Video](https://youtu.be/d3yJB7AmCLM)
- [Project Front Page](../README.md)

## Start Here

Project-level front door:

1. [Quick Tutorial](quick_tutorial.md)
2. [Tutorials](tutorials/README.md)
3. [RTDL v0.2 User Guide](v0_2_user_guide.md)
4. [Release-Facing Examples](release_facing_examples.md)
5. [v0.4 Application Examples](v0_4_application_examples.md)
6. [Feature Homes](features/README.md)
7. [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
8. [Workloads And Research Foundations](workloads_and_research_foundations.md)
9. [RTDL v0.3 Release Reports](release_reports/v0_3/README.md)
10. [RTDL v0.3 Release Statement](release_reports/v0_3/release_statement.md)
11. [RTDL v0.3 Support Matrix](release_reports/v0_3/support_matrix.md)
12. [RTDL v0.4 Release Package](release_reports/v0_4/README.md)
13. [RTDL v0.4 Release Statement](release_reports/v0_4/release_statement.md)
14. [RTDL v0.4 Support Matrix](release_reports/v0_4/support_matrix.md)
15. [RTDL v0.4 Preview Package](release_reports/v0_4_preview/README.md)
16. [RTDL v0.4 Preview Release Statement](release_reports/v0_4_preview/release_statement.md)
17. [RTDL v0.4 Preview Support Matrix](release_reports/v0_4_preview/support_matrix.md)
18. [RTDL v0.2 Release Statement](release_reports/v0_2/release_statement.md)
19. [RTDL v0.2 Support Matrix](release_reports/v0_2/support_matrix.md)
20. [RTDL v0.2 Release Reports](release_reports/v0_2/README.md)
21. [Future Ray-Tracing Directions](future_ray_tracing_directions.md)
22. [v0.1 Release Notes](v0_1_release_notes.md)
23. [v0.1 Reproduction And Verification](v0_1_reproduction_and_verification.md)
24. [v0.1 Support Matrix](v0_1_support_matrix.md)
25. [v0.1 Release Reports](release_reports/v0_1/README.md)
26. [RTDL v0.1 Archive](archive/v0_1/README.md)
27. [RayJoin Target](rayjoin_target.md)

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

Historical and maintainer-facing context:

1. [v0.4 GPU Status Refresh](goal_220_v0_4_gpu_status_refresh.md)
2. [Archived Milestone Q/A](current_milestone_qa.md)
3. [RayJoin Reproduction Performance Report](reports/goal104_rayjoin_reproduction_performance_report_2026-04-05.md)

Imported historical artifacts:

1. [History Capture And External Artifact Import (2026-04-10)](reports/history_capture_external_artifacts_2026-04-10.md)
2. [External Gemini v0.3 Final Audit Report](reports/RTDL_v0_3_Final_Audit_Report_2026-04-09_external.md)
3. [External Gemini Wiki Generation Report](reports/RTDL_Wiki_Generation_Report_2026-04-09_external.md)
4. [External Claude v0.4 Code Audit](reports/rtdl_v0_4_code_audit_2026-04-10_external.md)
5. [External Raw Reports](reports/external_raw/README.md)
6. [Preserved Wiki Drafts](wiki_drafts/README.md)

## Live State Summary

Keep these current facts in mind while reading:

- current `main` is now the released `v0.4.0` branch state
- the accepted v0.2 workload surface is exactly:
  - `segment_polygon_hitcount`
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- the live released engineering line on `main` is now the `v0.4` nearest-neighbor surface:
  - `fixed_radius_neighbors`
  - `knn_rows`
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
- preserved reproduction matrices and older plan docs

Use them when you need detailed historical or goal-specific context.
