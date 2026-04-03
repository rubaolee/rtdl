# Docs Index

This directory contains two different kinds of material:

- **canonical live docs**: current project guidance and language/runtime docs
- **reference/archive docs**: preserved plans, matrices, and accepted reports

If you want the current project story, read the canonical set first.

## Canonical Live Docs

Project-level:

1. [Vision](vision.md)
2. [v0.1 Plan](v0_1_final_plan.md)
3. [RayJoin Target](rayjoin_target.md)
4. [Dataset Summary](rayjoin_datasets.md)
5. [Public Dataset Sources](rayjoin_public_dataset_sources.md)

Language-level:

1. [RTDL Language Docs Index](rtdl/README.md)
2. [Feature Guide](rtdl_feature_guide.md)

Process-level:

1. [Development Reliability Process](development_reliability_process.md)
2. [AI Collaboration Workflow](ai_collaboration_workflow.md)

## Reference Material

These are still useful, but they are not the primary current-state narrative:

- `docs/goal_*.md`
- `docs/reports/`
- preserved reproduction matrices and older plan docs

Use them when you need detailed historical or goal-specific context.

Current live state to keep in mind while reading:

- Embree is the strongest validated backend today
- OptiX is real and validated on bounded accepted workloads on `192.168.1.20`
- Vulkan is currently kept as provisional backend code
- the PostGIS ground-truth comparison track is in progress and not yet a closed result
