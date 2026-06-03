# Handoff: External Review For Goal3070 v2.7 Primitive Discovery Core

Please perform a read-only external review of Goal3070.

## Context

v2.6 is released. v2.7 starts by improving primitive discovery so users and the
Main AI can find existing generic RTDL primitives before proposing new ones.

Primary input design:

- `docs/reports/claude_primitive_discovery_and_orchestration_design_for_main_ai_2026-06-01.md`

Implemented Goal3070 report:

- `docs/reports/goal3070_v2_7_primitive_discovery_core_2026-06-03.md`

Files to inspect:

- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/primitive_discovery.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl_primitive_catalog.md`
- `tests/goal3070_v2_7_primitive_discovery_core_test.py`
- `tests/goal2624_primitive_hierarchy_test.py`

## Review Questions

1. Does the new discovery metadata preserve the app-agnostic primitive boundary?
2. Is the controlled facet vocabulary sufficient for this first v2.7 slice?
3. Does `find_primitive(...)` provide deterministic, useful discovery without hidden routing or partner auto-selection?
4. Does `lint_new_primitive(...)` make duplicate primitive creation fail closed enough for this stage?
5. Are the docs honest that catalog generation and orchestration recipes are deferred future work?
6. Are there any public-claim, release-readiness, zero-copy, speedup, or app-specific-engine overclaims?

## Expected Output

Use verdicts from this set only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If you are Gemini, write:

- `docs/reviews/goal3071_gemini_review_goal3070_v2_7_primitive_discovery_core_2026-06-03.md`

If you are Claude, write:

- `docs/reviews/goal3072_claude_review_goal3070_v2_7_primitive_discovery_core_2026-06-03.md`

Do not edit source files. If you run tests, record the exact command and result.
