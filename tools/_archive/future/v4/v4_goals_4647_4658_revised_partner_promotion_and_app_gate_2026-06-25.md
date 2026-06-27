# V4 Goals 4647-4658 Revised: Partner Promotion And App-Level Gate

Date: 2026-06-25
Status: revised execution proposal, pending external review before execution
Supersedes:
`future/v4/v4_goals_4647_4658_partner_promotion_and_all_app_gate_for_claude_review_2026-06-25.md`
Required-amendment source:
`future/v4/v4_goals_4647_4658_claude_amendments_and_final_recheck_2026-06-25.md`
Claude review:
`docs/reviews/claude_v4_goals_4647_4658_review_2026-06-25.md`

## Expected Outcome Stated Up Front

The expected honest outcome of this chain is:

```text
bounded_operator_v4_only + partner unification
```

That is not failure. V2.14 already had strong CuPy and Numba partner routes. If
V4 moves those known-good routes behind a cleaner V4 front door, the product is
better, but the app is not automatically faster than V2.14. Formal
high-performance V4 requires new V4 runtime/operator wins against the proper
V2.14/V3 denominator, not partner migration or partner parity.

## Binding Integrity Locks

- Partner migration is not a V4 speed win.
- Partner parity is not a V4 speed win.
- `formal_high_performance_v4_supported` cannot be triggered by
  `partner_migration` or `partner_parity` rows.
- Bars must be class-aware:
  - fused-operator-addressable rows get speedup bars;
  - backend-bound rows get parity-with-explanation bars;
  - partner-migration/parity rows get parity and front-door certification bars;
  - no-route rows become blockers, not hidden exclusions.
- Route binding / blocker declaration must happen before app-level protocol
  freeze.
- "Material speedup" must be numeric and frozen before measurement.
- CuPy claims require V4-certified CuPy surfaces.
- Numba claims require fixed certified continuations; arbitrary callbacks stay
  Tier-3 spike-only.
- Every goal completion requires 3-AI consensus, or a recorded review-debt entry
  if a reviewer is unavailable and the owner allows debt.

## Goal4647 - V2.14 Partner Inventory With V4 Boundary Ledger

Purpose:

Create the one-page boundary ledger Claude requested while inventorying V2.14
CuPy/Numba partner assets. This merges the old truth-freeze idea into useful
inventory work and avoids process-only churn.

Tasks:

- Record current V4 truth in one ledger section:
  - V4.0.0 is a bounded operator release;
  - eight measured generic Tier-2 surfaces;
  - Torch CUDA is the main measured device-array partner;
  - one Numba-scoped component-union surface;
  - one RTDL-native AABB surface;
  - no CuPy V4 performance claim;
  - no broad app-level V4 speed claim.
- Inventory V2.14/V3 historical CuPy and Numba assets from reports, handoffs,
  scripts, tests, and evidence directories.
- For every candidate, record:
  - route name;
  - benchmark family/app;
  - partner;
  - input/output contract;
  - ratio and denominator;
  - scale;
  - raw artifact path;
  - generic operator fit;
  - V4 promotion status.
- Classify each row as:
  - `promotion_candidate_strong`;
  - `promotion_candidate_needs_rerun`;
  - `historical_only`;
  - `rejected_or_no_go`.

Exit evidence:

- `future/v4/v4_goal4647_v2_14_partner_inventory_boundary_ledger_2026-06-25.md`
- `future/v4/evidence/v4_goal4647_partner_inventory_2026-06-25.json`
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No benchmarks.
- No claim expansion.
- No use of partner migration as V4 speed evidence.
- No rewriting V2.14 success as if V4 invented it.

## Goal4648 - V4 Partner Promotion Contract With Numeric Bars

Purpose:

Define the contract and numeric pre-run bars for CuPy and fixed Numba promotion.

Tasks:

- Define the CuPy device-array front-door contract:
  - accepted dtypes and contiguous layouts;
  - CUDA device ownership;
  - stream/synchronization assumptions;
  - output allocation/ownership;
  - no-host-hot-path telemetry;
  - correctness parity.
