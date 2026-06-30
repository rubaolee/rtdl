# Call For Review: Goal4816-D Correctness Preflight And Smoke Plan

Date: 2026-06-30

Review target:

`history/internal_docs/goal4816_D_rayjoin_correctness_preflight_smoke_plan_2026-06-30.md`

Prior gate:

`history/internal_docs/antigravity_goal4816_C_app_only_design_review_2026-06-30.md`

## Requested Verdict Labels

Use one of:

- `approve_goal4816_D_correctness_preflight_authorize_smoke_execution`;
- `approve_with_required_amendments_before_smoke_execution`;
- `block_goal4816_D_redo_preflight_plan`;
- `block_goal4816_line_due_to_environment_or_input_gap`.

## Review Questions

1. Does the plan correctly keep the executor in RTDL-user mode rather than RTDL
   developer mode?
2. Does it prevent runtime/native/release-surface modification?
3. Does it correctly avoid authorizing performance benchmarking?
4. Does it define environment checks strongly enough for Windows/local Linux/POD
   portability?
5. Does it correctly require route labels and prevent bundled-helper evidence
   from being reported as generic user-language reproduction?
6. Does the first smoke route correctly focus on bundled-helper correctness over
   available inputs without speedup claims?
7. Does the second smoke route correctly frame generic primitive + Numba as a
   gap probe rather than full overlay reproduction?
8. Are the artifact requirements sufficient for later external audit?
9. Are the exit labels honest and complete?
10. Should the next execution goal be authorized as a correctness smoke, or
    must Goal4816-D be amended first?

## Non-Authorization Boundaries

This review must not authorize:

- performance runs or speedup claims;
- RTDL runtime/native/source edits;
- full 8/8 reproduction claims;
- generic-language claims from bundled helper output;
- private helper use as public API.

## Expected Reviewer Output

Please provide:

- one verdict label;
- P0/P1/P2 findings;
- answers to the ten questions;
- explicit statement whether the next correctness-smoke execution goal is
  authorized;
- explicit non-authorization block.
