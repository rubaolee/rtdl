# Gemini Review for Goal3070 v2.7 Primitive Discovery Core

## Review Date
2026-06-03

## Reviewed By
Gemini

## Context
v2.6 is released. v2.7 starts by improving primitive discovery so users and the
Main AI can find existing generic RTDL primitives before proposing new ones.

Primary input design:
- `docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`

Implemented Goal3070 report:
- `docs/reports/goal3070_v2_7_primitive_discovery_core_2026-06-03.md`

Files inspected:
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/primitive_discovery.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl_primitive_catalog.md`
- `tests/goal3070_v2_7_primitive_discovery_core_test.py`
- `tests/goal2624_primitive_hierarchy_test.py`

## Review Questions and Answers

### 1. Does the new discovery metadata preserve the app-agnostic primitive boundary?
**Answer:** Yes, the new discovery metadata explicitly preserves the app-agnostic primitive boundary. The design document, implementation, and tests all reinforce this by using a controlled vocabulary for capability tags, explicitly excluding app-domain specific terms from primitive nodes, and leveraging the `APP_OWNED_BOUNDARY_EXCLUSIONS` list to govern what remains outside the primitive boundary.

### 2. Is the controlled facet vocabulary sufficient for this first v2.7 slice?
**Answer:** Yes, the controlled facet vocabulary (`intent`, `shape`, `dim`, `output`, `exactness`, `keying`) appears sufficient for this first v2.7 slice. The design explicitly intends it to be a closed set, and the implemented tags cover fundamental, app-agnostic aspects of primitive behavior. It aligns with the goal of improving primitive discovery without introducing app-specific semantics.

### 3. Does `find_primitive(...)` provide deterministic, useful discovery without hidden routing or partner auto-selection?
**Answer:** Yes, `find_primitive(...)` provides deterministic and useful discovery. Its ranking mechanism is based on explicit facet matches, aliases, and text, which is deterministic. The design and implementation clearly state that it is an inverse index for discovery and explicitly avoids hidden routing or partner auto-selection, aligning with the "advisory planner" principle. The `compose_hint` also serves as an advisory element, not a directive.

### 4. Does `lint_new_primitive(...)` make duplicate primitive creation fail closed enough for this stage?
**Answer:** Yes, `lint_new_primitive(...)` makes duplicate primitive creation fail closed effectively for this stage. It correctly identifies potential duplicates based on key facets and enforces the requirement for `considered_alternatives` and `distinct_from` fields. This mechanism prevents new primitives from being added without explicit justification for their uniqueness, ensuring controlled growth of the primitive set.

### 5. Are the docs honest that catalog generation and orchestration recipes are deferred future work?
**Answer:** Yes, the documentation is honest. Both the design document and the implementation report explicitly state that catalog generation and orchestration recipes are deferred future work, focusing this slice on the core discovery mechanism. The `docs/rtdl_primitive_catalog.md` file itself does not claim to be generated, reinforcing this point.

### 6. Are there any public-claim, release-readiness, zero-copy, speedup, or app-specific-engine overclaims?
**Answer:** No, there are no public-claim, release-readiness, zero-copy, speedup, or app-specific-engine overclaims. All reviewed documents (design, implementation report, and catalog) explicitly disclaim these aspects, consistently defining the scope as app-agnostic discovery and governance without touching engine changes, performance claims, or release readiness.

## Verdict
`accept`