- Define the fixed Numba continuation contract:
  - fixed operators only;
  - no arbitrary user callback support;
  - accepted signatures;
  - compile/cache timing boundaries;
  - correctness parity.
- Freeze numeric bars before runs:
  - CuPy certification: correctness `100%`; no host materialization in hot path
    for certified surfaces; per-surface representative speedup floor written
    before the run, default floor `>= 1.20x` unless a stricter row-specific
    floor is justified before measurement.
  - Fixed Numba certification: correctness `100%`; fixed-continuation only;
    per-surface representative speedup floor written before the run, default
    floor `>= 1.20x` unless a stricter row-specific floor is justified before
    measurement.
  - Partner parity rows: floor `>= 0.98x` against same-contract historical or
    current partner denominator, plus explanation.
- Define fail-closed planner/catalog behavior for unsupported partners.

Exit evidence:

- `future/v4/v4_goal4648_partner_promotion_contract_numeric_bars_2026-06-25.md`
- Contract tests for planner/catalog status.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No "material speedup" without a number.
- No CuPy performance claim.
- No arbitrary Numba callback claim.

## Goal4649 - CuPy Front-Door Certification Gate

Purpose:

Promote specific CuPy surfaces from historical strong partner evidence into V4
certified front-door support.

Tasks:

- Select surfaces from Goal4647 that are generic, not app-identity kernels.
- Run CuPy input/output arrays through the V4 front door.
- Verify:
  - correctness parity;
  - no Python row/object hot-path materialization;
  - raw JSON/log artifacts;
  - command, hardware, denominator, scale;
  - pre-frozen numeric bars from Goal4648.
- Update the catalog only for surfaces that pass.

Exit evidence:

- `future/v4/v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md`
- POD evidence directory with raw JSON/logs.
- Passing tests for certified CuPy catalog rows.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No blanket "CuPy supported" claim.
- No reuse of V2.14 ratios without V4 rerun.
- No partner migration row supporting V4-vs-V2.14 speed claims.

## Goal4650 - Fixed Numba Continuation Certification Gate

Purpose:

Promote fixed Numba-backed continuation operators into V4 while keeping
arbitrary callback support blocked.

Tasks:

- Select generic fixed continuation surfaces from Goal4647.
- Certify each against Goal4648 numeric bars.
- Keep categories separate:
  - fixed continuation operator;
  - partner migration/parity;
  - Tier-3 Numba->PTX->OptiX spike;
  - arbitrary callback unsupported.
- Record compile/cache timing if relevant.

Exit evidence:

- `future/v4/v4_goal4650_fixed_numba_continuation_certification_gate_2026-06-25.md`
- POD evidence directory with raw JSON/logs.
- Passing tests for certified fixed Numba catalog rows.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No arbitrary Numba callback support claim.
- No app-specific Numba route promotion unless made generic.
- No partner migration row supporting V4-vs-V2.14 speed claims.

## Goal4651 - Partner Catalog Promotion And Regression Gate

Purpose:

Update the V4 catalog/planner after CuPy and fixed Numba certification, and
protect it from drift.

Tasks:

- Update `measured_operator_catalog_v4()`.
- Update `plan_operator_request_v4()` and pushdown recognizer behavior.
- Ensure:
  - measured partners match raw evidence;
  - unmeasured partners fail closed;
  - baseline denominators and scales are recorded;
  - no broad speedup wording appears;
  - no app-identity kernels appear.
- Run local catalog regression tests and GPU regression tests where required.

Exit evidence:

- `future/v4/v4_goal4651_partner_catalog_promotion_regression_gate_2026-06-25.md`
- Updated catalog evidence.
- Test output summary.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No catalog row without raw evidence.
- No stale `declared_unmeasured` wording after certification.
- No broad app-level claim.

## Goal4652 - App Route Binding Or Blocker Declaration

Purpose:

Bind every benchmark app to a real V4 route or declare a blocker before freezing
the app-level benchmark protocol.

Apps:

