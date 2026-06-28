# Goal4789 Spatial Primitives Tutorial Batch

Date: 2026-06-28

## Purpose

Goal4789 repairs the Stage 1 spatial-primitives tutorial path so it teaches
RTDL kernel thinking first, then V4 operator/runtime mapping second. The target
is not to teach GIS or application algorithms. The target is to teach how users
express RT-shaped relations: inputs, traversal, refinement predicates, emitted
rows, and later continuations.

## Files Changed

| File | Action | Purpose |
| --- | --- | --- |
| `examples/tutorial_programs/point_in_polygon.py` | Rewritten with `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both`. | Teach point/polygon containment as an RTDL kernel relation before showing the V4 AABB broadphase surface. |
| `examples/tutorial_programs/spatial_join_lsi.py` | Rewritten with `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both`. | Teach segment-pair intersection as an RTDL kernel relation before showing the V4 AABB broadphase surface. |
| `tutorials/current/08_point_in_polygon.md` | Rewritten kernel-first. | Show the actual `@rt.kernel` shape, copy-paste runnable snippets, row meaning, visible broadphase, and V4 mapping. |
| `tutorials/current/09_line_segment_intersection_spatial_join.md` | Rewritten kernel-first. | Show the actual `@rt.kernel` shape, copy-paste runnable snippets, row meaning, visible AABB overlap, and V4 mapping. |
| `examples/tutorial_programs/README.md` | Updated commands and suggested order. | Make PIP/LSI explicitly run as `--mode both` and describe their kernel/V4 split. |
| `examples/README.md` | Updated quick commands. | Keep the public examples path aligned with the repaired dual-mode programs. |
| `docs/public_documentation_map.md` | Updated quick commands. | Keep the public documentation command path aligned with the repaired dual-mode programs. |

## Design Rules Applied

1. Kernel mode is the programming model.
2. Visible mode is only the Python mirror that helps learners inspect rows.
3. V4 mode is the runtime/operator mapping after the relation is understood.
4. No tutorial asks users to learn a black-box "do the app for me" call.
5. The V4 AABB route is described honestly as broadphase candidate generation
   and prepared routing, not as a complete replacement for exact PIP or exact
   line-segment intersection semantics.
6. The scripts remain runnable without CUDA.

## Validation

Windows:

```text
py -3 examples\tutorial_programs\point_in_polygon.py --mode both
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode both
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 71.224s
OK
```

Linux clean-copy validation on `192.168.1.20`:

```text
cd /tmp/rtdl_goal4789_spatial
PYTHONPATH=src:. python3 examples/tutorial_programs/point_in_polygon.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/spatial_join_lsi.py --mode both
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 27.727s
OK
```

## Completion Claim

Goal4789 is ready for external review as the Stage 1 spatial-primitives tutorial
batch: AABB, point-in-polygon, and line-segment intersection now follow the
kernel-first/V4-second teaching rule and pass Windows plus Linux public-surface
validation.

This record does not authorize any new performance claim, release claim,
Tier-3 callback claim, raw OptiX callback claim, C ABI claim, embedding claim,
or full paper-reproduction claim.
