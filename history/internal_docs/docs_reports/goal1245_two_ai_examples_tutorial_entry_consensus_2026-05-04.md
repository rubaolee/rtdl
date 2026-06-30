# Goal1245 Two-AI Consensus: Examples And Tutorial Entry

Date: 2026-05-04

Participants:
- Codex
- Gemini (`docs/reports/goal1245_gemini_examples_tutorial_entry_review_2026-05-04.md`)

Scope:
- `examples/README.md`
- `docs/tutorials/README.md`
- `tests/goal1245_examples_tutorial_entry_test.py`

## Verdict

`ACCEPT`

Codex and Gemini agree that the examples/tutorial entry changes are safe to
commit.

## Consensus Basis

- `examples/README.md` now starts with a short beginner path before the full
  inventory.
- `docs/tutorials/README.md` now clearly separates the tutorial ladder from the
  complete examples index.
- The wording keeps performance boundaries intact: examples demonstrate
  runnable shapes, while public speedup wording still requires the support
  matrix and reviewed evidence for an exact bounded sub-path.
- No new NVIDIA RTX public speedup wording or backend maturity claim is
  authorized.

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal1245_examples_tutorial_entry_test tests.goal512_public_doc_smoke_audit_test tests.goal958_public_app_native_continuation_schema_test tests.goal700_fixed_radius_summary_public_doc_test tests.goal646_public_front_page_doc_consistency_test tests.goal1232_public_doc_map_test`
  - Result: `Ran 18 tests`, `OK`.

## Boundary

This consensus covers documentation entry routing only. It does not release
v1.0, does not change the current released version, does not authorize new
public speedup wording, and does not require an NVIDIA pod.
