# Goal 535: Minimal ITRE Extension Demo Kernels

Date: 2026-04-18
Status: draft demos, not implementation

## Purpose

The user asked what the proposed new features would look like before
implementation.

The answer is the design-only demo page:

- `docs/rtdl/minimal_itre_extension_demo_kernels.md`

The demos cover:

- bounded any-hit / early-exit traversal
- line-of-sight / visibility rows
- bounded emitted-row reductions
- multi-hop graph as Python-orchestrated ITRE
- hierarchical candidate filtering
- non-rendering probe generation helpers
- a combined visibility app sketch

## Boundary

The page explicitly states that these snippets are not runnable RTDL code today.
It excludes:

- shader callbacks
- mutable ray payloads
- device-side recursive ray spawning
- path tracing
- ambient occlusion as rendering
- global illumination
- BRDF/material/skybox APIs

## Intended Next Step

Use the demo page as a design review artifact before implementing Goal A:
the formal bounded any-hit / early-exit traversal contract.
