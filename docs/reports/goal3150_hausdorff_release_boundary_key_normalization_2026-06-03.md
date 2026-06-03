# Goal3150: Hausdorff Release-Boundary Key Normalization

Date: 2026-06-03

Status: source and artifact key normalization complete; no computation changes.

## Purpose

The Goal3144 Claude review noted that the Goal3143 Hausdorff comparison artifact used `v2_8_release_authorized: false` on the new `partner_exact, partner="numba"` rows, while the legacy comparison rows only carried `v2_6_release_authorized: false`.

Both values were false, so there was no claim leak. The inconsistency was still worth fixing because machine checks should not need to special-case the legacy comparison backend.

## Changes

- Added `v2_8_release_authorized: false` to the legacy `partner_numba_witness_exact` and `partner_numba_block_nearest_exact` claim boundaries in the Hausdorff benchmark app.
- Preserved `v2_6_release_authorized: false` on those legacy paths for compatibility.
- Updated the Goal3143 artifact so every row carries `v2_8_release_authorized: false`.
- Added a future-version note that the adapter currently named `directed_hausdorff_2d_partner_columns` should eventually gain a generic alias such as `directed_max_of_nearest_distance_2d`, with `hausdorff` retained as a discovery alias.

## Boundary

This is not a performance or correctness change. It does not rerun hardware timing, alter kernels, change numerical behavior, or authorize release/speedup/RT-core/zero-copy claims.

The RTX pod was unavailable during this cleanup (`Connection refused` on the active SSH port), but no pod rerun is required for this key-only artifact normalization.