- `rt_dbscan`
- `raydb_style`
- `triangle_counting`
- `librts_spatial_index`
- `hausdorff_xhd`
- `robot_collision`
- `contact_manifold`
- `rtnn`
- `spatial_rayjoin`
- `barnes_hut`

Tasks:

- For each app, assign one of:
  - `v4_fused_operator_addressable`;
  - `partner_migration_or_parity`;
  - `backend_bound_parity_control`;
  - `requires_new_generic_operator`;
  - `requires_cupy_promotion`;
  - `requires_fixed_numba_continuation`;
  - `no_v4_app_route_blocker`;
  - `deferred_excluded_with_reason`.
- Record whether the route actually uses V4 code.
- Dry-run all route bindings where possible.

Exit evidence:

- `future/v4/v4_goal4652_app_route_binding_or_blocker_declaration_2026-06-25.md`
- JSON route-binding matrix.
- Dry-run/test output.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No silent fallback to V2/V3 while calling it V4.
- No app-specific kernel to rescue a single app.
- No app skipped without a blocker label.

## Goal4653 - Full App-Level Protocol Freeze

Purpose:

Freeze the all-app V2.14/V3/V4 benchmark protocol after route binding is known.

Tasks:

- Use Goal4652's route-binding matrix as input.
- For each app, freeze:
  - V2.14 route;
  - V3 route;
  - V4 route or blocker;
  - correctness contract;
  - dataset scale;
  - warmup/repeat;
  - metric windows;
  - denominator;
  - class-aware pass/fail bar.
- Freeze class-aware bars:
  - fused-operator-addressable rows: pre-declared speedup floors;
  - backend-bound rows: parity floor `>= 0.98x` plus explanation;
  - partner-migration/parity rows: parity floor `>= 0.98x`; no formal
    high-performance contribution;
  - no-route blockers: counted as blockers, not hidden.
- Request external review before POD spend.

Exit evidence:

- `future/v4/v4_goal4653_full_app_level_protocol_freeze_2026-06-25.md`
- JSON protocol.
- Claude/Antigravity/third-seat review or explicit review debt if unavailable.

Forbidden:

- No app-level benchmark before protocol review/debt record.
- No post-hoc app exclusion.
- No naive whole-suite geomean as the release trigger.

## Goal4654 - Serious Full App-Level POD Benchmark

Purpose:

Run the frozen same-hardware V2.14/V3/V4 benchmark suite.

Tasks:

- Run exactly the Goal4653 protocol.
- Record hardware, driver, CUDA, OptiX, commit, environment.
- For each app record:
  - V2.14 wall time;
  - V3 wall time;
  - V4 wall time;
  - hot phase/operator timing;
  - correctness parity;
  - route metadata;
  - raw JSON/logs.

Exit evidence:

- `future/v4/v4_goal4654_full_app_level_v2_14_v3_v4_pod_benchmark_2026-06-25.md`
- Raw evidence directory.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No partial public claim.
- No rerun-only-the-winners behavior.
- No protocol changes after seeing results.

## Goal4655 - Benchmark Analysis With Partner-Migration Lock

Purpose:

Interpret Goal4654 without overclaiming.

Tasks:

- Produce app table:
  - V4/V2.14;
  - V4/V3;
  - V3/V2.14;
  - correctness;
  - route source;
  - blocker status;
  - claim class.
- Classify every row:
  - `true_v4_operator_win`;
  - `partner_migration`;
  - `partner_parity`;
  - `algorithmic_complexity_win`;
  - `backend_bound_parity`;
  - `regression`;
  - `no_route_blocker`.
- Enforce AM1:
  - `partner_migration` and `partner_parity` cannot contribute to
    `formal_high_performance_v4_supported`.
- Produce decision:
  - `formal_high_performance_v4_supported`;
  - `bounded_operator_v4_only`;
  - `v4_partner_promotion_needed`;
  - `v4_no_go_reframe_required`.

Exit evidence:

- `future/v4/v4_goal4655_full_app_level_benchmark_analysis_2026-06-25.md`
- JSON scorecard.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No broad claim if only partner migration/parity moved.
- No hiding blockers.
- No treating tiny V4/V3 noise as meaningful.

