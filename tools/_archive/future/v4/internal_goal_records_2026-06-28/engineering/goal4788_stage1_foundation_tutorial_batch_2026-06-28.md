# Goal4788: Stage 1 Foundation Tutorial Batch

Date: 2026-06-28

Status: implemented, pending external review.

## Scope

Goal4788 implements the first foundation batch approved by Goal4787:

1. Relations and operators.
2. Fixed-radius neighbor relation.
3. Nearest-witness relation and ranked-summary continuation.

This goal does not implement later spatial, ray/triangle, grouped continuation,
app-lowering, partner, measurement, callback, or benchmark-bridge lessons.

## Old Material Inspected

| Material | What was inherited |
| --- | --- |
| `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_language_reference.py` | The kernel pattern `input -> traverse -> refine -> emit` and relation-row vocabulary. |
| `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_fixed_radius_neighbors_reference.py` | Fixed-radius kernel shape, emitted `(query_id, neighbor_id, distance)` rows. |
| `tools/_archive/history/examples_legacy_2026-06-27/reference_legacy/rtdl_knn_rows_reference.py` | KNN/nearest row shape with `neighbor_rank`. |
| `tools/_archive/history/tutorial_archive/nearest_neighbor_workloads.md` | The distinction between fixed-radius rows and nearest/top-k rows. |

## Files Changed

| File | Action | Purpose |
| --- | --- | --- |
| `tutorials/current/04_relations_and_operators.md` | Rewritten. | Teaches row vocabulary and the relation/operator/continuation pipeline before planner usage. |
| `tutorials/current/05_fixed_radius_neighbors.md` | Added. | Teaches radius-neighbor rows, candidate checks, neighbor rows, and threshold continuation. |
| `tutorials/current/06_nearest_witness.md` | Added. | Teaches candidate distance rows, argmin nearest witness, and ranked summary. |
| `tutorials/current/05_prepare_run_continue.md` | Removed from current path. | Old sequence page conflicted with the approved Goal4787 order. |
| `tutorials/current/06_measure_a_program.md` | Removed from current path. | Measurement moves to a later approved lesson. |
| `tools/_archive/history/tutorial_archive/goal4788_replaced_current_pages_2026-06-28/05_prepare_run_continue.md` | Added archive copy. | Preserves the old page outside the current user path. |
| `tools/_archive/history/tutorial_archive/goal4788_replaced_current_pages_2026-06-28/06_measure_a_program.md` | Added archive copy. | Preserves the old page outside the current user path. |
| `examples/tutorial_programs/operator_primitives.py` | Updated. | Adds concrete `relation_row_examples`, data-flow text, and continuation classes instead of only catalog rows. |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | Updated. | Turns the output into a user-facing import/operator/partner quickstart while preserving stable test fields. |
| `examples/tutorial_programs/README.md` | Updated. | Puts hello world and sorting first, then relation/operator quickstart; adds missing callback-planning command. |
| `tutorials/current/README.md` | Updated. | Points lessons 05 and 06 to fixed-radius and nearest-witness pages. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Updated. | Public-doc gate now checks the new 05/06 current pages instead of removed stale pages. |

## Teaching Outcome

After this batch, a learner can run the first six current lessons and understand:

- a relation row as a table fact produced by traversal and refinement;
- how V4 operator surfaces name generic relation-producing work;
- how fixed-radius rows differ from nearest-witness rows;
- how candidate rows become neighbor rows, nearest rows, threshold rows, ranked
  rows, and summary rows;
- why app meaning remains outside the generic operator.

## Validation Summary

Validation details are recorded in:

- `docs/engineering/goal4788_stage1_tutorial_linux_validation_2026-06-28.md`
- `docs/engineering/goal4788_stage1_tutorial_link_validation_2026-06-28.md`
- `docs/engineering/goal4788_stage1_tutorial_file_audit_2026-06-28.md`

Final local Linux validation directory:

`/tmp/rtdl_goal4788_full_check`

Final Linux results:

- Goal4788 tutorial scripts: passed.
- `tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test`: passed, 7 tests.
- `tests.v4_goal4640_public_docs_cleanup_test`: passed, 14 tests.

## Non-Authorization

Goal4788 does not claim the full tutorial surface is complete. It only completes
the first implementation batch for the foundation lessons. Later batches
Goal4789-Goal4793 remain required.
