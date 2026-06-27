# V4 Goal4727 Contact Manifold No-Go Row

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `contact_manifold_closed_as_no_go_rebranded_collect_k_not_v4_speed_evidence`

## Purpose

Goal4727 closes `contact_manifold` for the current V4 high-performance path.
This is a design-gate no-go, not a failed tuning run.

Machine-readable row:

- `future/v4/evidence/v4_goal4727_contact_manifold_no_go_row_2026-06-26.json`

## Evidence

Source audit:

- `future/v4/evidence/v4_goal4683_contact_witness_design_audit_2026-06-25.json`
- `future/v4/v4_goal4683_contact_witness_design_audit_2026-06-25.md`

The audited target was:

```text
AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D
```

Goal4683 killed it because V2.14 already contains bounded collect-k primitives,
and the current tree already contains exact-witness partner-column surfaces.

## Why No-Go

V4 needs a new generic runtime lever or a material same-primitive improvement
over V2.14. The proposed contact/witness path provides neither:

- the bounded collection core is V2.14 work;
- exact-witness device-column continuation is current partner adapter work;
- a contact-specific fused witness kernel would violate the app-identity-kernel
  lock.

Therefore the row is closed as:

```text
closed_no_go_for_current_high_performance_path
```

## Reopen Condition

Only reopen this row if a new app-name-free bounded-witness primitive is defined
with frozen bars, or if a material same-primitive V2.14-vs-V4 improvement
hypothesis exists before POD.

## Next

Proceed to Goal4728: `spatial_rayjoin` relation-topology route or no-route
blocker.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4727_contact_manifold_no_go_row_test tests.v4_goal4683_contact_witness_design_audit_test tests.v4_goal4724_remaining_app_route_gap_audit_test`

## Goal-Level Decision Audit

1. Was I being stupid?
   No. This goal avoids implementing or benchmarking a target already shown to
   be rebranded V2.14/current work.

2. If yes, what action made the decision stupid?
   Not applicable. The stupid action would be treating collect-k plus witness
   plumbing as a new V4 speed lever.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Record the no-go row and reopen only if a fresh generic primitive or
   material same-primitive improvement is defined before POD.

4. Can I now try the different path that actually solves the problem?
   Yes. Move to `spatial_rayjoin`, which currently has no V4 relation-topology
   route.

## Non-Authorization

Goal4727 authorizes no implementation, no POD spend, no final V4 tag, no public
speed claim, no contact-manifold speedup claim, no whole-app high-performance
claim, no broad V4-over-V2.14 claim, no partner-migration speed credit, no
app-specific native kernel, no arbitrary callback support, and no hidden V2/V3
fallback.
