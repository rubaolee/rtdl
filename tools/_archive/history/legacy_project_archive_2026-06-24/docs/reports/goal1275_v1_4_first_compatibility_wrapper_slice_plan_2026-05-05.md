# Goal1275 v1.4 First Compatibility Wrapper Slice Plan

Date: 2026-05-05

Status: local v1.4 planning artifact. This plan does not authorize public RTX
speedup wording, release tags, or new Vulkan/HIPRT/Apple RT implementation.

## Decision

The first v1.4 compatibility-wrapper slice should be
`graph_analytics.visibility_edges`.

It is the narrowest safe first migration because the current app already has a
bounded RT traversal boundary, current validated pod evidence, and an accepted
v1.3 lowering target:

- primitive predicate: `ANY_HIT`;
- summary primitive: `COUNT_HITS` or `REDUCE_INT(COUNT)`;
- active backends: Embree and OptiX only;
- frozen backends: Vulkan, HIPRT, and Apple RT remain untouched before v2.1;
- excluded graph work: BFS, triangle counting, shortest path, graph database
  behavior, frontier bookkeeping, and graph reductions.

## Current State

The graph app has two relevant visibility paths:

| Path | Current owner | Current behavior | v1.4 treatment |
| --- | --- | --- | --- |
| `visibility_pair_rows(...)` row mode | generic Python API dispatching CPU/Embree/OptiX/Vulkan/HIPRT/Apple RT | materializes one row per candidate edge | keep behavior unchanged; wrap only Embree/OptiX metadata and contract |
| OptiX summary prepared path in `examples/rtdl_graph_analytics_app.py` | app-specific continuation | prepares blocker geometry and rays, then calls prepared any-hit count repeatedly | first target for a compatibility wrapper around `ANY_HIT` plus aggregate count |

Goal1272/Goal1273 validated the internal evidence: graph OptiX total timing
beats Embree on the targeted pod, and prepared-repeat any-hit query timing is
tens of microseconds. That evidence is internal and sub-path specific.

## First Wrapper Contract

The wrapper should expose a primitive-plan payload without changing the app
result shape:

| Field | Required value for first slice |
| --- | --- |
| `app_row` | `graph_analytics.visibility_edges` |
| `primitive` | `ANY_HIT` |
| `summary_primitive` | `COUNT_HITS` or `REDUCE_INT(COUNT)` |
| `backend_scope` | `embree`, `optix` |
| `mode` | `one_shot` for row materialization, `prepared` for reusable summary query |
| `build_layout` | 2-D triangle/blocker build buffer |
| `probe_layout` | 2-D visibility ray/probe buffer |
| `result_layout` | per-edge visibility rows for row mode; aggregate visible/blocked counts for summary mode |
| `prepared_state` | OptiX summary may reuse build geometry and prepared ray buffers; Embree compatibility can begin as one-shot if no prepared object exists |
| `phase_counters` | input construction, blocker pack, ray pack, scene prepare, ray prepare, any-hit query/count, summary postprocess |
| `claim_boundary` | visibility edge any-hit/count only; not broad graph analytics |

The first implementation should be a compatibility wrapper: it delegates to the existing behavior, surfaces the v1.3 primitive metadata, and records the same
phase counters. It must not retire the existing app-specific OptiX summary path
until the generic path passes the v1.3 migration gates.

## Implementation Order

1. Add a small graph visibility primitive wrapper module or helper with no new
   public claim surface.
2. Route `graph_analytics.visibility_edges` summary mode through the wrapper
   while preserving JSON shape and current phase counter names.
3. Keep row mode behavior equivalent to `visibility_pair_rows(...)`; only add
   primitive metadata after parity tests pass.
4. Add tests that verify CPU/Embree/OptiX same-contract metadata where the
   backend is available, and mocked OptiX tests for prepared-state metadata on
   local macOS.
5. Re-run targeted pod evidence only after the local wrapper is stable.

## Non-Goals

- Do not touch Vulkan, HIPRT, or Apple RT implementation before v2.1.
- Do not claim whole-app graph acceleration.
- Do not include BFS, triangle counting, graph database behavior, shortest
  path, frontier operations, or graph reductions.
- Do not retire `optix_prepared_visibility_anyhit_count` until the generic
  wrapper is performance-neutral or an accepted overhead is reviewed.
- Do not expand public RTX wording from this planning artifact.

## Exit Gate For This Slice

The slice is ready for implementation review when:

- the wrapper emits the v1.3 ABI metadata for `ANY_HIT` and the count summary;
- existing graph JSON output remains backward-compatible;
- Embree and OptiX execute the same logical contract where available;
- local tests pass without requiring a pod;
- the next pod run validates parity and phase counters before any performance
  conclusion is recorded.
