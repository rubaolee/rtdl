# Goal 254: Engineering Support Docs Audit Pass

## Objective

Expand the system-audit coverage through the engineering/support-doc cluster
that remains easy to discover after the front-surface and tutorial passes, with
special attention to older Embree planning documents that can be mistaken for
the current live roadmap.

## Scope

- `docs/ai_collaboration_workflow.md`
- `docs/embree_baseline_contracts.md`
- `docs/embree_baseline_plan.md`
- `docs/embree_evaluation_matrix.md`
- `docs/embree_evaluation_plan.md`
- `docs/embree_rayjoin_reproduction_program.md`
- `docs/future_ray_tracing_directions.md`
- `docs/gemini_cli_notes.md`

## Acceptance

- each file is reviewed and recorded in the system-audit DB
- older planning docs are clearly marked as historical when needed
- live workflow docs point to the current `refresh.md`-driven review rule
- any easy-to-misread release/roadmap ambiguity is reduced
