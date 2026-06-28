# V4 Tutorial/App Gap Remediation

Date: 2026-06-27

This internal record documents the remediation pass after the two-agent
tutorial/app alignment audit.

## Remediation Summary

The alignment audit found that the public tutorials taught V4 concepts and
planner-level recipes, but did not yet teach enough app-lowering material for
users to build the full benchmark and paper-reproduction apps.

This pass adds executable teaching programs for every P0 gap and adds public
docs for benchmark runner protocol and paper-reproduction scope.

## New Tutorial Programs

| Gap | New file | What it teaches |
| --- | --- | --- |
| Barnes-Hut aggregate frontier | `examples/tutorial_programs/aggregate_frontier_rows.py` | Body/cell inputs -> aggregate/exact frontier rows -> vector contribution rows -> grouped force output. |
| RTDBSCAN component union | `examples/tutorial_programs/component_union_from_radius.py` | Radius-neighbor rows -> core flags -> union edges -> component labels/signature. |
| RTNN ranked summary | `examples/tutorial_programs/ranked_summary_neighbors.py` | Candidate rows -> radius filter -> bounded top-k rows -> per-query summary. |
| Contact bounded witnesses | `examples/tutorial_programs/bounded_witness_collection.py` | Candidate witnesses -> bounded collection -> overflow validation rows. |
| Triangle graph lowering | `examples/tutorial_programs/triangle_counting_graph_lowering.py` | Directed edges -> two-hop rows -> triangle witness rows -> grouped counts. |
| Robot collision lowering | `examples/tutorial_programs/robot_collision_lowering.py` | Poses/links/obstacles -> link segments -> candidate rows -> collision flags. |
| Hausdorff composition | `examples/tutorial_programs/hausdorff_distance_recipe.py` | Directed nearest rows -> directed max -> undirected distance -> threshold decision. |
| RayDB table-to-ray lowering | `examples/tutorial_programs/raydb_table_to_ray.py` | Table rows -> rays/primitives/payloads -> hit rows -> dedup -> grouped aggregate. |
| RayJoin topology bridge | `examples/tutorial_programs/rayjoin_topology_intro.py` | Candidate pairs -> topology rows -> boundary-policy filtered output. |

## New Public Docs

| File | Purpose |
| --- | --- |
| `tutorials/current/09_benchmark_harness_protocol.md` | Teaches prepared runner timing boundaries, warmup, validation, and capacity/overflow records. |
| `examples/paper_reproduction/paper_reproduction_scope.md` | Explains RT-BarnesHut and RayJoin paper-oriented wrappers, their routed app, and reading order. |

## Public Path Updates

- `examples/tutorial_programs/README.md` now lists the new runnable programs.
- `tutorials/current/README.md` now includes the benchmark runner protocol.
- `tutorials/current/07_benchmark_apps.md` now links each complex app idea to a
  concrete app-lowering program.
- `examples/README.md` now includes representative app-lowering commands.
- `examples/paper_reproduction/README.md` now points to the paper scope note.
- `docs/public_documentation_map.md` and `docs/learn/source_tree_doctor.md`
  now include representative checks for the added app-lowering path.

## Verification

The following checks were run during this pass:

- all nine new tutorial programs run without CUDA;
- public forbidden-language scan found no public leakage;
- `tests.v4_goal4640_public_docs_cleanup_test` passed;
- release packaging/staging/clean-checkout tests passed;
- `scripts/v4_catalog_regression_gate.py --mode dry-run` passed.

The strict universe audit reported only expected local debris before staging:
the newly added public tutorial files were untracked. The final release gate
must be rerun after staging and commit.
