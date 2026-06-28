# Goal4792 app-lowering tutorial batch

Date: 2026-06-28

## Purpose

Goal4792 completes the remaining V4 tutorial app-lowering bridge after the
Goal4791 continuation batch. The purpose is not to teach benchmark apps as
special recipes. The purpose is to teach how a user lowers different problem
families into RTDL row relations and continuations.

The six covered concepts are:

1. ranked/top-k summaries over candidate rows,
2. contact manifold broadphase and bounded witness rows,
3. graph triangle counting as witness rows plus grouped counts,
4. robot collision as link-hit rows plus pose flags,
5. RayDB-style table rows as ray payload rows,
6. Hausdorff composition from nearest-witness rows and max reductions.

## Files changed

| File | Action | Purpose |
| --- | --- | --- |
| `examples/tutorial_programs/ranked_summary_neighbors.py` | Rewritten. | Adds `relation`, `v4`, `both`, and `visible` modes for top-k candidate-row summaries. |
| `examples/tutorial_programs/contact_manifold_lowering.py` | Rewritten. | Adds relation-first broadphase pair rows, bounded witness rows, overflow validation, and V4 surface mapping. |
| `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Rewritten. | Adds graph two-hop rows, ray rows, edge primitive rows, witness rows, grouped counts, and V4 surface mapping. |
| `examples/tutorial_programs/robot_collision_lowering.py` | Rewritten. | Adds pose/link rows, obstacle candidate rows, hit rows, pose collision flags, and V4 surface mapping. |
| `examples/tutorial_programs/raydb_table_to_ray.py` | Rewritten. | Adds table-to-ray payload rows, hit rows, dedup rows, grouped aggregates, and V4 surface mapping. |
| `examples/tutorial_programs/hausdorff_distance_recipe.py` | Rewritten. | Adds directed candidate rows, nearest-witness rows, directed max reductions, symmetric max, threshold decision, and V4 surface mapping. |
| `tutorials/current/15_ranked_summary_neighbors.md` | Added. | Teaches ranked summary as a continuation over emitted candidate rows. |
| `tutorials/current/16_contact_manifold_lowering.md` | Added. | Teaches broadphase pair rows and bounded contact witness rows. |
| `tutorials/current/17_graph_triangle_counting_lowering.md` | Added. | Teaches graph triangle counting as RTDL witness rows plus grouped count continuation. |
| `tutorials/current/18_robot_collision_lowering.md` | Added. | Teaches sampled robot collision as link-hit rows and pose-level flags. |
| `tutorials/current/19_raydb_table_to_ray.md` | Added. | Teaches table rows as ray payload rows followed by grouped aggregation. |
| `tutorials/current/20_hausdorff_composition.md` | Added. | Teaches Hausdorff as nearest-witness rows plus max reductions. |
| `tutorials/current/README.md` | Updated. | Adds lessons 15-20 to the current V4 tutorial path. |
| `examples/tutorial_programs/README.md` | Updated. | Adds `--mode both` commands and concept descriptions for the rewritten programs. |
| `examples/README.md` | Updated. | Adds the app-lowering tutorial programs to the first example path. |
| `docs/public_documentation_map.md` | Updated. | Adds the app-lowering tutorial programs to the quick-check path. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Updated. | Adds lessons 15-20 to the public documentation gate. |

## Teaching contract

Each rewritten program defaults to `--mode both` and exposes:

- `relation`: the RTDL row/continuation model,
- `v4`: the V4 operator/runtime mapping,
- `visible`: a small hand-readable flow,
- `both`: relation plus V4 mapping.

The V4 wrapper is deliberately second. The relation mode must make the user
able to say which rows exist and which continuation consumes them before they
look at the V4 surface.

## Validation

### Windows workspace

Commands:

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

The Windows Python process printed the known local prefix warning on some
subprocesses, but all commands exited successfully.

### Local Linux clean-copy simulation

Host: `192.168.1.20`

The workspace was copied to `/tmp/rtdl_goal4792_app_lowering` and run as a
clean user checkout with `PYTHONPATH=src:.`.

Commands:

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

## Non-claims

This goal does not authorize:

- a V4 public tag,
- broad V4 speedup wording,
- whole-app performance claims,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims,
- app-specific native-kernel claims.

## Goal status

Implementation and Windows/Linux validation are complete. External review is
required before marking the goal complete.
