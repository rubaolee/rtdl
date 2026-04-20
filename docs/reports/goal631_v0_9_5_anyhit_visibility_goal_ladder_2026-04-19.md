# Goal631: v0.9.5 Any-Hit And Visibility Goal Ladder

Date: 2026-04-19
Status: active

## Scope

v0.9.5 implements only the first two Goal534 candidates:

- bounded any-hit / early-exit traversal
- line-of-sight / visibility rows as a standard-library workload built on
  any-hit

The following Goal534 candidates are explicitly out of scope for v0.9.5:

- multi-hop graph traversal helpers
- hierarchical candidate filtering
- bounded row reductions beyond what visibility needs
- rendering shader hooks, mutable payloads, recursive rays, BRDFs, path
  tracing, or global illumination

## Goal Ladder

### Goal631: Version Scope And Contract

Define the v0.9.5 contract and acceptance ladder.

Acceptance:

- Names only any-hit and visibility as v0.9.5 scope.
- Preserves the non-rendering ITRE boundary from Goal534.
- Records that first implementation must prioritize CPU/oracle correctness.
- Gets 2+ AI consensus before v0.9.5 closure.

### Goal632: Bounded Ray/Triangle Any-Hit

Add `ray_triangle_any_hit` as a first-class RTDL predicate and direct helper.

Acceptance:

- DSL predicate compiles and lowers for ray probe plus triangle build inputs.
- CPU Python reference emits one row per ray with fields:
  - `ray_id`
  - `any_hit`
- `run_cpu` works through the native-oracle-facing public path.
- Semantics are bounded: stop after the first valid hit per ray in the Python
  reference implementation.
- Exact first-blocker ID is not part of this release contract.
- Native backend support may start as compatibility fallback unless parity and
  backend-specific early-exit behavior are explicitly tested.

### Goal636: Backend Any-Hit Compatibility Dispatch

Allow real RTDL backend dispatchers to run kernels using
`ray_triangle_any_hit`.

Acceptance:

- Embree, OptiX, Vulkan, HIPRT, and Apple RT dispatchers recognize the
  `ray_triangle_any_hit` predicate.
- Compatibility dispatch is allowed to run the backend's existing
  `ray_triangle_hit_count` path and project `hit_count > 0` to `any_hit`.
- Reports and public docs must record the user's concern that this is not true
  early-exit: it proves backend execution and parity, not performance benefit.
- Raw row-view mode may be rejected for projected any-hit until a native row ABI
  exists.
- Native early-exit kernels remain a separate future goal unless implemented
  and parity/performance-tested directly.

### Goal633: Visibility Rows Standard Library

Add a standard-library helper that builds observer-target rays and consumes
any-hit rows.

Acceptance:

- Public helper emits rows with fields:
  - `observer_id`
  - `target_id`
  - `visible`
- Supports 2D points with 2D triangle blockers and 3D points with 3D triangle
  blockers.
- Uses the new any-hit predicate internally.
- Does not expose rendering concepts.
- Does not promise deterministic blocker IDs.

### Goal634: Docs And Examples

Refresh public-facing docs/examples for v0.9.5.

Acceptance:

- Add at least one runnable any-hit example.
- Add at least one runnable visibility example.
- Explain that visibility rows are a non-rendering spatial-query helper.
- Explain backend maturity honestly.

### Goal635: Test, Review, Audit, Release Gate

Run focused and broad tests, obtain AI reviews, and produce final audit docs.

Acceptance:

- Focused any-hit and visibility tests pass.
- Relevant public docs tests pass.
- Full local test suite passes or any skips/failures are explicitly justified.
- Claude/Gemini review accepts the implementation and docs.
- Release state is updated only after the above gates pass.
