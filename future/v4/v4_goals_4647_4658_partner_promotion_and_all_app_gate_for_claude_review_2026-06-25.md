# V4 Goals 4647-4658: Partner Promotion And All-App Gate

Date: 2026-06-25
Status: reviewed by Claude; approved only with required amendments, not
execution authorization as written
Previous completed goal: Goal4646, pre-tag mandatory wording fixes

Claude review:

- `docs/reviews/claude_v4_goals_4647_4658_review_2026-06-25.md`
- Verdict: `approve_with_required_amendments`
- Required before execution: apply AM1-AM6 from
  `future/v4/v4_goals_4647_4658_claude_amendments_and_final_recheck_2026-06-25.md`
- Most important lock: partner migration / partner parity cannot support
  "V4 is faster than V2.14" claims.

## Why This Goal Chain Exists

The current V4.0.0 state is a bounded operator release: eight measured generic
Tier-2 operator surfaces, an explicit `rtdsl.v4` front door, a planner/catalog,
and corrected public wording. That is real progress, but it is not the same as
proving that V4 is broadly faster than V2.14 or V3 at the benchmark-app level.

V2.14 already had strong CuPy and Numba partner evidence across many routes.
The next V4 work must not pretend those assets are new, lost, or irrelevant.
Instead, it must promote the proven V2.14 partner routes into V4's unified
front-door/catalog contract, then run a serious app-level gate.

## Non-Negotiable Rules

- Do not claim broad V4 speedup until the full app-level gate passes.
- Do not count V2.14 historical CuPy/Numba rows as V4 support until they are
  migrated into V4 front-door surfaces and re-certified under V4 contracts.
- Do not add app-identity kernels such as `DBSCAN kernel`, `Barnes-Hut kernel`,
  or `RayJoin kernel`.
- Do not skip benchmark apps. If an app has no V4 app route, record
  `no_v4_app_route_blocker`.
- Correctness parity is a hard gate, equal to performance.
- Every measured result must record command, hardware, raw JSON, ratio,
  baseline denominator, scale, and claim boundary.
- No post-hoc reclassification after seeing results. Classifications and bars
  must be frozen before POD runs.
- External review is required for goal-list approval and final release
  decisions. Intermediate implementation can proceed with review debt only if
  the work is not a release decision.

## Goal4647 - Current Truth And Claim Boundary Freeze

Purpose:

Freeze the exact current truth before doing more work, so V4 does not repeat
the V3 failure mode of changing the story after measurements.

Scope:

- Record what V4.0.0 currently proves:
  - eight measured generic Tier-2 operator surfaces;
  - Torch CUDA as the main measured V4 device-array partner;
  - one Numba-scoped component-union surface;
  - one RTDL-native AABB surface;
  - no CuPy V4 performance claim;
  - no broad all-benchmark speedup claim;
  - no raw OptiX callback / C ABI / embedding claim.
- Record what V2.14 already proved at route level:
  - CuPy grouped-reduction and device-column paths;
  - Numba continuation and fused-route paths;
  - route/app-specific performance packets.
- Produce a single boundary ledger mapping:
  `V2.14 asset -> current V4 status -> promotion needed -> public claim status`.

Exit evidence:

- `future/v4/v4_goal4647_current_truth_and_claim_boundary_freeze_2026-06-25.md`
- Machine-readable JSON ledger with one row per major V2.14 partner asset.
- Explicit statement that this goal does not authorize any new performance
  claim.

Forbidden:

- No new benchmarks.
- No claim expansion.
- No rewriting V2.14 history as if V4 invented those partner routes.

## Goal4648 - V2.14 CuPy/Numba Partner Route Inventory

Purpose:

Find and rank all serious V2.14 CuPy and Numba routes that are candidates for
V4 promotion.

Scope:

- Search historical reports, handoff docs, scripts, tests, and evidence
  packets for CuPy/Numba routes.
- Classify each route:
  - `promotion_candidate_strong`
  - `promotion_candidate_needs_rerun`
  - `historical_only`
  - `rejected_or_no_go`
- Extract for each candidate:
  - route name;
  - benchmark family/app;
  - partner;
  - input/output contract;
  - measured ratio;
  - baseline denominator;
  - scale;
  - raw artifact path;
  - why it is generic or why it is app-specific.

Exit evidence:

- `future/v4/v4_goal4648_v2_14_cupy_numba_partner_inventory_2026-06-25.md`
- JSON candidate inventory.
- Top promotion list, ordered by expected V4 value and genericity.

Forbidden:

- Do not include toy rows.
- Do not promote rows that lack correctness evidence.
- Do not treat app-identity routes as V4 surfaces.

## Goal4649 - V4 Promotion Contract For CuPy And Fixed Numba Continuations

Purpose:

Define the exact V4 contract that historical partner routes must satisfy before
they become official V4 catalog surfaces.

Scope:

- Define the V4 CuPy device-array contract:
  - accepted CuPy array dtypes;
  - contiguity requirements;
  - CUDA device requirements;
  - stream synchronization rules;
  - output ownership and materialization rules;
  - no-host-hot-path telemetry.
