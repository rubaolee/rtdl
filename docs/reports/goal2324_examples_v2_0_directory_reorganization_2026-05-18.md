# Goal2324: v2.0 Examples Directory Reorganization

Status: `implemented`

Date: 2026-05-18

## Purpose

The v2.0 release made the front page clean, but the `examples/` directory still
looked like a flat dump of scripts. That is frustrating for a learner because
it asks them to infer version, purpose, feature family, maturity, and claim
boundary from filenames.

This goal reorganizes examples by version and reader intent.

## New Layout

| Directory | Purpose | Operation |
| --- | --- | --- |
| `examples/v2_0/getting_started/` | first runnable programs | moved hello-world, backend-selection, and feature-cookbook examples here |
| `examples/v2_0/features/ray_queries/` | ray-query primitives | moved any-hit, visibility, and reduction examples here |
| `examples/v2_0/features/neighbors/` | neighbor primitives | moved fixed-radius and KNN row examples here |
| `examples/v2_0/features/database/` | columnar scan/reduction primitives | moved DB scan, grouped-count, and grouped-sum examples here |
| `examples/v2_0/features/graph/` | graph primitive examples | moved BFS/frontier and triangle-count examples here |
| `examples/v2_0/features/spatial/` | spatial row and summary features | moved segment/polygon and polygon-set examples here |
| `examples/v2_0/apps/` | complete applications | moved analytics, geospatial, ML, robotics, simulation, and trajectory apps into purpose subdirectories |
| `examples/v2_0/partners/` | partner/user continuations | moved partner any-hit, CuPy RawKernel control apps, and user C++ continuation examples here |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/` | Hausdorff vs X-HD-style study | moved serious Hausdorff function/lab/benchmark files here |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/` | spatial vs RayJoin-style study | moved the RayJoin-inspired spatial join app here |
| `examples/legacy_or_backend_proofs/` | proof/backend-maintenance examples | moved Apple RT and HIPRT proof demos out of the learner path |
| `examples/reference/`, `examples/generated/`, `examples/internal/`, `examples/visual_demo/` | existing non-mainline areas | preserved, with the root README marking their audience |

## Compatibility

The flat root `rtdl_*.py` files were removed from the visible GitHub directory
view. A lazy compatibility map in `examples/__init__.py` preserves old
module-style imports such as `from examples import rtdl_graph_bfs`.

New docs and commands should use explicit `examples/v2_0/...` paths.

## Public Docs Updated

Current learner/user docs were updated to the new paths:

| Area | Operation |
| --- | --- |
| root README and quick tutorial | examples path references now point at `examples/v2_0/...` |
| tutorials | command snippets now use versioned example paths |
| feature pages | feature-specific links now point at versioned feature directories |
| app catalog and support matrix | app paths now point at versioned app/research locations |
| v2.0 release report | smoke commands now use versioned examples |
| scripts and current tests | direct imports now use `examples.v2_0...` package paths instead of flat `examples.rtdl_*` modules |

Historical reports, handoffs, and archived history were deliberately not
rewritten.

## Validation

Validation is covered by:

- `tests.goal2324_examples_v2_0_directory_reorganization_test`
- focused smoke tests for the moved examples
- `py_compile` over the moved v2.0 examples

## Verdict

`accept`: `examples/` now has a versioned v2.0 learner path, feature grouping,
app grouping, partner grouping, and special paper-facing benchmark directories
for Hausdorff/X-HD and spatial/RayJoin work.
