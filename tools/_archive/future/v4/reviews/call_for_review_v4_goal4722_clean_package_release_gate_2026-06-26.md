# Call For Review: V4 Goal4722 Clean Package Release Gate

Date: 2026-06-26

Requested verdict labels:

- `accept_goal4722_package_gate_passed`
- `accept_with_required_amendments`
- `reject_packaging_or_public_docs_gate`
- `reject_overclaim_or_missing_release_blocker`

## Review Target

Please review:

- `future/v4/v4_goal4722_clean_package_release_gate_2026-06-26.md`

Supporting evidence:

- `future/v4/v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`
- `future/v4/evidence/v4_goal4720_catalog_regression_gate_dry_run_2026-06-26.json`
- `dist/goal4722_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`

## Questions

1. Is Goal4722 acceptable as a local release-packaging gate for the current V4
   release candidate?
2. Is the `ensurepip` repair and `pip wheel --no-deps` build path acceptable for
   this source-tree release candidate?
3. Are current public docs/examples clean enough, given that old 8-surface text
   remains only in historical goal/review/design artifacts?
4. Does Goal4722 correctly preserve `formal_release_authorized: false` while
   moving the package gate forward?
5. What exact blocker remains before final public tag?

## Non-Authorization

This review must not authorize broad V4 speedup wording, whole-application
speedups, all-benchmark speedups, public true-zero-copy claims, arbitrary
callback support, raw OptiX callbacks, blanket CuPy performance claims, C ABI,
embedding, non-Python host binding claims, app-specific native kernels, or a
final public tag unless the reviewer explicitly says the 3-AI final release
rule is satisfied.
