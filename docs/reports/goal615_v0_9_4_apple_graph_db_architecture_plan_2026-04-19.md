# Goal615: v0.9.4 Apple Graph/DB Architecture Plan

Date: 2026-04-19

Status: accepted with 2-AI planning consensus (Codex + Gemini 2.5 Flash checklist review).

## Version Definition

v0.9.4 is the Apple graph/DB backend architecture version.

The goal is not to claim that Apple MPS RT magically understands graph or database workloads. The goal is to add the missing Apple backend layer needed to make graph and DB rows honestly native-assisted:

```text
RTDL kernel
  -> Apple lowering contract
  -> MPS RT candidate discovery over geometric proxy primitives
  -> Metal compute refinement/filter/aggregation where needed
  -> bounded CPU oracle parity and performance reporting
```

This brings Apple closer to the architecture style already possible in OptiX/Vulkan/HIPRT, where RT traversal is paired with programmable GPU-side compute.

## Why v0.9.4 Is Needed

v0.9.3 expanded Apple RT native/native-assisted support to 13 geometry/nearest-neighbor rows. The five remaining rows are:

- `bfs_discover`
- `triangle_match`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

These are not directly geometric. They need explicit proxy encodings and compute passes. Without that, `run_apple_rt(..., native_only=True)` would either be misleading or CPU-only.

## Hardware-Backed Definition For v0.9.4

A v0.9.4 Apple graph/DB workload can be called hardware-backed only if:

- MPS RT performs candidate discovery over an explicit geometric proxy representation; or
- Metal compute performs the main predicate/filter/refinement/aggregation step; and
- CPU work is limited to packing, orchestration, validation, or explicitly documented final materialization.

If CPU performs the dominant workload logic, the row must remain compatibility-only.

## Goal Ladder

### Goal615: Architecture Contract

Deliverables:

- This architecture plan.
- A support-matrix rule for graph/DB Apple native-assisted states.
- External AI review and consensus.

Acceptance:

- 2-AI consensus that the plan is honest and implementable.
- No code claims changed before implementation evidence exists.

### Goal616: Apple Metal Compute Runtime Skeleton

Deliverables:

- Native Metal compute entry point alongside the existing MPS RT library.
- Buffer packing/unpacking helpers.
- Command queue and pipeline creation.
- Minimal compute kernel smoke test.
- Python ctypes wrapper and tests.

Acceptance:

- Local macOS test proves Metal compute can read input buffers and emit deterministic rows.
- No workload is marked graph/DB hardware-backed yet.

### Goal617: DB `conjunctive_scan` Native-Assisted Slice

Deliverables:

- Bounded row/proxy primitive encoding for table rows.
- Predicate encoding for numeric equality/range filters first.
- MPS RT candidate discovery or Metal compute predicate filtering.
- CPU oracle parity.
- PostgreSQL comparison remains Linux-only and release-report evidence, not local macOS dependency.

Acceptance:

- `run_apple_rt(..., native_only=True)` works for bounded `conjunctive_scan`.
- Apple result matches CPU oracle on fixtures and stress cases.
- Report states whether candidate discovery, predicate filtering, or both are hardware-backed.

### Goal618: DB `grouped_count` / `grouped_sum`

Deliverables:

- Reuse Goal617 candidate/filter stage.
- Define group-key packing.
- Implement bounded aggregation.

Implementation options:

- Preferred: Metal compute grouping/aggregation.
- Acceptable first slice: MPS/Metal predicate filtering plus CPU aggregation, named native-assisted only.

Acceptance:

- Exact parity for count/sum.
- Numeric type and overflow boundaries documented.
- PostgreSQL comparison included where Linux host is used.

### Goal619: Graph `bfs_discover`

Deliverables:

- Graph CSR/frontier proxy encoding.
- Candidate edge discovery.
- Visited filtering and dedupe boundary.

Implementation options:

- Preferred: Metal compute for frontier expansion/filtering with MPS candidate discovery only if a useful proxy exists.
- Acceptable first slice: Metal compute graph expansion without MPS, if documented as Apple GPU-backed but not MPS RT-backed.

Acceptance:

- Exact parity with CPU graph oracle.
- Bounded graph size and candidate ceiling documented.
- Performance compared to CPU/Embree if applicable.

### Goal620: Graph `triangle_match`

Deliverables:

- Wedge/seed encoding.
- Neighbor intersection candidate generation.
- Uniqueness/order contract.

Acceptance:

- Exact parity with CPU oracle.
- Stress case covers asymmetric degree ordering and duplicate suppression.
- Native-assisted wording is limited to the actual hardware path used.

### Goal621: v0.9.4 Performance and Release Gate

Deliverables:

- Full macOS Apple graph/DB correctness suite.
- Performance report.
- Docs/support-matrix update.
- External AI review.

Acceptance:

- No graph/DB native claim without row parity.
- No speedup claim without stable, correctness-valid timing evidence.

## Initial Implementation Recommendation

Start with Goal616, then Goal617.

Reason:

- A Metal compute skeleton is foundational and reduces risk.
- `conjunctive_scan` has the clearest bounded semantics.
- DB scan has a simpler correctness oracle than triangle matching.
- Grouped count/sum can reuse scan/filter infrastructure.

Do not start with graph triangle matching. It is the hardest remaining row because it combines adjacency intersection, duplicate suppression, and uniqueness ordering.

## Honesty Rules

- `Apple RT native` means MPS RT traversal is used for candidate discovery.
- `Apple GPU-backed` means Metal compute performs significant filter/refine/aggregate work, even if MPS RT is not used.
- `Apple native-assisted` means at least one hardware stage participates, but CPU refinement/materialization remains documented.
- `Apple compatibility` means the API runs but the workload logic is CPU reference.

## v0.9.4 Non-Goals

- Do not build a full graph database.
- Do not build a full SQL database.
- Do not claim GPU-resident DBMS execution.
- Do not claim broad Apple speedups before repeatable timing evidence exists.
- Do not remove CPU oracle paths; they are required for correctness gates.

## Open Risks

- MPS RT may not be the right primitive for every graph/DB row; Metal compute alone may be more honest for some stages.
- Group aggregation on GPU can be complex due to atomics, hash tables, ordering, and determinism.
- Candidate overproduction may make Apple slower than CPU/Embree unless prepared structures and batching are implemented.
- PostgreSQL validation remains Linux-hosted, not local macOS.

## Required Review

Goal615 has external review evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal615_gemini_plan_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal615_gemini_checklist_review_2026-04-19.md`

The first Gemini review was NEUTRAL because it declined a broad open-ended feasibility judgment. The second bounded checklist review returned ACCEPT on whether the plan honestly distinguishes MPS RT, Metal compute, native-assisted, and CPU compatibility; avoids premature graph/DB hardware claims; provides a plausible Goal616 path; and states risks/non-goals.

Goal615 is accepted as a planning gate. It does not prove that graph/DB Apple native support is implemented; it only authorizes Goal616 to begin.
