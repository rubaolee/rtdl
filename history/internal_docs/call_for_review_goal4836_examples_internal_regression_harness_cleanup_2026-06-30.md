# Call For Review — Goal4836 Examples-Internal Regression Harness Cleanup

Date: 2026-06-30

Please review:

- `history/internal_docs/goal4836_examples_internal_regression_harness_cleanup_2026-06-30.md`

## Requested Verdict Label

One of:

- `approve_goal4836_cleanup_and_continue_rayjoin_optix_line`
- `approve_with_required_amendments`
- `block_goal4836_public_surface_or_regression_issue`

## Questions For Reviewer

1. Did Goal4836 correctly preserve the clean user-facing public surface by keeping archived/internal examples under `history/examples_internal` rather than restoring `examples/internal`?
2. Are the import/path changes properly limited to tests, maintainer scripts, and archived examples?
3. Is the zero-match scan for `examples.internal` / `examples/internal` sufficient evidence that this specific stale-path issue is closed?
4. Do the targeted migration tests support closing the stale examples-internal regression harness issue?
5. Does the RayJoin focused gate (`38 tests OK`) show that the cleanup did not regress the current RayJoin correctness line?
6. Is it correct to keep Windows Embree linker failures as separate toolchain debt, outside the current no-Embree RayJoin reproduction line?
7. Should the next work continue with Linux/OptiX RayJoin confirmation and County x Zipcode mismatch analysis rather than more public-surface churn?

## Non-Authorization

Approval of this review must not authorize:

- full RayJoin Section 5.7 reproduction claims;
- broad v2.14 performance claims;
- Embree evidence in the current RayJoin line;
- public documentation changes;
- V3/V4 resurrection;
- any release tag or push.
