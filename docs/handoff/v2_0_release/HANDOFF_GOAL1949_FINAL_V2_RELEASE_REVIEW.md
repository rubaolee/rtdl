# Handoff: Goal1949 Final v2.0 Release Review

Please perform an independent final release review for RTDL v2.0.

## Context

RTDL v2.0 is the Python + partner + RTDL milestone. The release is intentionally
source-tree-only: users run from the repository with `PYTHONPATH=src:.`.
Package-install support remains out of scope.

The current readiness aggregator reports only two remaining blockers:

- final v2.0 release consensus missing;
- explicit user-requested release action missing.

This review is intended to close the first blocker if accepted. It must not
perform a release action or move tags.

## Primary Files To Read

- `docs/reports/goal1909_v2_release_packet_skeleton_2026-05-13.md`
- `docs/reports/goal1946_all_app_v2_perf_deep_dive_2026-05-13.md`
- `docs/reports/goal1947_v2_source_tree_only_policy_consensus_2026-05-13.md`
- `docs/reports/goal1948_user_owned_native_continuation_example_2026-05-13.md`
- `docs/partner_acceleration_boundaries.md`
- `README.md`

Useful gate outputs/reports:

- `scripts/goal1908_v2_local_preflight.py`
- `docs/reports/goal1905_v2_partner_pod_batch_acceptance.json`
- `docs/reports/goal1916_v2_post_pod_artifact_manifest.json`
- `docs/reports/goal1911_v2_readiness_aggregator.json`, if present; otherwise
  rerun `PYTHONPATH=src:. python scripts/goal1911_v2_readiness_aggregator.py`.

## Review Questions

1. Does the release packet correctly preserve the claim boundary?
   - Allowed: selected OptiX RTDL primitive contracts hand compact outputs to
     Torch/CuPy device tensors and show reviewed positive rows.
   - Blocked: broad RT-core speedup, whole-app acceleration, arbitrary
     PyTorch/CuPy acceleration, package-install support, and unconstrained
     true zero-copy.
2. Are the all-app classifications in Goal1946 fair?
   - Positive rows must stay exact to their measured contracts.
   - Control rows (`database_analytics`, `graph_analytics`,
     `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) must not be used
     as speedup claims.
3. Is the source-tree-only release policy in Goal1947 acceptable for v2.0?
4. Does Goal1948 correctly show interoperability with user-owned C/C++ without
   treating it as official v2 partner speedup evidence?
5. Is there any public-facing wording in README/docs that overclaims v2.0?
6. Final verdict: one of `accept`, `accept-with-boundary`,
   `needs-more-evidence`, or `reject`.

## Expected Output

Write a review file under `docs/reviews/`.

For Claude, write:

`docs/reviews/goal1949_claude_final_v2_release_review_2026-05-13.md`

For Gemini, write:

`docs/reviews/goal1950_gemini_final_v2_release_review_2026-05-13.md`

The review must state the reviewer identity, independence from Codex, exact
files read, tests or commands run, findings, and the final verdict.
