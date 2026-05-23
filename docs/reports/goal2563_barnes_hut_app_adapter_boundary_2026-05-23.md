# Goal2563: Barnes-Hut App Adapter Boundary

Date: 2026-05-23

## Scope

The Barnes-Hut benchmark introduced an exact pairwise inverse-square force
partner reference. That code is useful for the app, but it is a domain-specific
composition, not a generic RTDL engine primitive. Goal2563 moves it out of the
shared partner adapter module.

## Change

- Added `src/rtdsl/app_adapters/barnes_hut.py`.
- Moved `pairwise_inverse_square_force_2d_partner_columns` and its CuPy kernel
  cache into that app-adapter module.
- Removed the pairwise inverse-square force adapter from
  `src/rtdsl/partner_adapters.py`.
- Kept `weighted_point_rows_to_partner_columns` in shared partner adapters
  because it is a generic column-conversion helper.
- Kept the top-level `rtdsl` export intact by importing the moved function from
  `rtdsl.app_adapters`.

## Boundary

The pairwise inverse-square force adapter moved out of shared partner adapters.
It remains available as a top-level `rtdsl` compatibility export for existing
app code, but direct shared-module imports are intentionally not preserved.

No native engine or ABI changes are made.

## Validation

- Updated `tests/goal1979_exact_pairwise_force_partner_barnes_hut_reference_test.py`.
- Added `tests/goal2563_barnes_hut_app_adapter_boundary_test.py`.
- The tests verify the moved location, absence from shared partner adapters,
  and preserved top-level `rtdsl` export.

No pod was used. This is local Python module-boundary cleanup.
