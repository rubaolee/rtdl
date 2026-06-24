# Goal1228 v1.0 Positioning And Engine Customization Plan

Date: 2026-05-03

Status: v1.0 planning and documentation direction

## Positioning

RTDL v1.0 should be presented as the release that proves the RTDL model works
on real application-shaped workloads.

The v1.0 message is not "every app is fully accelerated." The correct message
is:

> RTDL lets users express useful spatial, graph, database-style, nearest-neighbor,
> simulation-screening, and geometry workflows in Python, then routes selected
> traversal-heavy phases through RT-capable backends. Some selected sub-paths
> have reviewed speedup evidence; whole-app performance depends on whether the
> non-RT continuation has a native implementation.

This is the right foundation for v1.5 and v2.0:

- v1.0 proves the DSL and app targets.
- v1.5 removes app-specific engine customization by introducing generic
  traversal-plus-reduction primitives.
- v2.0 targets broader end-to-end performance through explicit GPU compute
  partnership and zero-copy handoff.

## What v1.0 Should Finish

v1.0 should finish the app-facing product surface:

- Public app catalog is accurate.
- Front page explains the RTDL model and does not overclaim.
- Every public app documents the accelerated phase, the native continuation
  if any, and the Python/postprocess work that remains outside the claim.
- Apple RT, HIPRT, and Vulkan stay as proven backend-specific capability lines;
  they are not expanded as v1.0 blockers.
- Embree remains the CPU RT backend and comparison/reference path.
- NVIDIA OptiX/RTX remains the main hardware RT-core evidence path, with public
  wording limited to reviewed sub-paths.

## Engine Customization Inventory

The v1.0 implementation uses app-driven native customization. That is acceptable
for v1.0, but it must be documented because v1.5 is expected to remove this
pattern.

| App family | v1.0 customization used | Why it exists in v1.0 | v1.5 target |
| --- | --- | --- | --- |
| Fixed-radius density, hotspot, coverage | Prepared scalar summary modes and compact count/threshold continuations | Avoid row materialization and isolate traversal-heavy phases | `COUNT_HITS`, `ANY_HIT`, scalar reductions |
| DB compact analytics | Native compact-summary filtering/grouping paths | Row materialization and Python grouping can dominate app time | AABB/payload lowering plus `REDUCE_INT`/`REDUCE_FLOAT` |
| Graph analytics | Visibility-edge any-hit and graph-ray candidate-generation paths | Show graph workloads can lower bounded candidate phases to RT traversal | Generic visibility/candidate traversal primitives; BFS/triangle logic remains explicit unless separately lowered |
| Segment/polygon apps | Native OptiX/Embree segment-polygon traversal and bounded row emitters | Custom geometry traversal and row volume need native control | Generic segment/polygon traversal plus `COUNT_HITS`, `ANY_HIT`, and experimental bounded collect |
| Polygon area/Jaccard apps | Native-assisted LSI/PIP candidate discovery plus exact-area continuation | Candidate discovery benefits from RT-style traversal; exact area remains separate | Candidate discovery primitive first; exact refinement only after a reviewed reduction contract |
| Hausdorff/ANN/KNN | Prepared threshold/candidate decision paths | Exact row/ranking output is expensive; threshold decisions isolate RT-friendly work | `REDUCE_FLOAT(MIN|MAX)` and experimental `COLLECT_K_BOUNDED` where appropriate |
| Robot collision | Prepared ray/triangle any-hit pose flags/counts | Any-hit traversal is the app-critical collision-screening phase | `ANY_HIT` over rays/triangles plus explicit pose grouping |
| Barnes-Hut | Prepared node-coverage decision and native compact summaries | Node coverage can be expressed as bounded traversal, but force reduction is separate | Generic node/candidate coverage primitive; force reduction remains compute-partner work |

## Public Claim Rule

For v1.0, docs should consistently say:

- reviewed RTX wording rows are bounded sub-path claims, not whole-app claims;
- `--backend optix` alone is not a public RT-core speedup claim;
- Python continuation can make a full app slow even when RT traversal is fast;
- blocked rows are honest results, not failures of the DSL;
- custom native continuations are v1.0 proof machinery, not the final v1.5
  architecture.

## Immediate Documentation Work

Before calling v1.0 docs complete, patch the stale public docs that still say
there are `11` reviewed RTX wording rows after Goal1208. Current branch state
after Goal1224 is `12` reviewed rows, with Hausdorff promoted and graph plus
polygon-pair public speedup wording blocked.

Required public-doc updates:

- `README.md`
- `docs/README.md`
- `docs/application_catalog.md`
- `docs/rtdl_feature_guide.md`
- `docs/release_facing_examples.md`
- `docs/app_engine_support_matrix.md`

Historical handoff/release-authorization request files may remain historical,
but current public docs must point to Goal1224/Goal1227-era source of truth.

## Next Step After This Plan

Continue v1.0 stabilization first:

1. Fix stale front-page and docs-index wording.
2. Add or update an audit that checks public docs no longer claim `11` reviewed
   rows as current state.
3. Ask Gemini/Claude to review the v1.0 positioning and customization inventory.
4. Only after v1.0 docs are stable, start the v1.5 primitive ABI and per-app
   lowering matrix as design documents, not implementation.
