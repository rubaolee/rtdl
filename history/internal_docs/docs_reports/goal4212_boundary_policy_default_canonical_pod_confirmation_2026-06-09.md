# Goal4212: Boundary Policy Default Canonical Pod Confirmation

Date: 2026-06-09

## Purpose

Goal4211 changed the user-facing default boundary policy to
`single_pass_candidate_root_rebased`. Goal4212 confirms that a no-policy-argument
OptiX+Numba prepared run uses the canonical default on RTX hardware.

## Pod Result

Artifact:

`docs/reports/goal4212_boundary_policy_default_canonical_pod_rtx4000ada/default_canonical_smoke.json`

The smoke ran at commit `7eea73ca` and confirmed:

- plan policy: `single_pass_candidate_root_rebased`;
- plan canonical policy: `single_pass_candidate_root_rebased`;
- runtime metadata policy: `single_pass_candidate_root_rebased`;
- runtime metadata canonical policy: `single_pass_candidate_root_rebased`;
- native metadata policy: `single_pass_candidate_root_rebased`;
- native metadata canonical policy: `single_pass_candidate_root_rebased`;
- native pass count: `1`;
- labels: `[1, 1, 1, 1, 1]`;
- speedup and true-zero-copy claim flags remain false.

## Boundary

This confirms the default naming behavior only. It does not authorize release,
route promotion, public speedup claims, broad RT-core claims, true-zero-copy
claims, automatic partner selection, or app-specific native engine logic.
