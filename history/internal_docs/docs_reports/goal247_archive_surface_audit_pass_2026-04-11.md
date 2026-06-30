# Goal 247 Report: Archive Surface Audit Pass

Date: 2026-04-11
Status: implemented

## Summary

This goal seeds the archive tier with a representative pass instead of trying
to audit all remaining historical files as if they were live product surface.

The archive tier needed a different standard from the live tiers:

- preserved historical drafts should be safe and clearly archival
- internal handoffs can remain historical, but should be classified honestly
- high-value release-adjacent reports should be distinguished from low-value
  stale workspace glue

## Direct Outcome

Low-risk cleanup was applied to the six preserved wiki draft files so they no
longer leak broken absolute paths into the visible archive layer.

The remaining selected archive files were recorded with mixed outcomes:

- `preserved_archive`
- `release_adjacent_archive`
- `stale_but_acceptable`

and, where appropriate:

- `quality_status = follow_up_needed`
- `link_status = follow_up_needed`

## Why This Matters

Without this pass, the system-audit DB would overstate confidence by covering
only live product layers while ignoring the long-tail archive where stale paths
and historical assumptions accumulate.

With this pass, the DB can now distinguish:

- live reviewed surface
- reviewed but archival surface
- archive files that still deserve selective cleanup
