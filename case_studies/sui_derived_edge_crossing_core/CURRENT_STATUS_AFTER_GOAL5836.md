# Current status after Goal5836

Date: 2026-09-01

This file is the current operational status for the Sui-derived edge-crossing
case study. The adjacent `README.md` is a hash-bound Goal5835 historical input
and must not be edited in place. In particular, its final sentence saying that
Goal5836 is still required is historical. Goal5836 later completed at its A1
terminal negative branch.

## Current classification

```text
Goal5835:
BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE

Goal5836:
MATERIAL_PREDICATE_DIFFERENCE
TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE__A2_NOT_REACHABLE

paper_app_status: NOT_A_PAPER_APP
```

Goal5835 constructs application-shaped swept-segment and obstacle-edge objects,
reproduces the exact public bytes of the frozen Goal5834 fixtures, and composes
their inherited 33 true-OptiX launches with an independent active-set oracle.
It adds no Goal5835 GPU launch. Its receipt runner does not execute the
case-study front door, construct trajectories with
`trajectory_to_swept_segments`, or derive positive edges from a complete mesh.
It is therefore evidence for a bounded semantic projection, not evidence that
the paper application or even this case-study front door ran end to end.

Goal5836 statically inspected the exact arXiv v2 paper and exact author commit.
The author's benchmark uses a strongly connected directed obstacle-edge graph
to address inside starts for one-sided rays against hollow round curves.
Goal5835 keeps one arbitrary direction for a deduplicated edge and excludes
initial overlap. This is a material predicate difference, not a performance
detail, so the preregistered transaction terminated before input freeze,
execution, GPU work, timing, or Paper App promotion.

## Allowed and prohibited wording

| Wording | Status |
|---|---|
| Bounded Sui-derived app-semantic projection over inherited true-OptiX fixtures | Allowed |
| Goal5836 completed with a negative source-fidelity result | Allowed |
| Goal5835 executed the case-study front door | Prohibited |
| Goal5835 reproduced the paper application or full RT-CCD | Prohibited |
| Goal5836 successfully promoted a Paper App | Prohibited |
| Goal5835/5836 provide new performance evidence | Prohibited |

## Open engineering findings

- No positive registered row reconstructs a complete triangle or mesh.
- The frozen fixture adapter assigns `sphere_id=primitive_index`; a connected
  two-segment trajectory is represented with sphere IDs `[0, 1]`.
- `execute_registered_problem` does not reject a result whose bit count differs
  from the edge count or whose reported collision differs from `OR(bits)`.
- Duplicate triangle IDs can make the chosen directed shared edge depend on
  caller order.
- The historical Goal5835 receipt embeds absolute source paths.
- `SweptSphereSegment` accepts non-integral numeric IDs inside the u32 range.

These defects are preserved as audited historical facts. Repairing hash-bound
Goal5835 source in place would invalidate Goal5836 custody. Any implementation
repair must be a separately named successor with new prospective evidence.

## Review and evidence state

The post-Goal5836 review is an internal hostile self-audit only. The owner
explicitly deferred independent external review until returning from travel.
External-review count is zero and no consensus is claimed. No pod is required
for this audit.

Controlling new audit files:

- `history/internal_docs/goal5835_goal5836_strict_audit_20260901/STRICT_AUDIT_AUTHORITY.json`
- `history/internal_docs/goal5835_goal5836_strict_internal_audit_20260901.md`
- `history/internal_docs/self_review_goal5835_goal5836_strict_audit_20260901.md`

Verify locally with:

```bash
PYTHONPATH=src:. python3 scripts/audit_goal5835_goal5836.py --verify-stored
PYTHONPATH=src:. python3 -m unittest \
  tests.goal5835_goal5836_strict_audit_test -v
```
