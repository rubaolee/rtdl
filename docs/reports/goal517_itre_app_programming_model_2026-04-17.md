# Goal 517: ITRE App Programming Model Documentation

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

Goal517 documents the v0.8 programming-model conclusion from the release
discussion:

**ITRE (`input -> traverse -> refine -> emit`) is sufficient for the RTDL-owned
query/traversal kernels in the current v0.8 target apps, while Python remains
responsible for orchestration, construction, reductions, and output.**

The goal is to make that claim explicit, useful, and bounded in public docs.

## Changes Made

- Added `/Users/rl2025/rtdl_python_only/docs/rtdl/itre_app_model.md`.
- Linked it from:
  - `/Users/rl2025/rtdl_python_only/docs/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/rtdl/README.md`
  - `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
  - `/Users/rl2025/rtdl_python_only/docs/tutorials/v0_8_app_building.md`
- Added `/Users/rl2025/rtdl_python_only/tests/goal517_itre_app_model_doc_test.py`.

## Documented Boundary

The new document states:

- RTDL owns typed inputs, traversal intent, backend dispatch, candidate
  generation, refinement semantics, and emitted row schemas.
- Python owns data loading, app construction, orchestration, reductions,
  visualization, and external/app-level comparison.
- ITRE is not claimed to be a complete app language.
- ITRE is claimed to be sufficient for the RTDL-owned kernel part of the current
  v0.8 target apps.

## App Mapping Recorded

The document maps the three v0.8 apps:

- Hausdorff distance: point-set inputs become nearest-neighbor rows; Python
  reduces rows into directed/undirected Hausdorff distance and witness IDs.
- Robot collision screening: link edge rays traverse obstacle triangles and
  emit hit-count rows; Python builds poses/link rays and aggregates collision
  flags.
- Barnes-Hut force approximation: bodies and quadtree nodes become candidate
  interaction rows; Python builds the quadtree, applies opening policy, and
  computes force vectors and oracle error.

## Language Pressure Recorded

The Barnes-Hut app is documented as the strongest v0.8 language-pressure case.
Future RTDL work may need:

- tree-node input types
- opening predicates
- grouped vector reductions
- iterative multi-stage kernel orchestration

These are recorded as future pressure, not current release claims.

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal517_itre_app_model_doc_test tests.goal512_public_doc_smoke_audit_test tests.goal515_public_command_truth_audit_test -v
```

Result: `Ran 6 tests`, `OK`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile tests/goal517_itre_app_model_doc_test.py && git diff --check
```

Result: passed.

## Current Verdict

Goal517 is accepted. The ITRE app-programming boundary is now documented in the
public language docs and linked from the v0.8 app-building path.

## AI Review Consensus

- Claude review: `APPROVED`; the bounded claim is precise, the RTDL/Python
  ownership split is explicit, and the Barnes-Hut caveat records language
  pressure without laundering it into a current capability claim.
- Gemini Flash review: `ACCEPT`; the documentation states that ITRE is
  sufficient for RTDL-owned kernel parts of v0.8 apps while Python remains the
  application layer, and the test verifies the key statements and links.
- Codex conclusion: `ACCEPT`; Goal517 converts the release discussion into a
  durable public documentation boundary.
