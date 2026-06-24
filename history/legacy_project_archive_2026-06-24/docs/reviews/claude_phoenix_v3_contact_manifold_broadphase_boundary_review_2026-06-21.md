# Claude Review - Phoenix V3 Contact Manifold Broadphase Boundary

Reviewer: Claude, via Claude CLI.

Date: 2026-06-21.

## Verdict

Approve as a rebuild boundary lesson, not M7.

The decision to hold `contact_manifold / generic_aabb_broadphase_collect_k` at
boundary-lesson status is correct. Three facts independently block promotion:

- wall ratio is `0.803x`, so OptiX is slower end to end;
- paired V2.14 rows are parity/regression (`1.004x` Embree, `0.989x` OptiX);
- the scope is broadphase candidate discovery and bounded rows, not a full
  contact solver.

## Findings

No hidden full-solver or physics overclaim was found.

Claude found one latent overclaim path: downstream tooling could index by
`app_id: contact_manifold` and extract only `query_optix_over_embree: 1.235`,
making the number look like a full contact-manifold claim. Claude recommended
adding a machine-readable query metric scope beside that ratio.

## Required Or Recommended Fixes

- Add a machine-readable `query_metric_scope` field to the candidate row.
- Add an explicit M7 blocker naming AABB index preparation as the fix target:
  `aabb_index_preparation_optix_4x_slower_fix_required_before_candidacy`.
- Add an explicit M7 blocker for untested overflow behavior:
  `overflow_path_larger_dataset_not_validated`.
- Extend tests so they assert the external-review blocker/closure, V2 parity or
  regression blocker, wall ratio `< 1.0`, and AABB prepare ratio `< 1.0`.

## Final Reading

The CPU-reference pass makes the lesson useful: the row produces a correct
witness set and passes the v2.4 phase contract. That does not overcome the wall
failure or full-solver scope boundary.
