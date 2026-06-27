# V4 Goal4723 Complete 10-App Protocol Freeze

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `complete_10_app_v2_14_vs_v4_protocol_frozen_final_tag_blocked_until_matrix_closure`

## Purpose

Goal4723 freezes the full 10 benchmark-app app-level V2.14-vs-V4 protocol
before further POD spending. It replaces the too-early final-tag path with a
hard app-level evidence gate.

## Protocol Artifact

Machine-readable protocol:

- `future/v4/evidence/v4_goal4723_complete_10_app_protocol_2026-06-26.json`

Context document:

- `future/v4/v2_14_vs_v4_per_app_implementation_comparison_2026-06-26.md`

## Frozen App Set

The protocol includes all 10 promoted apps exactly once:

1. `rt_dbscan`
2. `raydb_style`
3. `triangle_counting`
4. `librts_spatial_index`
5. `hausdorff_xhd`
6. `robot_collision`
7. `contact_manifold`
8. `rtnn`
9. `spatial_rayjoin`
10. `barnes_hut`

## Current Row Classes

| Row class | Apps |
| --- | --- |
| `measured_existing_full_app_row` | `rt_dbscan`, `raydb_style`, `triangle_counting`, `librts_spatial_index`, `hausdorff_xhd` |
| `measured_no_win_candidate` | `rtnn` |
| `route_gap_requires_generic_operator` | `robot_collision`, `contact_manifold` |
| `no_v4_route_blocker` | `spatial_rayjoin` |
| `deferred_no_app_identity_route` | `barnes_hut` |

## Critical Rules

- V2 means exactly V2.14.
- Same RT hardware is required for comparable final rows.
- Correctness parity is required before timing can be credited.
- No silent fallback to V2/V3 routes is allowed.
- No app-specific native kernels are authorized.
- Partner migration does not count as a V4 speed win.
- Same-primitive productization does not count as a V4 speed win by itself.
- Operator/subprobe evidence cannot substitute for complete app-level evidence.
- Final public tag is blocked until Goal4733.

## What This Means For The Remaining Five Apps

- `robot_collision`: must produce a full app route or prove same-primitive
  improvement over V2.14 any-hit collision primitive.
- `contact_manifold`: must produce a complete bounded contact/witness route or
  name the missing generic collect operator.
- `rtnn`: candidate evidence already says serious scale is parity/slower; it
  must become a formal measured no-win row unless a new generic lever is built.
- `spatial_rayjoin`: current blocker; requires a generic relation-topology
  route or explicit no-route row.
- `barnes_hut`: aggregate-frontier subprobe is not a full app result; needs a
  generic aggregate-tree weighted-vector workflow or explicit no-go.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4723_complete_app_protocol_test`

Expected result:

- all 10 apps present exactly once;
- all row classes are approved;
- incomplete rows cannot authorize performance claims;
- final tag remains blocked.

## Goal-Level Decision Audit

1. Was I being stupid?
   No for this goal. This directly fixes the earlier mistake: approaching final
   V4 tag without a complete 10-app app-level protocol.

2. If yes, what action made the decision stupid?
   Not applicable here. The stupid action would be to let the five incomplete
   apps remain vague.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Freeze missing-route rows explicitly before spending POD time.

4. Can I now try the different path that actually solves the problem?
   Yes. Goals4724-4729 must now turn the five incomplete rows into measured
   rows or explicit no-go rows.

## Non-Authorization

Goal4723 does not authorize final V4 tag, broad V4 speedup wording,
whole-application speedups, all-benchmark speedups, arbitrary callback support,
raw OptiX callbacks, C ABI, embedding, non-Python host bindings, app-specific
native kernels, or using operator/subprobe evidence as complete app-level
evidence.
