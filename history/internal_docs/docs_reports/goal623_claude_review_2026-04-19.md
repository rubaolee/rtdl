# Goal623 Claude Review

Date: 2026-04-19
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Files Inspected

- `docs/reports/goal623_v0_9_4_backend_naming_and_apple_db_boundary_2026-04-19.md`
- `docs/backend_maturity.md`
- `docs/current_architecture.md`
- `docs/capability_boundaries.md`
- `docs/release_reports/v0_9_4/support_matrix.md`

## Question 1: Do the docs correctly state that HIPRT and Apple RT are two newer RTDL backend families?

Yes. `current_architecture.md` (line 69) states explicitly:

> This means HIPRT and Apple RT are now two newer RTDL backend families alongside Embree, OptiX, and Vulkan.

The Backend Roles table enumerates HIPRT and Apple RT as distinct named entries alongside the four established backends. `backend_maturity.md` lists both in the summary table with bounded, honest performance claims.

## Question 2: Do the docs honestly distinguish Apple MPS RT geometry/nearest-neighbor paths from Apple Metal compute/native-assisted DB and graph paths?

Yes. The distinction is explicit and consistent across all inspected files:

- `docs/release_reports/v0_9_4/support_matrix.md` — the dispatch matrix labels `bfs_discover`, `conjunctive_scan`, `grouped_count`, `grouped_sum`, and `triangle_match` as `native_metal_compute` or `native_metal_filter_cpu_aggregate`, and the Honesty Boundary section states: "current RTDL DB workloads … and current graph workloads … are Apple GPU compute/native-assisted paths. They are not Apple ray-tracing-hardware traversal paths and must not be marketed as MPS RT acceleration."

- `docs/capability_boundaries.md` (lines 271–277) — names the five predicates explicitly and disavows MPS ray-tracing-hardware traversal for each.

- `docs/backend_maturity.md` — states: "Do not read 'Apple RT backend' as 'every Apple workload uses Apple ray-tracing hardware.' The DB and graph rows in the current Apple surface are Apple GPU Metal-compute/native-assisted paths, not MPS ray-tracing traversal paths."

- `docs/current_architecture.md` — Backend Roles table entry for Apple RT explicitly notes "DB/graph rows implemented through Metal compute/native-assisted modes rather than MPS ray traversal."

## Disallowed-Wording Check

The Goal623 report states validation found no matches for `current v0.9.2`, `Apple hardware execution`, or `cpu_reference_compat` in the updated public docs. The reviewed files contain none of those patterns. No inspected doc claims Apple DB or graph workloads are accelerated by Apple ray-tracing hardware.

## Rationale

Both review questions are answered correctly and consistently. The public docs name HIPRT and Apple RT as newer backend families without overstating maturity, and they cleanly separate the MPS RT geometry/nearest-neighbor surface from the Metal compute/native-assisted DB and graph surface with explicit per-predicate disclosure.
