# V4 Goals 4749-4758: Final V4.0 Completion Plan

Date: 2026-06-26

Status: active V4.0 completion goal chain

## Controlling Decision

V4.0 must be completed as the current RTDL user release. V4.0 work includes:

- V4 as a superset of V2.14/V3 RT-core benchmark-app capability.
- First-class CuPy and Numba partner support where those partners are claimed.
- A complete 10-app, same-hardware, same-semantics NVIDIA RT-core V2.14/V3/V4 benchmark matrix.
- Clean public documentation, tutorials, examples, and claim boundaries.

V4.1 is not the place to defer V4.0 compatibility, partner support, or benchmark matrix work. V4.1 is reserved for continuing the broader Numba ray-action/Tier-3 line beyond the V4.0 constrained predicate surface.

## Non-Negotiable Rules

1. No Embree denominator for primary V2.14/V3/V4 performance claims. Embree is control/reference only.
2. No `n/a` in user-facing app matrices. If a row cannot run, record the exact engineering blocker and convert it into a V4.0 repair task.
3. V4 is a superset release line. Existing mature V2.14/V3 RT-core app routes must be inherited or exposed in V4 unless a documented removal decision exists.
4. Same-semantics only: exact-vs-exact, threshold-vs-threshold, full-app-vs-full-app, hot-vs-hot, wall-vs-wall.
5. Correctness parity is a hard gate before any speed ratio can count.
6. Separate support from speed:
   - inherited compatibility support is required;
   - V4-new speedup requires fresh evidence that the V4 mechanism is materially faster.
7. Every completed goal needs a 3-AI completion consensus record or an explicit review-debt record, per the standing user rule. Do not block engineering on non-release micro-review when debt is allowed.

## Goal4749 - Freeze The Final Same-Semantics RT-Core Benchmark Protocol

Purpose: define the exact benchmark contract before more timing work.

Development work:

- Create the final 10-app V2.14/V3/V4 protocol table.
- For each app, specify V2.14 route, V3 route, V4 route, semantic contract, partner, RT-core requirement, hot metric, wall metric, correctness oracle, and allowed controls.
- Mark whether V4 route is inherited compatibility, V4-new route, or both.

Test work:

- Add a machine-readable protocol JSON.
- Add a local test that rejects Embree as primary denominator, rejects `n/a`, and requires same-semantics classification for all 10 apps.

Exit gate:

- 10/10 apps have a frozen protocol row.
- Every row has an executable command or an explicit V4.0 repair blocker.
- No public speed claim is authorized by this goal.

## Goal4750 - Build The Unified POD Runner For V2.14/V3/V4

Purpose: stop manual, inconsistent app timing and produce one repeatable POD runner.

Development work:

- Implement a runner that knows the three roots:
  - `/root/rtdl_v2_14_tag`
  - `/root/rtdl_v3_0_2_tag`
  - `/root/rtdl_v4_candidate_pod`
- Use the recorded RTX POD key and environment.
- Set both `RTDL_OPTIX_LIB` and `RTDL_OPTIX_LIBRARY` for old tags.
- Emit raw stdout/stderr, parsed metrics, route metadata, correctness result, and failure reason for every app/version row.

Test work:

- Add local parser/unit tests for the runner.
- Add a dry-run mode that validates all 30 app/version commands without running the POD timing.

Exit gate:

- Dry-run emits 30 rows.
- No row has `n/a`.
- Failure states are explicit and machine-readable.

## Goal4751 - Repair V4 Superset Compatibility For Missing Or Ambiguous App Rows

Purpose: make V4 actually include V2.14/V3 benchmark-app capability.

Development work:

- Repair or expose V4 compatibility routes for:
  - `robot_collision`
  - `contact_manifold`
  - `spatial_rayjoin`
  - `hausdorff_xhd`
- For each app, prefer inherited V2.14/V3 RT-core route compatibility before trying to claim a V4-new route.
- Keep V4-new performance classification separate from compatibility.

Test work:

- Add compatibility tests proving each repaired V4 route can be planned or invoked from the V4 front door.
- Add fail-closed tests for unsupported partner/semantic combinations.

Exit gate:

- V4 has a non-hidden compatibility route or explicit executable current route for 10/10 benchmark apps.
- Any remaining blocker becomes a named release blocker, not `n/a`.

## Goal4752 - Complete CuPy And Numba Partner Contract Audit

Purpose: make partner support user-visible and honest.

Development work:

