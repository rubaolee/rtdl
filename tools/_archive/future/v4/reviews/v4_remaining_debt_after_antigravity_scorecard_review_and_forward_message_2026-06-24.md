# V4 Remaining Debt After Antigravity Scorecard Review

Date: 2026-06-24

Status: `remaining_v4_debt_audited_and_categorized`

Primary new review consumed:

- `future/v4/reviews/antigravity_v4_goal4626_4632_scorecard_debt_review_2026-06-24.md`

Related intake:

- `future/v4/reviews/antigravity_v4_goal4626_4632_scorecard_debt_review_intake_2026-06-24.md`

## Bottom Line

Antigravity has now reviewed the 9 substantive Goal4626-4632 scorecard review-debt items and returned `close_debt` for all 9. This completes the resolution of the main scorecard review debt.

Additionally, Antigravity has performed a full pass over all older procedural and historical review debt files outside of the main scorecard set, marking them as either **closed by later scorecard goals** or **superseded**. 

This resolves **all historical review/procedure debt** (empty outputs, session limits, old blocked files). The remaining open items are now exclusively **engineering/release blockers** that must be solved before any formal high-performance V4 can be claimed.

The current valid V4 label remains:

- `development_state_performance_preview_not_release`

***

## A. Scorecard Review Debt Now Closed By Antigravity

These were the 9 open scorecard review debts. Antigravity has returned `close_debt` for all, and they are now officially resolved:

| ID | Debt | Antigravity Status | Resolution Reference |
|---|---|---|---|
| S1 | Goal4626 Antigravity amendment-check empty output | `close_debt` | Closed by Goal4626 amendments in protocol and tests. |
| S2 | Goal4627 Antigravity coverage-audit empty output | `close_debt` | Closed by Goal4627 1/5/1/3 split and candidate audit. |
| S3 | Goal4629 Antigravity amendment-check empty output | `close_debt` | Closed by Goal4629 future promotion requirements check. |
| S4 | Goal4630 Claude session limit | `close_debt` | Closed by Goal4630 pushdown recognizer minimal slice. |
| S5 | Goal4630 Antigravity empty output | `close_debt` | Closed by Goal4630 CuPy candidate fail-closed rules. |
| S6 | Goal4631 Claude session limit | `close_debt` | Closed by Goal4631 Tier-3 spike boundary decision. |
| S7 | Goal4631 Antigravity empty output | `close_debt` | Closed by Goal4631 Stage 1/Stage 2 link blocker verification. |
| S8 | Goal4632 Claude session limit | `close_debt` | Closed by Goal4632 final release preview confirmation. |
| S9 | Goal4632 Antigravity empty output | `close_debt` | Closed by Goal4632 final release preview confirmation. |

***

## B. Procedural / Historical Review Debt (Audited & Closed)

These older items are now officially marked closed or superseded, preventing historical file buildup from blocking current release evaluation.

### B1. Old Release-Candidate Tracker Debt

| File / Item | Antigravity Audit Status | Justification / Closure Reference |
|---|---|---|
| `future/v4/reviews/review_debt_v4_0_release_candidate_2026-06-24.md` <br> (D2 Antigravity non-interactive reviewer unavailable: `tool_unavailable`) | `superseded_by_goal4632_final_decision` | Superseded by the new comprehensive `antigravity_v4_goal4626_4632_scorecard_debt_review_2026-06-24.md` audit. |

### B2. Older Bounded Review-Debt Files

| File | Antigravity Audit Status | Justification / Closure Reference |
|---|---|---|
| `review_debt_v4_catalog_regression_gate_2026-06-24.md` | `closed_by_later_scorecard_goal` | Formally closed and tested by the push-down recognizer in Goal4630 and final release decision in Goal4632. |
| `review_debt_v4_operator_callback_planner_boundary_2026-06-24.md` | `closed_by_later_scorecard_goal` | Planner boundaries are formally implemented and enforced by the Goal4630 fail-closed logic. |
| `review_debt_v4_primitive_grouped_i64_candidate_2026-06-24.md` | `closed_by_later_scorecard_goal` | Grouped-i64 reduction was resolved and passed as the second same-contract gate in Goal4628. |
| `review_debt_v4_scope_gate_2026-06-24.md` | `closed_by_later_scorecard_goal` | Bounded scope gate is formally closed by the Goal4626 scorecard definition. |
| `review_debt_v4_second_tier2_closest_hit_grouped_argmin_2026-06-24.md` | `closed_by_later_scorecard_goal` | Closest-hit grouped argmin is now a measured surface in the active operator catalog (Goal4627/Goal4630). |
| `review_debt_v4_third_tier2_any_hit_flags_and_catalog_2026-06-24.md` | `closed_by_later_scorecard_goal` | Any-hit flags are now a measured surface in the active operator catalog (Goal4627/Goal4630). |
| `review_debt_v4_tier3_numba_ptx_probe_2026-06-24.md` | `closed_by_later_scorecard_goal` | Historical PTX compilation probe is superseded by Goal4631's Tier-3 spike execution decision. |
| `review_debt_v4_tier3_optix_module_link_probe_2026-06-24.md` | `closed_by_later_scorecard_goal` | Historical module linking probe is superseded by Goal4631's Tier-3 spike execution decision. |
| `review_debt_v4_unified_frontdoor_2026-06-24.md` | `closed_by_later_scorecard_goal` | Unified front door is closed and verified in Goal4630. |