- Define fixed Numba continuation contract:
  - allowed fixed operators only, not arbitrary callback support;
  - accepted signatures;
  - correctness parity rules;
  - compile/cache timing boundaries;
  - performance denominator rules.
- Define fail-closed behavior for unsupported partner/operator combinations.

Exit evidence:

- `future/v4/v4_goal4649_partner_promotion_contract_2026-06-25.md`
- Tests for catalog/planner behavior:
  - CuPy planned-but-unmeasured before certification;
  - fixed Numba continuations recognized only when certified;
  - arbitrary Numba callback remains Tier-3 spike-only.

Forbidden:

- No generic "Numba callback support" wording.
- No CuPy performance claim before Goal4650 passes.

## Goal4650 - CuPy Front-Door Certification Gate

Purpose:

Promote CuPy from historical strong partner evidence to an actual V4 certified
device-array partner.

Scope:

- Select at least three generic surfaces where CuPy is structurally meaningful:
  - grouped reduction / grouped i64 or weighted sum;
  - fixed-radius count-threshold or nearest-witness style route if supported;
  - one ray/triangle continuation route if feasible.
- Run CuPy input/output arrays through the V4 front door.
- Verify:
  - no Python row/object materialization in the measured hot path;
  - correctness parity;
  - raw command and JSON artifacts;
  - ratio against CuPy brute-force/reference baseline;
  - denominator and scale recorded.

Exit evidence:

- `future/v4/v4_goal4650_cupy_frontdoor_certification_gate_2026-06-25.md`
- POD evidence directory with raw JSON and logs.
- Catalog updated only for passed CuPy surfaces.

Pass bar:

- At least three CuPy V4 surfaces pass correctness.
- At least two surfaces show material speedup over stated CuPy baseline.
- Any failed surface remains recorded and excluded.

Forbidden:

- No "CuPy supported" blanket claim. Only passed surfaces count.
- No reuse of V2.14 ratios without V4 rerun.

## Goal4651 - Fixed Numba Continuation Certification Gate

Purpose:

Promote fixed Numba-backed continuation operators where V2.14 already showed
serious value, while keeping arbitrary callback support out of V4.0.

Scope:

- Select fixed continuation operators from the inventory, such as:
  - component union / component signature;
  - aggregate or vector reduction;
  - compact/summary-style continuation if generic enough.
- Certify each as a fixed V4 operator surface or reject it.
- Explicitly separate:
  - fixed continuation operator support;
  - arbitrary user Numba device callback support;
  - Tier-3 Numba->PTX->OptiX spike.

Exit evidence:

- `future/v4/v4_goal4651_fixed_numba_continuation_certification_gate_2026-06-25.md`
- POD evidence for certified surfaces.
- Catalog and planner tests.

Pass bar:

- At least two fixed Numba continuation surfaces pass correctness.
- At least one produces material runtime-sourced speedup at release scale.
- Arbitrary callback wording remains blocked.

Forbidden:

- No claim that users can pass arbitrary Numba callbacks into OptiX.
- No app-specific Numba route promotion unless the operator is made generic.

## Goal4652 - V4 Partner Catalog Promotion And Regression Gate

Purpose:

After Goals4650-4651, rebuild the V4 catalog so measured partners are accurate
and regression-protected.

Scope:

- Update `measured_operator_catalog_v4()`.
- Update planner behavior for Torch, CuPy, fixed Numba, and RTDL-native
  surfaces.
- Add regression tests ensuring:
  - measured partners match actual evidence;
  - unmeasured partners fail closed;
  - surfaces record baseline denominators;
  - no broad speedup wording appears.

Exit evidence:

- `future/v4/v4_goal4652_partner_catalog_promotion_regression_gate_2026-06-25.md`
- Local full V4 catalog regression pass.
- GPU regression pass if required by newly promoted surfaces.

Forbidden:

- Do not add a catalog row without raw evidence.
- Do not leave stale `declared_unmeasured` partner wording after certification.

## Goal4653 - Full App-Level V2.14/V3/V4 Benchmark Protocol Freeze

Purpose:

Freeze the serious all-app comparison protocol before any full POD spend.

Scope:

- Apps:
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
- For each app, define:
  - V2.14 route;
  - V3 route;
  - V4 route;
  - correctness contract;
  - dataset scale;
  - warmup/repeat;
  - metric windows;
  - baseline denominator;
  - failure labels.
- Freeze bars before running:
  - whole-suite geomean threshold;
  - per-app minimum floor;
  - app win count;
  - blocker conditions;
  - allowed exclusions, if any.

Exit evidence:

- `future/v4/v4_goal4653_full_app_level_benchmark_protocol_freeze_2026-06-25.md`
- JSON protocol.
- External review request to Claude and Antigravity before full run.

Forbidden:

- No app-level benchmark run before this protocol is reviewed.
- No post-hoc app exclusion.

## Goal4654 - V4 App Route Binding Or Blocker Declaration

Purpose:

Make every benchmark app enter the app-level gate honestly: either with a real
V4 route or with an explicit blocker.

Scope:

