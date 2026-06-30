# External Review Request: Goals4205-4212 RT-DBSCAN Policy Canonicalization

Date: 2026-06-09

Please perform an independent read-only review of the Goal4205-4212 chain.

## Context

The recent RT-DBSCAN/fixed-radius work moved from "two-pass is safer but slow"
to a cleaner evidence-backed default:

- Goal4205 broadened one-pass reference parity across 4 seeds x 4 fixtures.
- Goal4206 added an adversarial root-shadow fixture requested by Gemini.
- Goal4207/4208 fixed and pod-confirmed all-core boundary-policy metadata.
- Goal4209/4210 introduced and pod-confirmed the canonical policy name
  `single_pass_candidate_root_rebased`.
- Goal4211/4212 made that canonical policy the no-argument default and
  pod-confirmed it.

The old name `lowest_candidate_then_root` remains accepted as a compatibility
alias.

## Files To Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `docs/reports/goal4205_rt_dbscan_single_pass_multi_seed_parity_2026-06-09.md`
- `docs/reports/goal4206_rt_dbscan_root_shadow_parity_2026-06-09.md`
- `docs/reports/goal4208_all_core_boundary_policy_metadata_pod_confirmation_2026-06-09.md`
- `docs/reports/goal4210_boundary_policy_canonical_alias_pod_confirmation_2026-06-09.md`
- `docs/reports/goal4211_boundary_policy_default_canonicalization_2026-06-09.md`
- `docs/reports/goal4212_boundary_policy_default_canonical_pod_confirmation_2026-06-09.md`
- `tests/goal4211_boundary_policy_default_canonicalization_test.py`
- `tests/goal4212_boundary_policy_default_canonical_pod_confirmation_test.py`

## Questions

1. Does the evidence justify making `single_pass_candidate_root_rebased` the
   default policy name while preserving `lowest_candidate_then_root` as an alias?
2. Did the change avoid route promotion and release/speedup/zero-copy overclaim?
3. Is the metadata/API compatibility story clean enough for users and reviewers?
4. Are there remaining blockers before this policy can be called the recommended
   RT-DBSCAN fixed-radius component boundary policy?

## Expected Output

Write one of:

- `docs/reviews/goal4213_claude_review_goal4205_4212_rtdbscan_policy_canonicalization_2026-06-09.md`
- `docs/reviews/goal4214_gemini_review_goal4205_4212_rtdbscan_policy_canonicalization_2026-06-09.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

Do not mutate source code. Running focused tests is allowed.
