# Goal4788 Stage 1 Tutorial File Audit

Date: 2026-06-28

| File | Should be current? | Content verdict | Action taken |
| --- | --- | --- | --- |
| `tutorials/current/04_relations_and_operators.md` | Yes. | Previous page leaned too much toward planner/catalog usage. | Rewritten around relation rows, data flow, and app meaning boundaries. |
| `tutorials/current/05_fixed_radius_neighbors.md` | Yes. | Needed as the approved lesson 05. | Added new fixed-radius lesson with runnable snippets and program links. |
| `tutorials/current/06_nearest_witness.md` | Yes. | Needed as the approved lesson 06. | Added new nearest-witness lesson with runnable snippets and program links. |
| `tutorials/current/05_prepare_run_continue.md` | No, not at this location. | Useful later concept, but wrong position for the approved foundation sequence. | Removed from current path and archived. |
| `tutorials/current/06_measure_a_program.md` | No, not at this location. | Useful later concept, but wrong position for the approved foundation sequence. | Removed from current path and archived. |
| `examples/tutorial_programs/operator_primitives.py` | Yes. | Useful but too catalog-like. | Added relation-row examples and explicit data-flow payload. |
| `examples/tutorial_programs/v4_frontdoor_quickstart.py` | Yes. | Useful but too release-boundary-like for a learner. | Rewritten as a clean import/operator/partner quickstart while keeping stable test fields. |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Yes. | Already teaches candidate checks, neighbor rows, threshold rows. | Audited; no code change required. |
| `examples/tutorial_programs/nearest_neighbor.py` | Yes. | Already teaches candidate rows and argmin nearest rows. | Audited; no code change required. |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Yes. | Useful companion for top-k/ranked continuation. | Audited; no code change required. |
| `examples/tutorial_programs/README.md` | Yes. | Needed order and command corrections. | Moved sorting before quickstart and added missing custom-predicate command. |
| `tutorials/current/README.md` | Yes. | Linked to stale 05/06 pages. | Updated lesson 05/06 links. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Yes, as gate code. | Public docs list referenced removed stale pages. | Updated to check new 05/06 pages. |

## Open Follow-Up

Later batches must rewrite or archive the remaining current pages:

- `tutorials/current/07_benchmark_apps.md`
- `tutorials/current/08_choose_a_partner.md`
- `tutorials/current/09_benchmark_harness_protocol.md`

Those are outside Goal4788 and remain scheduled by Goal4792/Goal4793.
