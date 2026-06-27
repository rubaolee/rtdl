# Call For Review: V4 Goal4652 App Route Binding

Date: 2026-06-25
Requesting agent: Codex
Goal: 4652

## Review Packet

Please review:

- `future/v4/v4_goal4652_app_route_binding_or_blocker_declaration_2026-06-25.md`
- `future/v4/evidence/v4_goal4652_app_route_binding_matrix_2026-06-25.json`
- `src/rtdsl/v4_app_route_binding.py`
- `src/rtdsl/v4.py`
- `tests/v4_goal4652_app_route_binding_test.py`

Context:

- Prior goals 4647-4651 separated V2.14 partner history from V4 certified
  partner support and preserved the rule that partner migration is not a V4
  speed win.
- Goal4652 must happen before Goal4653 protocol freeze.
- This goal does not authorize app-level speed claims; it only declares V4
  routes or blockers for the benchmark apps.

## Questions

1. Are all ten benchmark apps explicitly bound or blocked?
2. Is the route classification honest, especially for partial routes such as
   `hausdorff_xhd`, `robot_collision`, `contact_manifold`, and `rtnn`?
3. Does the implementation prevent silent V2/V3 fallback from being counted as
   V4?
4. Are `spatial_rayjoin` and `barnes_hut` correctly treated as blocker/deferred
   rows instead of being hidden?
5. Do the tests sufficiently prove that planner dry-runs match current V4
   catalog behavior?
6. Does Goal4652 correctly preserve non-authorization for public release,
   app-level speed claims, CuPy blanket claims, arbitrary Numba callback claims,
   and app-specific kernels?
7. Can the project proceed to Goal4653 protocol freeze using this matrix as
   input?

## Requested Verdict Labels

- `accept_goal4652_complete_proceed_goal4653`
- `accept_with_required_amendments`
- `reject_goal4652_route_matrix_misleading`
- `blocked_missing_context`

## Non-Authorization

This review must not authorize public release, app-level performance claims, POD
all-app benchmark spend, broad V4 speed claims, CuPy blanket support, arbitrary
Numba callback support, C ABI, embedding, true-zero-copy, non-Python hosts, or
app-identity kernels.
