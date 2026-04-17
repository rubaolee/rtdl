# Goal 504: Barnes-Hut Force App Implementation

Date: 2026-04-17

Status: accepted with 2-AI consensus; Gemini Flash retry capacity-blocked

Version line: `v0.8` app-building over existing RTDL language features

## Purpose

Goal499 classified RT-BarnesHut as a controlled language-growth candidate. It
was explicitly higher risk than Hausdorff distance and robot DCD because a
faithful version needs hierarchical tree-node primitives, an opening predicate,
and vector reductions that RTDL does not yet expose.

Goal504 implements the bounded app-level version first. It uses existing RTDL
nearest-neighbor rows for body-to-node candidate discovery and keeps quadtree
construction, opening-rule evaluation, and force-vector math in Python.

## Implementation

New app:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_barnes_hut_force_app.py`

The app uses the existing public `fixed_radius_neighbors` RTDL predicate:

- Python creates six 2D bodies with masses.
- Python builds a one-level quadtree and computes each node's center of mass.
- RTDL emits body-to-quadtree-node candidate rows.
- Python applies a Barnes-Hut-style opening rule.
- Python computes approximate force vectors and compares them against a
  brute-force all-pairs oracle.

This follows the `v0.8` rule: use current RTDL features first, and document
language gaps instead of hiding them behind a paper-specific shortcut.

## Data Transformation

| Input | RTDL output | Python output |
| --- | --- | --- |
| bodies with position and mass | body point probes | body metadata |
| Python-built quadtree nodes | node center-of-mass build points | node mass/size/body membership metadata |
| body points plus node points | body-to-node candidate rows | accepted node IDs and exact fallback body IDs |
| candidates plus metadata | none | approximate force vectors and oracle error rows |

## Public Docs Updated

- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`

Public example harness updated:

- `/Users/rl2025/rtdl_python_only/scripts/goal410_tutorial_example_check.py`

Regression test added:

- `/Users/rl2025/rtdl_python_only/tests/goal504_barnes_hut_force_app_test.py`

## Validation

Command:

```text
PYTHONPATH=src:. python3 examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

Result:

```text
"app": "barnes_hut_force_app"
"candidate_row_count": 24
"max_relative_error": 0.006558786879803883
```

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal504_barnes_hut_force_app_test tests.goal411_public_surface_ci_automation_test -v
```

Result:

```text
Ran 6 tests in 0.107s
OK
```

Command:

```text
PYTHONPATH=src:. python3 examples/rtdl_feature_quickstart_cookbook.py
```

Result:

```text
feature_count = 19
barnes_hut_force_app present
```

Command:

```text
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_barnes_hut_force_app.py examples/rtdl_feature_quickstart_cookbook.py tests/goal504_barnes_hut_force_app_test.py scripts/goal410_tutorial_example_check.py
git diff --check
```

Result:

```text
OK
```

## Honesty Boundary

This is a bounded one-level 2D approximation. It does not claim to implement the
full RT-BarnesHut paper system. In particular, RTDL does not yet provide:

- hierarchical tree-node input types
- a built-in Barnes-Hut opening predicate
- emitted force-contribution rows as a first-class primitive
- grouped vector-sum reductions
- timestep integration
- a faithful RT traversal over heterogeneous internal and leaf nodes

Those are now concrete language-growth candidates exposed by v0.8 app work.

## Verdict

Goal504 is accepted with Claude and Codex consensus. Gemini Flash review was
attempted but capacity-blocked by the remote service. The implementation
satisfies the Goal499 recommendation for a controlled Barnes-Hut prototype:
build the app with current RTDL candidate-row machinery where possible, keep the
rest in Python, and explicitly record the remaining language gaps.