- For every V4 operator/app route, classify CuPy and Numba as:
  - measured supported;
  - inherited supported;
  - declared unmeasured;
  - not supported with reason.
- Ensure `partner="cupy"` and `partner="numba"` planning is explicit and fail-closed.
- Preserve the boundary that arbitrary Numba ray-action callbacks are V4.1+, while V4.0 supports constrained Numba predicate early-exit.

Test work:

- Add catalog/planner tests for partner classification.
- Add docs tests ensuring partner support is not overclaimed.

Exit gate:

- Users can see exactly when to choose CuPy or Numba.
- No partner-migration row is counted as V4-new speedup.

## Goal4753 - Run Full NVIDIA RT-Core POD Matrix

Purpose: produce the final fair performance evidence requested by the user.

Development work:

- Sync runner and any V4 compatibility repairs to the RTX POD.
- Run V2.14/V3/V4 for all 10 apps under the frozen protocol.
- Use serious, non-toy scales matching existing benchmark intent and POD budget.

Test work:

- Correctness parity for every comparable row.
- Hot and wall metrics for every successful row.
- Capture all raw artifacts and summary JSON.

Exit gate:

- 30 app/version rows attempted.
- Every app has a clear V2.14/V3/V4 status.
- No Embree primary denominator.
- No `n/a`.

## Goal4754 - Analyze The Matrix And Classify V4.0 Claims

Purpose: convert raw timings into honest release claims.

Development work:

- Produce per-app table:
  - V2.14 hot/wall;
  - V3 hot/wall;
  - V4 hot/wall;
  - V4/V2.14;
  - V4/V3;
  - correctness;
  - route class;
  - partner;
  - fair-comparison status.
- Classify every win as V4-new, inherited compatibility, partner migration, parity, regression, or incomparable-but-repaired.

Test work:

- Machine gate verifies all ratios have denominators and all claim classes obey policy.

Exit gate:

- Release wording can be generated from the matrix without manual reinterpretation.

## Goal4755 - Fix Remaining Performance Or Compatibility Regressions

Purpose: repair any serious blocker revealed by Goal4753/4754 before release.

Development work:

- For each regression or failed compatibility row, either:
  - fix the V4 route;
  - inherit the older route correctly;
  - or record a deliberate non-release blocker.

Test work:

- Rerun only affected POD rows after each fix.

Exit gate:

- No unexplained serious regression remains.
- Any surviving regression is explicitly accepted by release decision, not hidden.

## Goal4756 - Clean Public V4.0 Documentation, Tutorials, And Examples

Purpose: make the user-facing V4.0 simple, current, and non-misleading.

Development work:

- Update README, docs, tutorials, examples, and front-door quickstart.
- Move historical/development-only material away from the user path.
- Document:
  - V4.0 architecture;
  - partner choice;
  - benchmark matrix;
  - compatibility vs V4-new speedups;
  - Numba constrained predicate status;
  - V4.1 deferred ray-action work.

Test work:

- Docs tests reject outdated `n/a`, Embree-primary speed ratios, broad all-app claims without matrix support, and V4.1 work mislabeled as V4.0.
- Example smoke tests pass locally.

Exit gate:

- A new user sees one coherent V4.0 story.

## Goal4757 - Final Local Release Gate

Purpose: ensure the repo itself is coherent before external review.

Development work:

- Run the V4 local test suite and selected V3/V2 compatibility gates that protect the release.
- Produce a clean release candidate ledger with changed files, evidence files, and remaining risk.

Test work:

- Full relevant unit tests pass locally.
- Benchmark evidence paths exist and parse.

Exit gate:

- Local machine gate says V4.0 release candidate is internally coherent.

## Goal4758 - External Review And Final V4.0 Release Decision

Purpose: obtain the required release-level external consensus.

Development work:

- Prepare one final review packet, not micro-review churn.
- Include:
  - final protocol;
  - raw POD matrix;
  - analysis;
  - docs/examples status;
  - claim boundary;
  - known limitations;
  - V4.1 deferrals.

Review work:

- Claude and Antigravity review required.
- Third AI seat required by standing rule; if unavailable, record explicit review debt only if the user allows release with debt.

Exit gate:

- One of:
  - `release_authorized_v4_0`;
  - `release_blocked_fix_required`;
  - `release_reframed_with_limitations`.

## Immediate Next Action

Start Goal4749 now. Do not run the final POD matrix until the protocol and runner dry-run gates are complete.
