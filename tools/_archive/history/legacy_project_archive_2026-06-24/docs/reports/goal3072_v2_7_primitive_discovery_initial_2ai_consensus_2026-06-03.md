# Goal3072: v2.7 Primitive Discovery Initial 2-AI Consensus

Date: 2026-06-03

Status: accepted for internal v2.7 continuation; not a release authorization.

## Scope

This consensus covers Goal3070 only:

- capability metadata on selected app-independent primitive hierarchy nodes;
- `primitive_index()`;
- `find_primitive(...)`;
- `describe_primitive(...)`;
- `lint_new_primitive(...)`;
- catalog documentation for the discovery overlay;
- focused tests for discovery, export, validation, and duplicate gating.

It does not cover future catalog generation, orchestration recipes,
multi-partner planning, release packaging, performance claims, zero-copy claims,
or v2.7 public readiness.

## Evidence

Codex local implementation and validation:

- `docs/reports/goal3070_v2_7_primitive_discovery_core_2026-06-03.md`
- `tests/goal3070_v2_7_primitive_discovery_core_test.py`
- Windows validation: `Ran 12 tests in 0.031s OK`
- `py_compile` clean for `primitive_hierarchy.py`, `primitive_discovery.py`, and `__init__.py`

Gemini independent review:

- `docs/reviews/goal3071_gemini_review_goal3070_v2_7_primitive_discovery_core_2026-06-03.md`
- Verdict: `accept`

Claude review attempt:

- Background Claude was attempted through the handoff workflow.
- Claude returned a session-limit message: `You've hit your session limit ... resets 9:50pm (America/New_York)`.
- No Claude review file exists for this goal; this file does not claim 3-AI consensus.

## Consensus Verdict

Codex + Gemini agree that Goal3070 is acceptable for internal v2.7 continuation.

The accepted boundary is:

- primitive discovery remains metadata/indexing over the app-agnostic hierarchy;
- no app-specific primitive semantics are promoted;
- no partner is auto-selected;
- duplicate-looking primitive proposals must include alternatives and distinction metadata;
- catalog generation and orchestration recipes remain future v2.7 work;
- no release, speedup, zero-copy, broad RT-core, or public-readiness claim is authorized.

## Next Recommended Goal

Proceed to the next v2.7 slice: make the Markdown primitive catalog generated
from the Python hierarchy, or add composition recipes only after the generated
catalog/drift gate exists. The single-source-of-truth gate should come before
more advisory orchestration so discovery data does not drift.
