# Call For Review: Goal4875 Section 5.7 Australia Representative Public-Primitives Closure

Date: 2026-07-02

Requested reviewer: Antigravity now; Claude later if available.

Please review the Goal4875 closure packet:

- `history/internal_docs/goal4875_section57_au_representative_public_primitive_closure_2026-07-02.md`
- `history/internal_docs/goal4875_section57_au_representative_status_2026-07-02.md`
- implementation script: `history/internal_docs/goal4875_public_primitives_au_overlay.py`
- relevant product formatting change: `src/rtdsl/rayjoin_overlay.py`
- focused tests:
  - `tests.goal4834_rayjoin_sos_synthetic_contract_test`
  - `tests.goal4373_rayjoin_cdb_point_location_route_test`
  - `tests.goal4857_planar_map_point_location_public_front_door_test`
  - `tests.goal4866_rayjoin_section57_output_contract_test`

## Requested Verdict Labels

Choose one:

- `approve_goal4875_bounded_representative_section57_public_primitives_closed`
- `approve_with_required_amendments`
- `block_goal4875_closure`

## What Must Be Checked

1. Does the evidence support byte-for-byte equality between the public RTDL route
   and `Author+RTDLContractPatch` on the Australia current-OSM representative?
2. Is it correct to treat unpatched AuthorPatch as the wrong comparator after
   the duplicate-half-edge contract was made explicit?
3. Does the small-case evidence justify the diagnosis that the earlier mismatch
   was duplicate-half-edge contract mismatch, not an LSI/PIP route failure?
4. Is removing the obsolete positive half-boundary display-coordinate nudge a
   valid formatting-contract repair rather than a hidden geometry change?
5. Does the public route avoid importing `rtdsl.rayjoin_overlay` and instead use
   public RTDL LSI/PIP primitives plus application-level assembly?
6. Are the boundaries clear: representative current-OSM pair only, not exact
   eight-pair Section 5.7, not broad performance, no Embree, and Numba not on
   the correctness-critical path?
7. Are the focused local tests sufficient for this bounded closure, or is an
   additional test required before accepting the closure?
8. Is there any overclaim, hidden RayJoin-specific core shortcut, or evidence
   gap that should block closure?

## Expected Output

Please write the review to:

`history/internal_docs/antigravity_goal4875_section57_au_representative_public_primitives_closure_review_2026-07-02.md`

Include a verdict label, findings, answers to the eight questions, and any
required amendments.
