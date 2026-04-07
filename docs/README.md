# Docs Index

This directory has two kinds of material:

- **live docs**: the current project story
- **reference/archive docs**: preserved reports, plans, and detailed history

If you are new to RTDL, read the live docs first.

## Start Here

Project-level front door:

1. [RTDL v0.2 User Guide](v0_2_user_guide.md)
2. [v0.1 Release Notes](v0_1_release_notes.md)
3. [Quick Tutorial](quick_tutorial.md)
4. [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
5. [v0.1 Reproduction And Verification](v0_1_reproduction_and_verification.md)
6. [v0.1 Support Matrix](v0_1_support_matrix.md)
7. [v0.1 Release Reports](release_reports/v0_1/README.md)
8. [RTDL v0.1 Archive](archive/v0_1/README.md)
9. [RayJoin Reproduction Performance Report](reports/goal104_rayjoin_reproduction_performance_report_2026-04-05.md)
10. [Current Milestone Q/A](current_milestone_qa.md)
11. [RayJoin Target](rayjoin_target.md)
12. [Future Ray-Tracing Directions](future_ray_tracing_directions.md)

Broader background:

1. [v0.1 Plan](v0_1_final_plan.md)
2. [Vision](vision.md)
3. [Dataset Summary](rayjoin_datasets.md)
4. [Public Dataset Sources](rayjoin_public_dataset_sources.md)

Language-level:

1. [RTDL Language Docs Index](rtdl/README.md)
2. [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
3. [Feature Guide](rtdl_feature_guide.md)

Process-level:

1. [Development Reliability Process](development_reliability_process.md)
2. [AI Collaboration Workflow](ai_collaboration_workflow.md)
3. [Audit Flow](audit_flow.md)

## Live State Summary

Keep these current facts in mind while reading:

- the accepted bounded package remains the current v0.1 trust anchor
- current `main` also carries two closed v0.2 segment/polygon workload families
  and their narrow generate-only support
- the strongest current performance closure is the long exact-source
  `county_zipcode` positive-hit `pip` surface
- Embree and OptiX are the mature high-performance backends on that surface
- Vulkan is supported and parity-clean there, but slower
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