### B3. Older Antigravity Blocked Files Before Goal4626

| File | Antigravity Audit Status | Justification / Closure Reference |
|---|---|---|
| `antigravity_v4_goal4620_weighted_sum_completion_review_blocked_2026-06-24.md` | `superseded_by_goal4632_final_decision` | Weighted-sum candidate status is resolved in Goal4629 and failed closed in Goal4630. |
| `antigravity_v4_goal4621_catalog_hardening_completion_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Catalog hardening was resolved by the Goal4627 operator catalog audit and Goal4630 pushdown recognizer. |
| `antigravity_v4_goal4622_tier3_callback_protocol_completion_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Tier-3 callback protocol is resolved by Goal4631 Tier-3 spike execution decision. |
| `antigravity_v4_goal4624_development_state_naming_cleanup_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Naming cleanup is formally completed and asserted in the Goal4632 release decision. |
| `antigravity_v4_goal4625_design_status_and_next_goals_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Superseded by the frozen release scorecard in Goal4626. |
| `antigravity_v4_goal4625_design_status_and_next_goals_amended_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Superseded by the frozen release scorecard in Goal4626. |
| `antigravity_v4_section8_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Resolved by Goal4626 section 8 evidence reconciliation and scorecard protocol. |
| `antigravity_v4_section8_device_array_frontdoor_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Resolved by Goal4626 section 8 evidence reconciliation and scorecard protocol. |
| `antigravity_v4_section8_route_d_handwritten_optix_ceiling_review_blocked_2026-06-24.md` | `closed_by_later_scorecard_goal` | Resolved by Goal4626 section 8 evidence reconciliation and scorecard protocol. |

***

## C. Remaining Engineering / Release Debt For Formal High-Performance V4

The following open items are the **exclusive remaining blockers** to a formal high-performance V4 release. They are engineering requirements that cannot be bypassed or waived.

### E1. Operator Coverage Is Limited
- **Current Evidence:** 10 promoted benchmark app families audited. Coverage split is `1 strong measured / 5 partial measured / 1 candidate / 3 deferred`.
- **Release Impact:** V4 cannot claim broad user value or catalog-wide high performance under this split.
- **Required Work:** Expand measured Tier-2 operator coverage, or explicitly declare V4 a bounded operator-only release.

### E2. Weighted-Sum Is Still Candidate
- **Current Evidence:** `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` remains candidate-only.
- **Release Impact:** The dominant path for `triangle_counting` is candidate-bound and unmeasured for release.
- **Required Work:** Run a predeclared weighted-sum promotion gate with expanded shapes, release-level repeats, and parity checks; or explicitly exclude it from release claims.

### E3. Tier-3 Is Not Supported
- **Current Evidence:** Bare Numba PTX failed `optixModuleCreate` with `No functions with semantic types found`. Tier-3 is spike-only/deferred.
- **Release Impact:** V4 cannot support custom user callbacks.
- **Required Work:** Build a real native OptiX module wrapper or direct-callable ABI to resolve linking; run correctness and overhead stages.

### E4. CuPy Performance Is Unmeasured
- **Current Evidence:** Torch CUDA is the only measured partner. CuPy requests fail closed.
- **Release Impact:** No CuPy performance claims are authorized.
- **Required Work:** Run CuPy partner validation gates, or restrict V4 release wording to Torch CUDA only.

### E5. No Whole-App / All-Benchmark Release Gate
- **Current Evidence:** No all-application benchmark gate validates workflow speedup.
- **Release Impact:** Broad speedup wording is not authorized; only isolated operator wins are proven.
- **Required Work:** Run end-to-end benchmarks comparing V4 device-array pipelines against matching baselines.

### E6. User-Facing Release Cleanup
- **Current Evidence:** Naming convention is cleaned up in tests, but user-facing docs must be finalized.
- **Release Impact:** Risk of user confusion between historical/candidate surfaces and measured features.
- **Required Work:** Update front page, docs, tutorials, and examples to match authorized wording and hide stale details.

### E7. Clean-Tree / Reproducibility Validation
- **Current Evidence:** Scorecard tests pass locally, but repo contains temporary artifacts.
- **Release Impact:** Lack of immutable release proof.
- **Required Work:** Run local and POD gates from a clean branch/worktree, producing a clean release package.

***

## D. Next Reviewer Instructions (For Reference)

For future release iterations, any newly discovered historical items should be classified into:

- `must_close_before_formal_release`
- `can_waive_for_bounded_operator_release`
- `superseded_by_goal4626_4632_scorecard`
- `not_required_for_v4_0_scope`

This ensures that development focus remains on the core engineering blockers (Section C) rather than administrative debt.