- Bind each app to V4 operator surfaces where possible.
- If an app cannot use V4 surfaces without app-specific kernels, record a
  blocker such as:
  - `no_v4_app_route_blocker`
  - `requires_cupy_promotion`
  - `requires_numba_fixed_continuation`
  - `requires_new_generic_operator`
  - `backend_bound_not_v4_lever`
- Ensure route binding records whether the path actually uses V4 code.

Exit evidence:

- `future/v4/v4_goal4654_app_route_binding_or_blocker_declaration_2026-06-25.md`
- One row per app with route or blocker.
- Tests or dry-runs for all route bindings.

Forbidden:

- No silent fallback to V2/V3 route while calling it V4.
- No app-specific kernel implementation to rescue a single app.

## Goal4655 - Serious Full App-Level POD Benchmark

Purpose:

Run the actual same-hardware V2.14 vs V3 vs V4 benchmark suite.

Scope:

- Use the frozen Goal4653 protocol.
- Run on the same RT hardware class with recorded driver/CUDA/OptiX versions.
- For each app record:
  - V2.14 wall time;
  - V3 wall time;
  - V4 wall time;
  - hot phase/operator timing;
  - correctness parity;
  - route metadata;
  - raw logs and JSON.

Exit evidence:

- `future/v4/v4_goal4655_full_app_level_v2_14_v3_v4_pod_benchmark_2026-06-25.md`
- Raw evidence directory with per-app JSON and logs.
- No release claim yet.

Forbidden:

- No partial-result public claim.
- No rerun-only-the-winners behavior.

## Goal4656 - Benchmark Analysis And Release Interpretation

Purpose:

Read Goal4655 without self-deception.

Scope:

- Produce app-level table:
  - V4/V2.14 ratio;
  - V4/V3 ratio;
  - V3/V2.14 ratio;
  - correctness status;
  - route source;
  - blocker status.
- Separate:
  - true V4 runtime/operator wins;
  - partner migration wins;
  - algorithmic-complexity wins;
  - parity rows;
  - regressions;
  - no-route blockers.
- Determine whether formal high-performance V4 is supported.

Exit evidence:

- `future/v4/v4_goal4656_full_app_level_benchmark_analysis_2026-06-25.md`
- JSON scorecard.

Decision labels:

- `formal_high_performance_v4_supported`
- `bounded_operator_v4_only`
- `v4_partner_promotion_needed`
- `v4_no_go_reframe_required`

Forbidden:

- No broad claim if the scorecard does not support it.
- No hiding deferred apps.

## Goal4657 - User Docs And Tutorial Rewrite Based On App-Level Truth

Purpose:

Update public docs only after the app-level truth is known.

Scope:

- If V4 passes:
  - write formal high-performance V4 docs with exact supported claims.
- If V4 does not pass:
  - keep V4 as bounded operator release;
  - explain partner promotion and app-level gaps without scaring users.
- Ensure tutorials are runnable and match actual supported partner surfaces.
- Keep historical/deferred material out of the user front door.

Exit evidence:

- Updated README/front page/current status/tutorials.
- Example dry-run and runnable-test evidence.
- No stale wording from earlier V3/V4 overclaims.

Forbidden:

- No marketing text that exceeds Goal4656.
- No deep-history references in user-facing quickstart unless explicitly marked.

## Goal4658 - Final 3-AI Release Or Reframe Authorization

Purpose:

Get the final external decision on what V4 honestly is.

Scope:

- Send Goals4647-4657 outputs to at least Claude and Antigravity, with a third
  AI seat if required by owner protocol.
- Ask reviewers to decide:
  - formal high-performance V4 release;
  - bounded operator V4 release only;
  - partner-promotion continuation;
  - no-go/reframe.
- Record explicit authorization and non-authorization.

Exit evidence:

- `future/v4/reviews/goal4658_final_v4_release_or_reframe_authorization_2026-06-25.md`
- Final decision file.
- Public tag/release action only if authorized.

Forbidden:

- No final release tag without 3-AI authorization.
- No owner-facing ambiguity about what is released.

## Claude Review Request

Please critically review this proposed Goal4647-4658 chain.

Questions:

1. Does the sequence correctly continue after Goal4646?
2. Does it preserve the distinction between V2.14 historical partner success
   and V4 certified front-door support?
3. Are CuPy and fixed Numba promotion handled correctly, without pretending
   that arbitrary callbacks are supported?
4. Is the app-level V2.14/V3/V4 gate strict enough to justify or block formal
   high-performance V4?
5. Are any goals process churn rather than necessary engineering/release gates?
6. Are the pass/fail labels and forbidden actions strong enough to prevent
   another V3-style overclaim?
7. What goals should be merged, split, removed, or reordered before execution?

Requested verdict labels:

- `approve_execute_as_written`
- `approve_with_required_amendments`
- `reject_rewrite_required`
- `blocked_missing_context`

Non-authorization:

This goal proposal does not authorize implementation, POD spend, public
performance claims, broad V4 release wording, CuPy performance claims, arbitrary
Numba callback claims, C ABI/embedding claims, or app-level V4 speedup claims.
