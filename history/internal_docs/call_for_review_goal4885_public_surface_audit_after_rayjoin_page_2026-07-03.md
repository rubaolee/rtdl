# Call For Review: Goal4885 Public Surface Audit After RayJoin Page

Please review the Goal4885 public user-surface audit:

`history/internal_docs/goal4885_public_surface_audit_after_rayjoin_page_2026-07-03.md`

## Context

After adding `docs/release_reports/v2_14/rayjoin_section57_bounded_reproduction.md`,
the user required another strict pass over the reader-visible surface. The goal
was to ensure that README/docs/tutorials/examples remain clean, current, and
free of internal process leaks, V3/V4 experiment exposure, broken links, stale
goal paths, or confusing old evidence.

## What Changed

- Removed the explicit `exp-project-1/` row from the root README.
- Replaced a historical RTNN `goal2348` runner path with the current public
  benchmark entry point.
- Removed an internal artifact path from the prepared-execution teaching page.
- Removed direct `history/internal_docs` pointers from public benchmark docs and
  example metadata strings.
- Updated RayJoin app-author wording to the current bounded Section 5.7
  reproduction claim.
- Updated the RT-vs-Embree overlay performance row to link the bounded
  correctness page without broadening the performance claim.
- Updated primitive catalog source reference paths and regenerated
  `docs/rtdl_primitive_catalog.md`.
- Updated one maintenance test that still expected the old `docs/reports` path.

## Local Validation

- Strict public leak scan over `README.md docs tutorials examples`: no matches.
- Markdown relative-link check: `89` files checked, all links exist.
- Primitive catalog drift check: passed.
- Public/front-door tests: `17` tests passed.
- Source-tree doctor: core checks passed; optional native/partner warnings only.
- Hello world example: printed `hello, world`.

## Questions For Reviewer

1. Is the current public reader-visible surface free of internal process leaks
   such as goal IDs, AI reviewer names, internal review paths, V3/V4 references,
   and experimental-directory advertising?
2. Are the RayJoin Section 5.7 docs now consistent: bounded reproduction
   documented, no full hidden-input `8/8` claim, and no broad performance claim?
3. Are the examples/tutorial/docs links and current v2.14 navigation coherent
   enough for first-time users?
4. Was it correct to remove the explicit root README `exp-project-1/` entry
   while leaving the top-level history archive available?
5. Is the primitive catalog cleanup acceptable, given that source references now
   point to public feature/boundary docs and the generated catalog was checked?
6. Does the maintenance-test update preserve a legitimate gate rather than
   hiding a user-facing problem?
7. Should Goal4885 close with:
   `approve_goal4885_public_surface_audit_after_rayjoin_page`?

## Non-Authorization

This review must not authorize new V3/V4 release claims, broad RT-core speedup
claims, full hidden-input RayJoin Section 5.7 reproduction, package-install
claims, or any runtime/native change. It only reviews public surface cleanliness
after the bounded RayJoin page addition.
