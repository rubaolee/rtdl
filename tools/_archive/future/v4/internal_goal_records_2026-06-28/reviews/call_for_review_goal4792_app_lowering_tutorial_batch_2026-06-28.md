# Call for review: Goal4792 app-lowering tutorial batch

Date: 2026-06-28

## Review request

Please review Goal4792 as a tutorial-quality and public-surface correctness
gate.

The goal adds the remaining app-lowering bridge lessons after Goal4791:

1. ranked/top-k summaries,
2. contact manifold lowering,
3. graph triangle counting lowering,
4. robot collision lowering,
5. RayDB table-to-ray lowering,
6. Hausdorff composition.

The review should determine whether the materials teach RTDL row relations and
continuations first, and only then introduce the V4 operator/runtime wrapper as
the implementation mapping.

## Primary files to inspect

Tutorial programs:

- `examples/tutorial_programs/ranked_summary_neighbors.py`
- `examples/tutorial_programs/contact_manifold_lowering.py`
- `examples/tutorial_programs/triangle_counting_graph_lowering.py`
- `examples/tutorial_programs/robot_collision_lowering.py`
- `examples/tutorial_programs/raydb_table_to_ray.py`
- `examples/tutorial_programs/hausdorff_distance_recipe.py`

Tutorial pages:

- `tutorials/current/15_ranked_summary_neighbors.md`
- `tutorials/current/16_contact_manifold_lowering.md`
- `tutorials/current/17_graph_triangle_counting_lowering.md`
- `tutorials/current/18_robot_collision_lowering.md`
- `tutorials/current/19_raydb_table_to_ray.md`
- `tutorials/current/20_hausdorff_composition.md`

Indexes and gates:

- `tutorials/current/README.md`
- `examples/tutorial_programs/README.md`
- `examples/README.md`
- `docs/public_documentation_map.md`
- `tests/v4_goal4640_public_docs_cleanup_test.py`

Completion record:

- `docs/engineering/goal4792_app_lowering_tutorial_batch_2026-06-28.md`

## Validation already run

Windows:

```powershell
py -3 examples\tutorial_programs\ranked_summary_neighbors.py --mode both
py -3 examples\tutorial_programs\contact_manifold_lowering.py --mode both
py -3 examples\tutorial_programs\triangle_counting_graph_lowering.py --mode both
py -3 examples\tutorial_programs\robot_collision_lowering.py --mode both
py -3 examples\tutorial_programs\raydb_table_to_ray.py --mode both
py -3 examples\tutorial_programs\hausdorff_distance_recipe.py --mode both
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 86.685s
OK
```

Linux clean-copy simulation on `192.168.1.20`, copied to `/tmp/rtdl_goal4792_app_lowering`:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/ranked_summary_neighbors.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/contact_manifold_lowering.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/triangle_counting_graph_lowering.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/robot_collision_lowering.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/raydb_table_to_ray.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/hausdorff_distance_recipe.py --mode both
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 32.245s
OK
```

## Required questions

1. Do the six rewritten programs teach relation rows and continuations before V4 wrapper calls?
2. Do the new tutorial pages avoid teaching benchmark apps as special recipes?
3. Do the programs use coherent modes: `relation`, `v4`, `both`, and `visible`?
4. Are partner statements honest and bounded?
5. Does the ranked-summary lesson correctly state that app-owned scoring is separate from V4 planning?
6. Does the Hausdorff lesson clearly separate exact nearest-witness output from threshold decision output?
7. Are public links and commands consistent?
8. Are Windows and Linux validations sufficient for this goal?
9. Should Goal4792 be accepted as complete, require amendments, or be blocked?

## Allowed verdict labels

- `approve_goal4792_app_lowering_tutorial_batch_complete`
- `approve_with_required_amendments`
- `block_goal4792_app_lowering_tutorial_batch`

## Non-authorization boundary

This review must not authorize:

- a V4 public tag,
- broad V4 speedup wording,
- whole-app performance claims,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims,
- app-specific native-kernel claims.
