# Goal 49 Report: Documentation Rewrite Plan

Date: 2026-04-02

## Summary

The live RTDL documentation surface is larger than the true authoritative
surface. The repo currently mixes:

- canonical project guidance,
- active user/developer guides,
- and many preserved goal-plan documents that are still useful but should not
  all be rewritten as current-facing material.

So this rewrite round should first establish a canonical documentation set and
leave historical/goal execution material alone.

## Inventory Result

The live non-report doc surface is broad:

- `README.md`
- `docs/vision.md`
- `docs/v0_1_final_plan.md`
- `docs/v0_1_roadmap.md`
- `docs/rtdl/README.md`
- `docs/rtdl/dsl_reference.md`
- `docs/rtdl/programming_guide.md`
- `docs/rtdl/workload_cookbook.md`
- `docs/rtdl/llm_authoring_guide.md`
- `docs/rtdl_feature_guide.md`
- `docs/development_reliability_process.md`
- `docs/ai_collaboration_workflow.md`
- `docs/rayjoin_target.md`
- `docs/rayjoin_datasets.md`
- `docs/rayjoin_public_dataset_sources.md`
- `docs/rayjoin_paper_reproduction_matrix.md`
- plus many preserved `docs/goal_*.md` plan documents

The authoritative subset should be smaller and clearer.

## Proposed Canonical Live Doc Set

These are the docs that should be rewritten and actively maintained as the
current project story:

1. `README.md`
   - primary entry point
   - current status
   - backend/runtime summary
   - repo navigation

2. `docs/vision.md`
   - whole-project vision
   - v0.1 framing
   - backend roadmap positioning

3. `docs/v0_1_final_plan.md`
   - what v0.1 now means in practice
   - what is complete
   - what remains

4. `docs/rtdl/README.md`
   - language-doc index
   - canonical order for readers

5. `docs/rtdl/dsl_reference.md`
   - precise language surface

6. `docs/rtdl/programming_guide.md`
   - practical how-to guide

7. `docs/rtdl/workload_cookbook.md`
   - workload-by-workload usage patterns

8. `docs/rtdl_feature_guide.md`
   - shorter feature summary for broader readers

9. `docs/rayjoin_target.md`
   - how RayJoin fits the project

10. `docs/rayjoin_datasets.md`
    - short dataset map

11. `docs/rayjoin_public_dataset_sources.md`
    - public-source acquisition summary

12. `docs/development_reliability_process.md`
    - review/verification rules

13. `docs/ai_collaboration_workflow.md`
    - Codex/Gemini/Claude workflow

## Proposed Non-Rewrite Reference Docs

These should stay in the repo but should not be rewritten in this goal:

- `docs/goal_*.md`
- `docs/reports/*`
- older evaluation-plan documents that are mainly historical scaffolding
- reproduction matrices/checklists unless only light pointer fixes are needed

They can remain as reference material, but the rewritten canonical docs should
be what readers rely on first.

## Planned Structural Changes

### 1. Make the README shorter and more authoritative

The current README is too broad and mixes:

- vision
- implementation status
- historical goal closure
- runtime caveats
- long repository index
- build/run instructions

Rewrite target:

- shorten the README
- move detail into the canonical docs
- keep only:
  - project definition
  - current status
  - backend status
  - where to read next
  - core build/test commands

### 2. Make one clear docs entry path

The docs should be readable in a stable order:

1. `README.md`
2. `docs/vision.md`
3. `docs/v0_1_final_plan.md`
4. `docs/rtdl/README.md`
5. language docs
6. workflow/reliability docs
7. RayJoin-specific data docs

### 3. Separate “current state” from “historical goal record”

Current-state claims should live only in the canonical docs above.

Historical goal docs should not be used as the main current-state narrative.

### 4. Normalize terminology

The rewrite should use the same terms everywhere for:

- Python-hosted DSL
- native C/C++ oracle
- Embree backend
- OptiX backend
- controlled runtime vs generated code skeletons
- bounded exact-source vs synthetic benchmarks

### 5. Tighten scope language

The docs should make these boundaries obvious:

- what is fully validated
- what is bounded but accepted
- what is synthetic only
- what is still future work

## Rewrite Rules

- do not rewrite `history/`
- do not rewrite `docs/reports/`
- do not rewrite archived goal-log material
- prefer shorter authoritative docs over sprawling recap text
- use cross-links instead of duplicating long explanations
- keep current-state claims aligned with the live code and accepted reports

## Proposed Outcome

After this rewrite, the repo should have:

- a much clearer canonical documentation set
- less duplicated current-state storytelling
- cleaner onboarding for readers
- less risk of live-doc drift

## Recommendation

Proceed with the rewrite on the canonical live doc set above, and leave the
historical goal/report surface untouched except for link hygiene if needed.