## Goal4656 - User Docs And Tutorial Rewrite Based On Measured Truth

Purpose:

Make the user-facing V4 surface match the measured truth from Goal4655.

Tasks:

- If Goal4655 supports formal high-performance V4, write exact bounded
  high-performance wording.
- If Goal4655 lands on bounded operator V4 + partner unification, keep the
  public story there and do not treat it as failure.
- Update:
  - README/front page;
  - `docs/current_v4_status.md`;
  - `future/v4/README.md`;
  - tutorials;
  - examples;
  - performance wording.
- Verify public examples run or dry-run as documented.

Exit evidence:

- `future/v4/v4_goal4656_docs_and_tutorial_rewrite_based_on_truth_2026-06-25.md`
- Example/test output summary.
- 3-AI completion consensus or recorded review debt.

Forbidden:

- No marketing wording beyond Goal4655.
- No deep-history references in the user quickstart.
- No stale CuPy/Numba claims.

## Goal4657 - Final 3-AI Release Or Reframe Authorization

Purpose:

Obtain final external authorization for what V4 honestly is after Goals4647-4656.

Tasks:

- Send the complete packet to Claude, Antigravity, and a third AI seat or record
  review debt if an allowed reviewer is unavailable.
- Ask reviewers to choose:
  - `formal_high_performance_v4_release_authorized`;
  - `bounded_operator_v4_release_only`;
  - `partner_promotion_continuation_required`;
  - `no_go_reframe_required`.
- Record explicit authorization and non-authorization.

Exit evidence:

- `future/v4/reviews/goal4657_final_v4_release_or_reframe_authorization_2026-06-25.md`
- Final decision file.
- 3-AI consensus record.

Forbidden:

- No final release/tag wording without 3-AI authorization.
- No ambiguity about what was released.

## Goal4658 - Final Recheck, Guardrails, And Completion Audit

Purpose:

Before marking V4 complete, prove the final state satisfies the full objective
and cannot drift into overclaim wording.

Tasks:

- Reopen:
  `future/v4/v4_goals_4647_4658_claude_amendments_and_final_recheck_2026-06-25.md`
- Reopen the current agent refresh/runbook:
  `future/v4/V4_CURRENT_AGENT_REFRESH_RUNBOOK_2026-06-25.md`
- Answer every final recheck item.
- Run wording/search guards for:
  - broad V4 speed claims;
  - app-level claims;
  - CuPy claims;
  - arbitrary Numba callback claims;
  - C ABI/embedding claims;
  - app-identity kernel claims.
- Run relevant test/regression gates.
- Produce a final requirement-by-requirement completion audit.

Exit evidence:

- `future/v4/v4_goal4658_final_recheck_guardrails_completion_audit_2026-06-25.md`
- Test/search output summary.
- 3-AI completion consensus.
- Goal can be marked complete only if every item is proven.

Forbidden:

- No completion claim on indirect or weak evidence.
- No ignoring review debt.
- No final answer that redefines success around a smaller goal.

## Review Request For Revised Chain

Please review this revised Goal4647-4658 chain after Claude's AM1-AM6.

Questions:

1. Are AM1-AM6 fully applied?
2. Is the sequence now dependency-correct?
3. Is partner migration prevented from becoming a fake V4 speed claim?
4. Are the numeric bars concrete enough before measurement?
5. Does the route-binding-before-protocol order fix the earlier flaw?
6. Does this chain avoid process churn while preserving release safety?
7. Can execution begin with Goal4647, or is another rewrite required?

Requested verdict labels:

- `approve_execute_goal4647`
- `approve_with_minor_edits`
- `reject_rewrite_required`
- `blocked_missing_context`

Non-authorization:

This revised chain does not authorize POD spend, public performance claims,
broad V4 release wording, CuPy performance claims, arbitrary Numba callback
claims, C ABI/embedding claims, or app-level V4 speedup claims. It authorizes
only review of the revised plan.
