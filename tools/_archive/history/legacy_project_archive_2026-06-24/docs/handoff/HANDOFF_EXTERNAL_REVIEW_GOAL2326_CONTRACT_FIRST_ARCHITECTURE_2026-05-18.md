# External Review Handoff: Goal2326 Contract-First Primitive Reconstruction

Please perform an independent architecture/code review of Goal2326.

## Files To Read

- `docs/reports/goal2326_contract_first_primitive_reconstruction_plan_2026-05-18.md`
- `src/rtdsl/execution.py`
- `src/rtdsl/primitives.py`
- `src/rtdsl/adapters/__init__.py`
- `src/rtdsl/adapters/traversal.py`
- `src/rtdsl/adapters/collection.py`
- `src/rtdsl/adapters/reductions.py`
- `src/rtdsl/adapters/columnar_payload.py`
- `src/rtdsl/adapters/partner_handoff.py`
- `src/rtdsl/adapters/prepared_handles.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl/dsl_reference.md`
- `tests/goal2326_public_primitive_contract_test.py`
- `tests/goal2326_execution_report_contract_test.py`
- `tests/goal2326_adapter_partition_test.py`
- `tests/goal2326_examples_recipe_boundary_test.py`

## Review Questions

1. Does the implemented slice keep native engines app-agnostic?
2. Does the new public `rtdsl.primitives` facade avoid making RTDL look like a fixed app library?
3. Is `ExecutionPolicy` / `ExecutionReport` explainable enough for reproducibility and public claim discipline?
4. Are `src/rtdsl/adapters/*` module boundaries generic rather than app/domain shaped?
5. Is the compatibility-preserving adapter re-export strategy safer than moving all call sites immediately?
6. Are the new Goal2326 guard tests meaningful, and what additional tests should block adoption later?
7. Should Goal2326 be accepted, accepted-with-boundary, rejected, or needs-more-evidence?

## Required Boundaries

- Do not claim v2.0 release readiness from this review.
- Do not authorize public speedup, RT-core, or zero-copy claims.
- Do not treat Codex-authored text as independent external consensus.
- If you find a blocker, cite exact file/line and explain the minimal fix.

## Expected Output

Claude should write:

`docs/reviews/goal2326_claude_contract_first_primitive_architecture_review_2026-05-18.md`

Gemini should write:

`docs/reviews/goal2326_gemini_contract_first_primitive_architecture_review_2026-05-18.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
