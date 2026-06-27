# Goal4265 Partner Guidance User-Facing Cleanup

Date: 2026-06-09

## Purpose

This goal responds to the reader-facing issue that a CuPy-vs-Numba table can
mislead users when it includes rows that do not actually need a partner. It also
fixes the app-shaped wording `native scalar triangle-count primitive`, which
made a generic RTDL graph/count composition sound like an app-specific native
engine primitive.

Partner-needed continuations and Primitive-first rows are now separated in the
learner-facing matrix.

## What Changed

| File | Previous Problem | Action | User-Facing Result |
| --- | --- | --- | --- |
| `docs/learn/benchmark_partner_reference_matrix.md` | One table mixed partner-needed continuations with primitive-first rows. | Split the matrix into `Partner-Needed Continuations` and `Primitive-First Paths`. | Users only see CuPy-vs-Numba decisions where partner code is actually relevant. |
| `docs/learn/benchmark_partner_reference_matrix.md` | RayDB fused count/sum and triangle scalar-answer rows could read like partner-choice examples. | Moved those rows to the primitive-first table. | Users are told to use RTDL primitives for those rows and not to force a partner decision. |
| `docs/learn/benchmark_partner_reference_matrix.md` | Triangle scalar wording used `native scalar triangle-count primitive`. | Replaced it with `generic RT graph relationship-count composition`. | The learner doc now preserves the app-agnostic engine story. |
| `docs/learn/partner_choice_for_custom_logic.md` | Benchmark lessons mixed primitive-first rows with custom-continuation rows. | Added a short rule, a partner-needed table, and a separate primitive-first table. | The page answers "should I choose CuPy or Numba?" without implying every benchmark needs a partner. |
| `src/rtdsl/v2_6_partner_choice_guidance.py` | Programmatic guidance repeated the app-shaped triangle scalar wording. | Updated triangle-counting metadata to describe a generic graph relationship-count composition and to state that CuPy lacks a current same-contract compact-mask timing row. | Example apps and helper output now match the learner docs. |
| `src/rtdsl/current_benchmark_route_decisions.py` | Route explanation said "native RT graph summary mode" for the triangle scalar route. | Reworded the reader decision and next action around the generic graph relationship-count route. | Current route explanations no longer suggest an app-specific native primitive. |
| `src/rtdsl/v2_8_benchmark_runtime_gap.py` | Runtime-gap summary repeated the app-shaped triangle scalar wording. | Reworded it to the generic graph relationship-count composition. | Internal gap summaries stay aligned with public guidance. |
| `tests/goal3050_partner_choice_docs_test.py` | Existing doc test did not guard against this confusion. | Updated expected rows and added negative checks for app-shaped triangle primitive wording. | Future doc edits fail if they reintroduce the old wording. |
| `tests/goal3054_v2_6_partner_choice_guidance_test.py` | Existing metadata test did not check the generic triangle scalar language. | Added checks for the generic composition and table split. | Programmatic guidance cannot drift back silently. |
| `tests/goal4265_partner_guidance_user_facing_cleanup_test.py` | No focused regression test existed for the user-facing split. | Added a dedicated test for the partner-needed/primitive-first separation. | The cleanup is machine-checked. |

## Current User Rule

```text
If the generic RTDL primitive or composition already answers the query, use it.
Only choose CuPy or Numba for the remaining custom continuation logic.
```

## Clarified Rows

| Row | Correct User Guidance |
| --- | --- |
| RayDB fused count/sum | Use fused generic grouped-reduction primitives; no partner is needed. |
| RayDB unfused grouped min/max/count/sum/avg | Use Numba for the currently demonstrated custom continuation; no same-contract CuPy-vs-Numba speedup is claimed. |
| Triangle scalar answer | Use generic RT graph relationship-count composition; no partner is needed. |
| Triangle candidate-row compaction | Use Numba if the app explicitly needs candidate rows; no same-contract CuPy compact-mask speedup is claimed. |

## Claim Boundary

No release, public speedup, or broad partner-speedup claim is authorized by this
cleanup. This is a user-facing documentation and metadata consistency goal. It
does not add a new native ABI, does not auto-select partners, and does not
authorize app-specific native engine behavior.

## Validation

Focused validation:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal3050_partner_choice_docs_test \
  tests.goal3054_v2_6_partner_choice_guidance_test \
  tests.goal3928_numba_reference_discovery_index_test \
  tests.goal3929_numba_reference_parity_expectations_test \
  tests.goal4265_partner_guidance_user_facing_cleanup_test
```
