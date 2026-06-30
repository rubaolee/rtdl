# Goal1274 Three-AI Consensus: v1.3 Primitive ABI And Lowering Contract

Date: 2026-05-05

Status: `ACCEPT`

## Scope

This consensus covers the v1.3 primitive ABI, per-app lowering matrix, backend
parity contract, public wording boundary, and migration gates for moving from
the internal v1.2 OptiX evidence checkpoint toward v1.4 and v1.5.

## Inputs

- Codex draft:
  `docs/reports/goal1274_v1_3_primitive_abi_lowering_contract_draft_2026-05-05.md`
- Gemini review:
  `docs/reports/goal1274_gemini_v1_3_primitive_contract_review_2026-05-05.md`
- Claude review:
  `docs/reports/goal1274_claude_v1_3_primitive_contract_review_2026-05-05.md`
- Evidence anchor:
  `docs/reports/goal1273_v1_2_validated_pod_findings_and_next_steps_2026-05-05.md`
- Roadmap anchor:
  `docs/reports/goal1255_three_ai_v1_1_to_v1_5_roadmap_consensus_2026-05-04.md`

## Consensus Verdict

`ACCEPT`

Codex, Gemini, and Claude accept the v1.3 contract. Gemini and Claude reported
no blocking findings. Their non-blocking suggestions were incorporated into the
draft before this consensus:

- `COLLECT_K_BOUNDED` must declare overflow/truncation/failure behavior when
  hits exceed `k`;
- `REDUCE_FLOAT(SUM)` may later expose compensated summation policy, but v1.3
  requires declared dtype, order, and tolerance;
- primitive plans must declare `retained_scale_range`;
- `prepared_state` must specify which state is immutable and reusable;
- floating reductions must define minimum NaN behavior;
- v1.4 migration treats "performance-neutral" as no worse than 10% slower than
  the app-specific continuation unless separately reviewed and accepted.

## Accepted Primitive Set

The accepted v1.5 target remains:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN)`
- `REDUCE_FLOAT(MAX)`
- `REDUCE_FLOAT(SUM)`
- `REDUCE_INT(COUNT)`
- `REDUCE_INT(SUM)`
- `COLLECT_K_BOUNDED`, experimental only after scalar primitives are stable

The consensus explicitly rejects an untyped `REDUCE` bucket because it hides
dtype, result shape, tolerance, overflow, grouping, and determinism contracts.

## Accepted Backend Scope

- Active v1.3/v1.4 engineering scope is Embree plus OptiX.
- NVIDIA RT performance remains the top priority.
- Embree remains the CPU RT fallback and same-contract baseline.
- Vulkan, HIPRT, and Apple RT remain frozen for new implementation work before
  v2.1; existing proof surfaces may be preserved but not expanded.

## Accepted Per-App Lowering Direction

| App row | Accepted v1.3 direction |
| --- | --- |
| `graph_analytics.visibility_edges` | Lower visibility predicate to `ANY_HIT`; summary count to `COUNT_HITS` or `REDUCE_INT(COUNT)`; keep BFS, triangle counting, graph DB, frontier bookkeeping, and reductions outside this row. |
| `database_analytics.sales_risk` | Lower compact-summary predicate/count path to `COUNT_HITS` or `REDUCE_INT(COUNT)`; keep SQL/DBMS/broad database and row-materializing claims outside scope. |
| `polygon_pair_overlap_area_rows` | Lower candidate discovery through `ANY_HIT`; defer exact area generalization to `REDUCE_FLOAT(SUM)` only after float reduction/refinement contracts exist; preserve Goal1270 diagnostic split. |
| `polygon_set_jaccard` | Keep as `optix_still_slower_with_reason`; explore `ANY_HIT`, experimental `COLLECT_K_BOUNDED`, and later `REDUCE_FLOAT(SUM)` without expanding public wording. |

## Accepted Migration Gates

No app-specific native continuation may be retired until the relevant contract,
parity, phase, performance, wording, and review gates pass. In particular:

- CPU oracle, Embree, and OptiX must pass the declared parity rule.
- Floating reductions use declared tolerance and NaN policy, not bit-exact
  parity by default.
- Phase reports must separate prepare, traversal/query, reduction or
  continuation, copyback, and output packing.
- Generic primitive replacement must be performance-neutral under the accepted
  10% threshold or have a separately reviewed overhead acceptance.
- Positive public wording remains false until a separate exact-sub-path wording
  packet is reviewed and accepted.

## Boundary

This consensus authorizes v1.3 as the current contract baseline and authorizes
local planning for v1.4 compatibility-wrapper slices. It does not by itself
authorize public RTX speedup wording, public release packages, release gates,
tags, or implementation work on Vulkan, HIPRT, or Apple RT before v2.1.
