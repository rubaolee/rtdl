# Goal1042 Two-AI Architecture Consensus

Date: 2026-04-27

## Scope

This consensus records alignment between the primary architecture feedback and Gemini's confirmation for the v1.5 generic primitives direction.

Reviewed:

- `docs/reports/goal1042_primary_architecture_feedback_v1_5_primitives_2026-04-27.md`
- `docs/handoff/gemini_goal1042_architecture_feedback_confirmation_2026-04-27.md`

## Consensus

Status: `accepted_direction_with_required_refinements`.

Both reviewers agree:

- v1.5 should pursue generic traversal-plus-reduction primitives, not broad app-specific backend rewrites.
- The minimum primitive set should be narrowed to `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- `COLLECT_K_BOUNDED` should remain experimental until scalar reductions are stable.
- DLPack/zero-copy handoff is the preferred extension mechanism for v1.5.
- PTX/SPIR-V plugin injection should be experimental and excluded from public stability claims.
- v1.0 stability and existing app evidence must not be destabilized by v1.5 refactoring.
- Required next artifacts are a primitive contract document and a per-app lowering matrix before touching C++/CUDA implementation.

## Next Gate

Do not begin broad backend rewrites. The next review gate is the primitive contract and per-app lowering matrix.

## Boundary

This consensus is an architecture-planning acceptance only. It does not authorize implementation, release, public speedup claims, or retirement of existing v1.0 endpoints.
