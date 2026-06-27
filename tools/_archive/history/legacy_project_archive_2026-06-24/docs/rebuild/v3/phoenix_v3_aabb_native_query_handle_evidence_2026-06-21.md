# Phoenix V3 AABB Native Query-Handle Evidence

Status: `aabb_native_query_handle_m7_candidate_pending_external_review`

This packet evaluates a generic engine change: OptiX AABB `range_intersection_rows` reuses prepared native box-query handles. The Contact Manifold fixture is only the evidence harness.

## Candidate Summary

- Material wall-speedup floor: `1.20x`.
- Best cold-plus-collect wall speedup: `1.719x`.
- Largest-scale cold-plus-collect wall speedup: `1.637x`.
- Best query-total speedup: `1.867x`.
- Native query-handle cache observed: `True`.

## Rows

| grid_count | repeat | OptiX/Embree cold+collect | OptiX/Embree query total | OptiX native cache | CPU reference |
|---:|---:|---:|---:|---|---|
| 32768 | 50 | 1.719x | 1.867x | {'native_range_intersection_entries': 1, 'native_range_intersection_hits': 52, 'native_range_intersection_misses': 1, 'point_membership_entries': 0, 'point_membership_hits': 0, 'point_membership_misses': 0, 'range_intersection_entries': 1, 'range_intersection_hits': 52, 'range_intersection_misses': 1} | True |
| 65536 | 50 | 1.637x | 1.743x | {'native_range_intersection_entries': 1, 'native_range_intersection_hits': 52, 'native_range_intersection_misses': 1, 'point_membership_entries': 0, 'point_membership_hits': 0, 'point_membership_misses': 0, 'range_intersection_entries': 1, 'range_intersection_hits': 52, 'range_intersection_misses': 1} | True |

## Boundaries

- Release authorized: `False`.
- Public speedup claim authorized: `False`.
- Broad V3-over-V2 claim authorized: `False`.
- M7 promotion authorized: `False` until external review and Codex consensus close.

## Interpretation

The native prepared-query handle path changes AABB from useful cleanup to a real V3 performance candidate. On the RTX 4000 Ada pod, both serious rows clear the 1.20x cold-plus-collect floor against Embree under the same generic AABB candidate-stream contract. This still does not authorize release wording or M7 promotion until external review and Codex consensus close.

## Next Action

Send this packet for external review. If accepted, update the Phoenix M7 row classification with an AABB native-query-handle row. Keep public copy row-scoped: generic AABB candidate streaming only, not full contact solving and not broad V3-over-V2 speedup.

## Goal-Level Decision Audit

- `decision`: Record native prepared-query handle reuse as an M7 candidate pending external review, not as an already promoted V3 row.
- `was_i_foolish`: No. This uses the predeclared serious scale, material wall floor, same hardware, and keeps release/M7 flags false before review.
- `foolish_actions`: The foolish action would be to treat one 32k result as final, omit the 65k rerun, or promote a contact-specific story instead of the generic AABB contract.
- `other_path`: I could have moved to a different app after the old no-go result, but the evidence pointed to native query lifetime as the actual generic bottleneck.
- `different_path_now`: Continue through external review and M7 classification, then use the same pattern on the remaining generic-engine queue rather than hand-tuning app code.
