# Docs Index

This directory contains two different kinds of material:

- **canonical live docs**: current project guidance and language/runtime docs
- **reference/archive docs**: preserved plans, matrices, and accepted reports

If you want the current project story, read the canonical set first.

## Canonical Live Docs

Project-level:

1. [v0.1 Release Notes](v0_1_release_notes.md)
2. [v0.1 Plan](v0_1_final_plan.md)
3. [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
4. [Current Milestone Q/A](current_milestone_qa.md)
5. [v0.1 Reproduction And Verification](v0_1_reproduction_and_verification.md)
6. [v0.1 Support Matrix](v0_1_support_matrix.md)
7. [Vision](vision.md)
8. [RayJoin Target](rayjoin_target.md)
9. [Dataset Summary](rayjoin_datasets.md)
10. [Public Dataset Sources](rayjoin_public_dataset_sources.md)

Language-level:

1. [RTDL Language Docs Index](rtdl/README.md)
2. [Architecture, API, And Performance Overview](architecture_api_performance_overview.md)
3. [Feature Guide](rtdl_feature_guide.md)

Process-level:

1. [Development Reliability Process](development_reliability_process.md)
2. [AI Collaboration Workflow](ai_collaboration_workflow.md)
3. [Audit Flow](audit_flow.md)

## Reference Material

These are still useful, but they are not the primary current-state narrative:

- `docs/goal_*.md`
- `docs/reports/`
- preserved reproduction matrices and older plan docs

Use them when you need detailed historical or goal-specific context.

Current live state to keep in mind while reading:

- the accepted bounded package remains the current v0.1 trust anchor:
  - `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
  - bounded `LKAU ⊲⊳ PKAU`
  - bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`
- the strongest current performance closure is the long exact-source
  `county_zipcode` positive-hit `pip` surface
- Embree and OptiX are the mature high-performance backends on that surface
- Vulkan is now parity-clean on that same long exact-source surface, but slower
- PostGIS remains the external indexed comparison baseline

Release-facing note:

- older goal reports and older background docs are still important evidence
  sources, but the preferred release-reading path now starts with:
  - `v0_1_release_notes.md`
  - `architecture_api_performance_overview.md`
  - `v0_1_reproduction_and_verification.md`
  - `v0_1_support_matrix.md`
- `rtdl_feature_guide.md` remains useful as background orientation, but the
  architecture/performance overview is the more current technical guide for the
  v0.1 release package
