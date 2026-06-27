# Goal1232 Two-AI Consensus: Public Documentation Map And Model Docs

Date: 2026-05-03

Participants:

- Codex
- Gemini CLI

## Decision

VERDICT: ACCEPT

## Consensus

The public documentation set needed a clear map for the areas the project wants
readers to understand first: front page, tutorials, apps, examples,
architecture, programming model, IR/lowering, and performance. Goal1232 is
accepted because it adds that map and fills two missing current-doc gaps:

- `docs/rtdl/ir_and_lowering.md` explains `CompiledKernel`,
  `RTExecutionPlan`, current predicate-specific lowering, and why v1.5 must
  generalize app/workload-specific engine work.
- `docs/performance_model.md` explains timing boundaries, Python overhead,
  native/prepared paths, RTX wording levels, and why v1.0 proves bounded
  sub-paths rather than universal whole-app speedup.

The linked front-page and docs-index updates are accepted. They improve
discoverability without making the README or docs index crowded again.

## Verification

Focused documentation tests passed:

```bash
python3 -m unittest \
  tests.goal1232_public_doc_map_test \
  tests.goal1231_front_page_simplification_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal1228_v1_0_positioning_docs_test \
  tests.goal1230_v1_0_app_acceleration_inventory_test \
  tests.goal821_public_docs_require_rt_core_test -v
```

Result: `OK`.
