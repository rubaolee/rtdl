# Goal2482 Consensus: Robot Collision Embree Contract

Date: 2026-05-21

Consensus: Approved

Goal2482 is complete.

## Reviewed Artifacts

- `docs/reports/goal2481_robot_collision_generic_contract_design_2026-05-21.md`
- `docs/reports/goal2482_robot_collision_embree_contract_2026-05-21.md`
- `docs/reviews/goal2482_gemini_review_robot_collision_embree_contract_2026-05-21.md`
- `docs/reviews/goal2482_claude_review_robot_collision_embree_contract_2026-05-21.md`
- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal2482_robot_collision_embree_contract_test.py`

## Consensus Finding

Codex, Gemini, and Claude agree that Goal2482 satisfies the Goal2481 contract:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

The accepted implementation is a generic Embree prepared static 3D triangle
scene plus grouped finite 3D segment any-hit flags. It does not introduce a
native application API.

## Review Results

Gemini:

- Verdict: Approved
- Blocking Issues: None
- Main non-blocking notes: native validation duplicates Python validation; the
  CPU oracle may later move into `src/rtdsl/reference.py` if reused by more 3D
  contracts.

Claude:

- Verdict: Approved
- Blocking Issues: None
- Main non-blocking notes: `prepared_reused` can be read ambiguously on the
  first call; the Python `claim_boundary` dict should explicitly include OptiX
  parity; the full test suite depends on review files existing.

Codex disposition:

- Kept `prepared_reused` for continuity and added `prepared_scene_used` to make
  first-call semantics explicit.
- Added `optix_parity: False` to the Python result claim boundary.
- The review-file-gated test is expected to pass after this consensus file is
  present.

## Accepted Evidence

- Embree matches the 3D CPU probe oracle on the Goal2481 contract fixture.
- Expected flags are `[1, 0, 1, 0, 1]`.
- Output format is byte-per-query-group `uint8` flags.
- Python rejects invalid finite-segment and grouping inputs before native
  traversal.
- Prepared scene reuse is represented by a persistent native handle and
  repeated run metadata.
- Precision metadata records host float64 input, Embree float32 BVH bounds, and
  float64 native callback intersection math.
- Active native Embree/OptiX files remain free of forbidden application
  vocabulary.
- No pod was used; the evidence is local Embree evidence only.

## Claim Boundary

Goal2482 still does not claim:

- paper reproduction;
- authors-code comparison;
- public speedup;
- native robot, link, pose, planner, or collision API support;
- exact solid contact;
- continuous or swept support;
- row witnesses;
- OptiX parity;
- release/tag action.

## Next Step

Goal2483 should add same-contract OptiX parity for the same primitive shape, or
Goal2484 may expand Python-side benchmark lowering if OptiX work is deferred.
