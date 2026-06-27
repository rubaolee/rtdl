# Goal 4 Spec

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-4-language-docs-authoring
Repo: /Users/rl2025/rtdl_python_only
Source Commit: 865ae551ad0e7cb064e14220c39f18c4298c4299

## Goal

Turn RTDL into a documented, teachable language for its current implemented surface:

- `lsi`
- `pip`
- `overlay`

The result should be usable by:

- Codex,
- Gemini,
- human developers.

## Deliverables

1. Language-level documentation
   - syntax and authoring model
   - kernel structure
   - supported geometry/layout concepts
   - predicates
   - emit fields
   - workload-specific rules
   - current limitations and non-goals

2. Programming guidance
   - how to write RTDL kernels
   - how to choose layouts and roles
   - how to use RayJoin datasets with RTDL
   - how to interpret current backend limitations

3. Example set
   - canonical language examples for all 3 workloads
   - Codex-authored examples
   - Gemini-authored examples

4. Validation
   - tests that compile and lower documented examples
   - tests that validate authored examples from both agents
   - evidence that docs are strong enough for independent authoring

## Constraints

- Stay within the current implemented RTDL surface.
- Do not invent unsupported runtime capabilities.
- Do not claim exact precision or full GPU execution.
- The language can remain Python-hosted, but must be documented as a language with explicit grammar-like rules and semantics.

## Completion Criteria

- RTDL has a clean documentation set for the current language surface.
- At least one non-trivial Codex-authored program per current workload is validated.
- At least one Gemini-authored program per current workload is validated.
- The example tests pass.
- Codex and Gemini agree that Goal 4 is complete.
