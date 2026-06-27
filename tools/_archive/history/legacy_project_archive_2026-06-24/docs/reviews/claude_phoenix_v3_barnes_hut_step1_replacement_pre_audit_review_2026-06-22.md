# Claude Review: Phoenix V3 Barnes-Hut Step-1 Replacement Pre-Audit

Date: 2026-06-22
Reviewer: Claude
Status: recorded external review; non-authorizing

## Verdict

`conditional_go_for_implementation_with_required_amendments`

Pod remains not authorized.

## Review Summary

Claude agreed that implementation is the correct next action and pod should not be run yet. Running pod before productized-runtime wiring would measure the existing app-front-door route, not the runtime trunk.

Claude also agreed that the dual comparison design is structurally correct:

- parity control versus the existing app-front-door fused Numba CUDA partner;
- reference comparison versus the old prepared OptiX/frontier route.

Required amendment: do not call the old prepared OptiX/frontier route the primary material baseline. It is a historical no-go reference / predecessor displacement evidence. The parity control is the primary validation gate.

## Required Amendments

1. Step 1 completion must be explicit. Since RTDBSCAN and RayJoin were structural-only, Barnes-Hut is not Step 2 generalization; it is a Step 1 replacement material-probe candidate.
2. Add a parity-failure threshold and consequence. If runner-wrapped fused partner is more than 5% slower than existing app-front-door fused partner on any serious size, the pod packet is no-go for claim use.
3. Confirm the M7 row amendments from the earlier Barnes-Hut fused-partner review are incorporated.
4. Confirm Barnes-Hut is in the frozen Set-A classification before any focused run.

These amendments were incorporated into `docs/rebuild/v3/phoenix_v3_barnes_hut_step2_pre_audit_2026-06-22.md` and `.json`.

## Non-Authorization

This review authorizes no release, no public speedup wording, no broad V3-over-V2 wording, no all-app run, no RT-core wording, no true-zero-copy wording, and no pod A/B before productized-runner wiring exists.
