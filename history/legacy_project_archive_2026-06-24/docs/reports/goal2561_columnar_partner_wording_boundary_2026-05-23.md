# Goal2561: Columnar Partner Wording Boundary

Date: 2026-05-23

## Scope

Goal2551 consensus identified `src/rtdsl/columnar_partner.py` as carrying
benchmark-specific wording in a shared runtime contract, especially the phrase
`numeric RayDB-style columns only`. Goal2561 removes that wording from the
shared partner-resident columnar planning surface.

## Change

- Replaced `numeric RayDB-style columns only` with
  `numeric columnar aggregate columns only`.
- Replaced the `OptiX DB dataset` blocker wording with generic compatibility
  payload wording.
- Replaced `OptiX native DB path` in the claim boundary with
  `OptiX native columnar path`.

## Boundary

No behavior or native ABI changes are made. This is a shared-runtime wording
cleanup so the partner-resident columnar contract is not anchored to the
RayDB-style benchmark app.

## Validation

- Added `tests/goal2561_columnar_partner_wording_boundary_test.py`.
- The test checks both source text and runtime-returned requirements for the
  generic wording.

No pod was used. This is local contract wording cleanup.
