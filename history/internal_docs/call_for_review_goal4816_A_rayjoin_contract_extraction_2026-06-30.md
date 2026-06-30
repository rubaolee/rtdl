# Call For Review: Goal4816-A RayJoin Section 5.7 Contract Extraction

Date: 2026-06-30

Review target:

`history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md`

## Requested Verdict Labels

Use one of:

- `approve_goal4816_A_contract_extraction_authorize_4816_B`;
- `approve_with_required_amendments_before_4816_B`;
- `block_goal4816_A_redo_contract_extraction`;
- `block_goal4816_line_due_to_unrecoverable_source_or_semantics_gap`.

## What To Review

Please critically verify whether Goal4816-A has correctly extracted the
RayJoin Section 5.7 reproduction contract before any implementation begins.

The review should not authorize implementation beyond Goal4816-B. Goal4816-B is
only the existing v2.14 asset/capability classification step.

## Specific Questions

1. Does the note correctly distinguish full Section 5.7 polygon overlay from
   scalar LSI/PIP or candidate-stage continuation rows?
2. Does it correctly record the author source commit and the fact that source
   semantics must be read via `git show HEAD:<file>` because the POD worktree is
   dirty?
3. Does it correctly extract the LSI contract: query segment as RT ray over
   `[0, 1]`, exact predicate after RT candidate generation, and pair output for
   later overlay construction?
4. Does it correctly extract the PIP/point-location contract: vertical ray,
   closest boundary edge, face-id derivation, and query-map-dependent SoS?
5. Does it correctly incorporate the user-provided author-reply determinism
   summary: equal-height candidates, OptiX strict `t < tmax` pruning, and the
   need to encode SoS tie-break into reported `t`?
6. Does it correctly flag the tension that author `HEAD:rt_pip_custom.cu` has
   internal slope tie-break logic but still reports unperturbed `t`, while the
   author-reply summary requires `t_reported` perturbation for determinism?
7. Does it correctly preserve Goal4380 as bounded 2/8 available-input evidence,
   not full 8/8 Section 5.7 reproduction?
8. Does it correctly separate `bundled_rayjoin_helper` from
   `existing_v2_14_primitive`, so future work cannot treat bundled RayJoin code
   as generic user-language capability?
9. Is the proposed Goal4816-B taxonomy complete enough to prevent hidden
   runtime edits, bundled-helper laundering, scalar-only overclaiming, and
   missing-input overclaiming?
10. Should Goal4816-B be authorized as the next step, or must Goal4816-A be
    amended first?

## Non-Authorization Boundaries

This review must not authorize:

- modifying `src/rtdsl/**`, `src/native/**`, or the v2.14 release surface;
- adding a RayJoin-specific RTDL runtime primitive;
- running POD performance experiments;
- presenting bundled-helper output as generic RTDL language reproduction;
- presenting scalar LSI/PIP or Numba candidate rows as full polygon overlay;
- claiming full 8/8 Section 5.7 reproduction from the current 2/8 evidence.

## Expected Reviewer Output

Please provide:

- one verdict label;
- P0/P1/P2 findings, if any;
- answers to the ten specific questions;
- explicit statement whether Goal4816-B is authorized;
- explicit non-authorization block.
