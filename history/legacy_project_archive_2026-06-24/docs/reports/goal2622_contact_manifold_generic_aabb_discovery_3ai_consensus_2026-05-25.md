# Goal2622 Contact-Manifold Generic AABB Discovery 3-AI Consensus

Date: 2026-05-25

Status: consensus accepted after resolving the artifact blocker identified by
Claude and receiving Claude re-review approval. Goal2622 is closed as a
boundary-cleanup and generic candidate-discovery step, not as a public
performance claim.

## Scope

Goal2622 addressed the concern that the contact-manifold benchmark still used
app-owned Python full all-pairs triangle-intersection discovery before bounded
row collection.

The implemented optimized path is:

```text
generic AABB_INDEX_QUERY_2D broadphase candidate rows
  -> app-owned exact triangle-intersection refinement
  -> generic COLLECT_K_BOUNDED fail-closed witness-row materialization
```

## Codex Review

Codex accepts the implementation because:

- `rtdsl.aabb_intersection_pair_rows_2d` emits app-name-free
  `(query_id, indexed_id)` candidate rows.
- The contact app uses the generic AABB broadphase before exact refinement.
- Exact triangle intersection and contact-summary interpretation remain
  app-owned Python code.
- `COLLECT_K_BOUNDED` still owns only bounded row materialization and
  fail-closed overflow.
- The benchmark app does not call old shape-pair native candidate collectors.
- Documentation states that OptiX AABB row output is not implemented and no
  speedup claim is authorized.

## Claude Review

Claude's first review verdict was `block` for one artifact issue: the new test
referenced this 3-AI consensus file before it existed. Claude otherwise found
that the core design passed:

- full-Python all-pairs discovery was removed from the optimized path;
- the engine remained app-agnostic;
- there was no collision-specific native engine logic;
- performance wording did not overclaim;
- primitive and application catalog entries were accurate.

The blocker is resolved by adding this consensus report and rerunning the test
suite. Claude re-review then returned `Approve` and confirmed that no blockers
remain.

## Gemini Review

Gemini verdict: `Approve`.

Gemini concluded that Goal2622 honestly addresses the discovery concern,
keeps the engine app-agnostic, avoids collision-specific native logic, avoids
performance overclaiming, and has sufficient tests for this goal.

## Consensus

All three reviews agree on the technical conclusion:

- Goal2622 replaces the optimized contact benchmark's full app-owned Python
  all-pairs discovery with generic `AABB_INDEX_QUERY_2D` candidate discovery.
- The engine still has no collision-specific native engine logic and no
  contact-manifold ABI.
- Exact refinement remains app-owned, so this is not a completed native RT
  exact contact-discovery primitive.
- `AABB_INDEX_QUERY_2D` row output is currently a CPU reference generic row
  path; OptiX remains count-only for this row shape.
- Public speedup claims remain blocked until native generic row output or an
  equivalent generic exact-refinement path has backend evidence and review.

Goal2622 is therefore accepted as a completed internal design step for the
contact benchmark and primitive catalog, with the next engine target clearly
identified: native generic AABB/candidate row output if this benchmark needs RT
speedup evidence later.

## Pod Follow-Up

After consensus, the running RTX A5000 pod was used for boundary evidence:

- Goal2622 tests passed on the pod.
- OptiX `AABB_INDEX_QUERY_2D` count-only `range_intersects` matched CPU for
  the contact grid-512 AABB workload.
- `aabb_intersection_pair_rows_2d(..., backend="optix")` still fails with the
  intended boundary error because native generic row output is not implemented.
- Large pressure testing found and fixed an unsafe app default: `resolution`
  must not scale directly as `grid_count` for skinny AABB scenes. The app now
  uses adaptive `min(256, max(16, sqrt(grid_count)))` resolution by default.
- Adaptive CPU row-output pressure reached 65,536 witness rows correctly, but
  spent `~45.6s` in generic CPU AABB broadphase emission while exact refinement
  spent only `~0.15s`. This reinforces that the next shared runtime target is
  native generic AABB/candidate row output.

Evidence file:
`docs/reports/goal2622_contact_manifold_optix_count_boundary_pod_evidence_2026-05-25.md`.
