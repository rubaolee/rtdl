# Goal 536: Minimal ITRE Extensions Task Proposal

Date: 2026-04-18
Status: proposal drafted

## Artifact

The detailed task proposal is:

- `docs/proposals/minimal_itre_extensions_task_proposal_2026-04-18.md`

## Scope

The proposal turns the Goal534 design study and Goal535 demo kernels into a
concrete implementation roadmap.

It covers:

- bounded any-hit / early-exit traversal
- line-of-sight / visibility rows
- bounded emitted-row reductions
- multi-hop graph orchestration
- hierarchical candidate filtering
- non-rendering probe generation helpers

## First Task

The proposal recommends starting with a formal `ray_triangle_any_hit` contract,
then CPU/Python reference and CPU/oracle correctness, then a visibility rows
standard-library app.

## Boundary

The proposal explicitly excludes:

- shader callbacks
- mutable ray payloads
- device-side recursive ray spawning
- renderer/material/BRDF/skybox/path-tracing APIs
- broad performance claims before evidence
