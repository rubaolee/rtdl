# V4 Current Goal4660-4666 And Forward Goals

Date: 2026-06-25

Status: active engineering plan, not release authorization

## Current Goal

Current active state:

- Goal4660/4661 RTNN ranked-summary candidate was implemented and measured.
  It validates, but serious rows are hot-path parity/slower versus V2.14/V3.0.2;
  it is not formal high-performance V4 evidence.
- Goal4662/4663 updated the app-route matrix and full app-level protocol to
  reflect RTNN and Hausdorff route truth.
- Goal4664 selected Hausdorff as the next focused target, rejecting an all-app
  rerun until a focused app route moves the decision.
- Goal4665 showed the V4 Torch Hausdorff official route fails the formal
  candidate bar at 262,144 points/side.
- Goal4666 has now productized a V4 official CuPy Hausdorff route and measured
  it on the same POD. The 262,144 points/side row clears the V4/V3 hot and
  prepare bars, but the 65,536 points/side row remains below the frozen bars and
  the app directed-summary denominator is still parity/slower. This is useful
  route productization, not release authorization.
- Goal4667 has now fixed the remaining Hausdorff focused-route bottleneck with
  a generic adaptive CuPy argmax continuation. The focused Hausdorff gate now
  passes at 65,536 and 262,144 points/side, and the 1M correctness-boundary
  probe passes.
- Goal4669 reran the serious full app-level scorecard after Hausdorff was
  promoted into the full candidate set. It found one true app-level V4 win
  (`hausdorff_xhd`) but did not support formal high-performance V4.
- Goal4670 selected RTDBSCAN as the first second-win probe and ran focused POD
  diagnostics. RTDBSCAN did not become the second true V4 win: the true V4
  route is still about `1.08x`, the best generic grouped-union toggle reaches
  only `1.166x`/`1.163x`, and the very fast direct-status rows are
  historical/external-proof-required rather than countable V4 wins.
- Goal4671 ran grouped-union root-read telemetry on the same RTDBSCAN shape and
  closed RTDBSCAN as a no-go for the second true V4 app-level win. The best
  generic telemetry shape is direct side effects with same-root culling disabled,
  but root-find depth is already about one parent-link step per root find, so a
  safe generic path-compression tweak is not a credible `1.20x` lever.
- Goal4672 prerequisite V2.14 per-app primitive audit is now complete. It
  records that V2.14 already had a primitive or explicit mixed partner route for
  every promoted benchmark app in the current V4 set. This blocks selecting
  `robot_collision` as a clean new V4 win target by default: V2.14 already had
  prepared RTDL/OptiX any-hit collision flags and scalar count.
- Goal4672 target selection after the audit is also complete. It selects no
  existing app target and records that the next work must be a new generic
  runtime lever or a material same-primitive improvement target with explicit
  V2.14 denominator.
- Current decision:
  `no_clean_existing_app_second_target_found__new_generic_runtime_lever_required`.
- Next concrete work is Goal4673: choose/design the new generic runtime lever or
  material same-primitive improvement target. It must not start with a POD run.

### Goal4660 - RTNN ranked-summary/top-k V4 candidate route

Purpose:

- Turn the RTNN partial V4 row into a real, auditable V4 app-route candidate.
- Promote only a generic continuation shape: fixed-radius ranked-summary/top-k.
- Do not add an RTNN-specific native kernel.
- Do not count this as measured V4 release evidence until POD scorecard evidence exists.

Current implementation status:

- Added `src/rtdsl/v4_ranked_summary.py`.
- Added candidate surface:
  `v4_fixed_radius_ranked_summary_3d_prepared_runner`.
- Added planner/catalog visibility as:
  `candidate_goal4660_needs_pod_scorecard_not_release`.
- Updated `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
  so `prepared_execution_ranked_summary` calls the V4 candidate wrapper.
- Local V4 gate status:
  `68 tests OK`.
- POD smoke status:
  `2048` points passed; JSON emitted `v4_surface`,
  `v4_candidate_status`, and `runtime_trunk_executes_end_to_end: true`.
- POD serious row status:
  `65536`, `262144`, and `1048576` point rows have been collected for:
  - V2.14 closest old front door:
    `v2_14_prepared_optix_ranked_summary_<scale>.json`
  - V3.0.2 closest old front door:
    `v3_0_2_prepared_optix_ranked_summary_<scale>.json`
  - V4 candidate front door:
    `v4_candidate_prepared_execution_ranked_summary_<scale>.json`
- Machine summary:
  `future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json`.
- Evidence report:
  `future/v4/v4_goal4660_4661_rtnn_ranked_summary_candidate_evidence_2026-06-25.md`.

Important current finding:

- V2.14 and V3.0.2 RTNN app front doors do not have
  `prepared_execution_ranked_summary`.
- Therefore a V2/V3/V4 comparison cannot be honestly described as the exact
  same runner across all versions.
- The allowed comparison is:
  old-version closest available RTNN ranked-summary front door versus V4
  candidate route, with that denominator explicitly stated.

Exit gate:

- POD evidence for serious RTNN scales:
  `65536`, `262144`, and `1048576` points.
- JSON proof that V4 emits:
  - `v4_surface: v4_fixed_radius_ranked_summary_3d_prepared_runner`
  - `v4_candidate_status: candidate_goal4660_needs_pod_scorecard_not_release`
  - correctness/signature validation passes
  - phase timings are recorded
- A written Goal4660/4661 evidence report with decision:
  `rtnn_candidate_does_not_move_app_level_bar`.

Non-success:

- Merely adding the wrapper is not success.
- A green local test without POD timing is not success.
- A V4-only timing without a clear old-version denominator is not success.
- Any broad V4 speed claim is forbidden.

## Forward Goals

### Goal4661 - RTNN serious same-hardware candidate comparison

Status:

- Evidence complete; local tests still need to be run after route-matrix update.
- Evidence rows exist locally under:
  `future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/`.
- Machine summary exists:
  `future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json`.
- The V4 candidate is hot-path parity at serious scales:
  - `262144`: V4/V2.14 `0.999x`, V4/V3.0.2 `1.005x`
  - `1048576`: V4/V2.14 `0.994x`, V4/V3.0.2 `0.993x`

Purpose:

- Measure RTNN V4 candidate against the closest available V2.14/V3.0.2
  ranked-summary routes on the same POD.

Required work:

- Run old-version RTNN ranked-summary rows using their available front door.
- Run V4 candidate `prepared_execution_ranked_summary`.
- Preserve denominator wording:
  old front door is not identical to the V4 prepared-execution wrapper.
- Record correctness/signature validation for every row.

Exit gate:

- Machine summary with timings, correctness, denominator class, and claim class.
- Decision label:
  - `rtnn_candidate_moves_app_level_bar`, or
  - `rtnn_candidate_does_not_move_app_level_bar`.

### Goal4662 - Update app-route binding matrix after Hausdorff and RTNN

Status:

- Complete pending external/debt review.
- RTNN is being updated as:
  `candidate_ranked_summary_present_but_app_bar_not_moved`.
- Hausdorff is recorded as:
  `official_v4_route_with_coordinate_normalized_correctness_boundary`.
- Evidence:
  `future/v4/evidence/v4_goal4662_app_route_binding_after_hausdorff_rtnn_2026-06-25.json`.
- Report:
  `future/v4/v4_goal4662_app_route_binding_after_hausdorff_rtnn_2026-06-25.md`.

Purpose:

- Make Goal4652 route matrix match current engineering truth.

Required work:

- Move `hausdorff_xhd` from partial route to full V4 route only with its
  correctness boundary:
  coordinate-normalized mode required for 1M exactness.
- Move `rtnn` only if Goal4660/4661 evidence justifies it.
- Preserve no-route/deferred rows:
  `spatial_rayjoin` remains no-route unless new work proves otherwise;
  `barnes_hut` remains deferred app-identity route.

Exit gate:

- Updated matrix JSON and tests.
- No silent V2/V3 fallback.
- No release authorization.

### Goal4663 - Refresh full app-level protocol with new route truth

Status:

- Complete pending external/debt review.
- The code-level protocol is synchronized with Goal4662 route truth.
- Report:
  `future/v4/v4_goal4663_app_level_protocol_refresh_after_changed_routes_2026-06-25.md`.
- Machine evidence:
  `future/v4/evidence/v4_goal4663_app_level_protocol_refresh_after_changed_routes_2026-06-25.json`.
- Decision:
  `protocol_refreshed__no_full_all_app_rerun_triggered`.
- Validation:
  `73 tests OK`.

Purpose:

- Update the app-level benchmark protocol so it includes the new route state
  without moving goalposts after results.

Required work:

- Freeze which apps are full V4 routes, partial routes, controls, and blockers.
- Freeze correctness gates before any new all-app run.
- Freeze denominator class for each app.
- Record whether each row can contribute to formal V4 performance.

Exit gate:

- Updated protocol artifact.
- Tests proving the protocol rejects broad claims from partial/candidate rows.

### Goal4664 - Select next real performance target

Purpose:

- Avoid another wasteful all-app run and avoid continuing parity-only rows.
- Pick one app-level target with a plausible generic V4 lever and frozen bars.

Status:

- Complete.
- Selected target: `hausdorff_xhd`.
- Decision:
  `select_hausdorff_for_goal4665_focused_formal_candidate_run`.
- Evidence:
  `future/v4/evidence/v4_goal4664_next_performance_target_selection_2026-06-25.json`.
- Report:
  `future/v4/v4_goal4664_next_performance_target_selection_2026-06-25.md`.
- Validation:
  `46 tests OK`.

Required work:

- Reject RTNN as a performance target because serious rows are parity/slower.
- Reject full all-app rerun until a focused target moves the release decision.
- Freeze the Hausdorff Goal4665 bars and denominators before the next POD run.

Exit gate:

- Machine target-selection summary and test guard proving the next target is
  not parity-only and has numeric bars.

### Goal4665 - Focused Hausdorff formal-candidate POD run

Purpose:

- Run only the selected Hausdorff focused protocol under the frozen Goal4664
  bars.
- Determine whether Hausdorff can contribute real formal V4 performance
  evidence.

Status:

- Complete pending external/debt review.
- Decision:
  `hausdorff_formal_candidate_fails_focused_bar`.
- Evidence:
  `future/v4/evidence/v4_goal4665_hausdorff_focused_20260625/summary.json`.
- Report:
  `future/v4/v4_goal4665_hausdorff_focused_formal_candidate_run_2026-06-25.md`.
- Validation:
  `50 tests OK`.
- Key result:
  262,144 points/side fails the formal bar: V4/V3.0.2 hot `0.649x`, prepare
  floor `0.711x`.

Required work:

- Run V2.14 Embree, V3.0.2 CuPy, and V4 Torch official-route rows for
  `65536` and `262144` points/side.
- Preserve correctness, hot, prepare, materialization, and denominator fields.
- Run the 1,048,576 point V4 coordinate-normalized exactness row as a
  correctness-boundary probe, not a speed claim.
- Do not add any Hausdorff-specific native kernel.

Exit gate:

- Machine summary with pass/fail against:
  - V4/V3.0.2 hot speedup >= `1.20x`;
  - V4/V2.14 primary metric speedup >= `1.20x`;
  - correctness parity required;
  - no unrestricted exactness claim.
- Decision label:
  - `hausdorff_formal_candidate_passes_focused_bar`, or
  - `hausdorff_formal_candidate_fails_focused_bar`.

### Goal4666 - Hausdorff official CuPy route and focused rerun

Purpose:

- Remove the Torch-only bottleneck from the official V4 Hausdorff route.
- Route `partner="cupy"` through the official V4 point-group session and the
  generic CuPy global-argmax continuation.
- Determine whether this repairs Goal4665's failed 262,144 points/side row
  without adding any Hausdorff-specific native kernel.

Status:

- Complete pending external/debt review.
- Decision:
  `official_cupy_route_productized__large_row_passes_hot_prepare__focused_bar_not_reopened`.
- Evidence:
  `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/summary.json`.
- Report:
  `future/v4/v4_goal4666_hausdorff_cupy_official_route_evidence_2026-06-25.md`.
- Validation:
  `30 tests OK`.
- Key result:
  - 65,536 points/side primary row: V4/V3 hot `0.357x`, prepare `0.745x`;
    diagnostic warmup2 rerun improves to hot `0.961x`, prepare `0.793x`, still
    below the frozen bars.
  - 262,144 points/side row: V4/V3 hot `1.288x`, prepare `1.031x`, correctness
    passes.
  - 1,048,576 points/side coordinate-normalized CuPy official route passes
    correctness; it is a correctness-boundary probe, not a speed claim.

Required work:

- Add CuPy output allocation and prepare support to the V4 point-group front
  door.
- Add generic CuPy support to `global_argmax_u32_f64_partner_columns`.
- Remove the app-local CuPy reducer from the Hausdorff hot path.
- Run focused POD rows for 65,536 and 262,144 points/side plus the 1M
  correctness-boundary probe.

Exit gate:

- Machine summary and human report.
- Correctness passes.
- Producer metadata proves the V4 official point-group surface is used.
- Consumer metadata proves the generic CuPy continuation is used.
- Decision does not authorize all-app rerun or V4 release unless both focused
  rows clear the frozen bars. This did not happen.

### Goal4667 - Hausdorff adaptive CuPy argmax focused gate

Purpose:

- Continue the selected Hausdorff focused route by removing the remaining
  generic continuation overhead without changing the app, benchmark bar, or
  denominator.

Status:

- Complete pending external/debt review.
- Decision:
  `hausdorff_focused_gate_passes_after_generic_adaptive_argmax__not_release_yet`.
- Evidence:
  `future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/summary.json`.
- Report:
  `future/v4/v4_goal4667_hausdorff_adaptive_argmax_focused_gate_2026-06-25.md`.
- Key result:
  - 65,536 points/side: V4/V3 hot `1.339x`, prepare `0.942x`.
  - 262,144 points/side: V4/V3 hot `1.832x`, prepare `1.201x`.
  - 1,048,576 points/side coordinate-normalized correctness-boundary probe
    passes.
- This is one focused candidate row and does not authorize release.

Required work:

- Add `synchronize=False` to the generic continuation so the caller can own the
  final hot-window synchronization.
- Replace CuPy global argmax's multi-kernel masked reduction with adaptive
  RawKernel strategies:
  - single-block RawKernel for rows `<= 131072`;
  - multi-block RawKernel for larger rows.
- Preserve correctness and the V3 CuPy denominator.
- Do not add a Hausdorff-specific native kernel.

Exit gate:

- Both focused rows clear:
  - correctness required;
  - V4/V3 hot >= `1.20x`;
  - prepare >= `0.80x`.
- 1M correctness-boundary probe still passes.
- No release or broad speed claim.

### Goal4668 - App-level protocol refresh after Hausdorff focused pass

Purpose:

- Decide whether the full app-level V2.14/V3/V4 benchmark should now run with
  the updated Hausdorff route.

Status:

- Complete pending external/debt review.
- Decision:
  `protocol_refreshed__full_app_rerun_go_after_hausdorff_focused_pass__no_release`.
- Evidence:
  `future/v4/evidence/v4_goal4668_protocol_refresh_after_goal4667_2026-06-25.json`.
- Report:
  `future/v4/v4_goal4668_protocol_refresh_after_hausdorff_focused_pass_2026-06-25.md`.
- Validation:
  `34 tests OK`.
- Result:
  full app candidate rows increase from `4` to `5`; partial controls decrease
  from `4` to `3`; full app rerun is now protocol-authorized, but release is
  not authorized.

Required work:

- Update the protocol to include Goal4667's Hausdorff candidate row.
- Preserve every denominator and correctness gate.
- Keep RTNN as performance-failed candidate.
- Decide whether a full all-app rerun is justified now, or whether another
  focused candidate row is required first.

Exit gate:

- Machine-readable protocol refresh artifact.
- Clear Go/No-Go for full app-level rerun.
- No release authorization.

### Goal4669 - Full app-level V2.14/V3/V4 benchmark rerun, only after protocol Go

Purpose:

- Produce the serious benchmark evidence the user expects before any formal
  high-performance V4 wording, if Goal4668 authorizes it.

Status:

- Complete pending external/debt review.
- Decision:
  `bounded_operator_v4_only__app_level_high_performance_not_supported`.
- Report:
  `future/v4/v4_goal4669_full_app_level_rerun_after_hausdorff_2026-06-25.md`.
- Raw evidence:
  `future/v4/evidence/v4_goal4669_serious_20260625/summary.json`.
- Machine analysis:
  `future/v4/evidence/v4_goal4669_app_level_benchmark_analysis_2026-06-25.json`.
- Key result:
  - Hausdorff XHD passes its custom frozen bar and is a true V4 app candidate win.
  - RTDBSCAN is modest and below the formal bar.
  - RayDB-style and triangle-counting regress against at least one required
    denominator/floor.
  - LibRTS spatial index is parity.
  - Formal high-performance V4 is still not supported.

Required work:

- Run all benchmark apps under frozen protocol.
- Include V2.14, V3.0.2, and current V4.
- Record correctness, denominator, hot/prepare/wall phases, and route class.
- Do not use toy data.

Exit gate:

- Machine-readable scorecard.
- Human-readable analysis.
- Classification for every app:
  true V4 win, partner migration, algorithmic-complexity control, parity,
  regression, or blocked.

### Goal4670 - Select and execute the second independent app-level V4 win target

Purpose:

- Move from one true V4 app candidate win to at least two independent true app
  wins, or prove that formal high-performance V4 should not continue on the
  current architecture.

Status:

- Complete as focused diagnostic; no second true V4 win found.
- Selected first target: `rt_dbscan`.
- Report:
  `future/v4/v4_goal4670_rt_dbscan_second_win_diagnostics_2026-06-25.md`.
- Evidence:
  `future/v4/evidence/v4_goal4670_rtdbscan_diag_20260625/summary.json`.
- Review debt:
  `future/v4/reviews/goal4670_completion_review_debt_no_release_authorization_2026-06-25.md`.
- Decision:
  `rt_dbscan_diagnostics_complete_no_second_true_v4_win_yet`.
- Key result:
  true V4 default route is `1.079x` vs V2.14 hot and `1.076x` vs V3.0.2 hot
  in the updated diagnostic; direct-side-effect reaches `1.116x`/`1.113x`;
  direct-side-effect plus disabled same-root culling reaches
  `1.166x`/`1.163x`; all remain below the frozen `1.20x` bar.

Required work:

- Use the Goal4669 scorecard as the only input truth.
- Choose exactly one non-trivial target before coding:
  - `triangle_counting`: restore or improve V4 vs V3.0.2 without app-specific
    kernels;
  - `rt_dbscan`: find a generic runtime/continuation change capable of moving
    the app from ~1.08x to the formal bar;
  - `raydb_style`: fix the 0.974x no-regression failure only if the same
    generic change can plausibly move it beyond hygiene.
- Freeze the chosen row's denominator and success/failure bar before running.
- Preserve correctness parity.
- Do not count partner migration, wording changes, or focused operator-only
  evidence as the second app win.

Exit gate:

- One of:
  - second independent true V4 app candidate win proven;
  - target fails, with numeric evidence and a recommendation to try the next
    candidate or reframe V4;
  - no viable non-trivial target remains, triggering bounded V4 reframe.

### Goal4671 - RTDBSCAN native grouped-union improvement fork or target pivot

Purpose:

- Decide whether RTDBSCAN still deserves engineering time after Goal4670.

Status:

- Complete as diagnostic no-go.
- Report:
  `future/v4/v4_goal4671_rtdbscan_native_grouped_union_feasibility_2026-06-25.md`.
- Evidence:
  `future/v4/evidence/v4_goal4671_rtdbscan_grouped_union_telemetry_20260625/summary.json`.
- Review debt:
  `future/v4/reviews/goal4671_completion_review_debt_no_release_authorization_2026-06-25.md`.
- Decision:
  `rt_dbscan_grouped_union_no_go__pivot_required_for_second_true_v4_app_win`.
- Key finding:
  best generic telemetry shape is direct side effect with same-root culling
  disabled, but root-find depth is already about `1.0185` parent-link steps per
  root find. Path compression/root halving is not a credible `1.20x` lever.

Required work:

- Inspect the generic native grouped-union implementation and current
  telemetry.
- If there is a credible generic change capable of moving the true V4 route
  from the best observed `1.166x`/`1.163x` probe to at least `1.20x`,
  implement and measure it.
- If not, record RTDBSCAN as not viable for the second true app-level V4 win
  and select a different target.
- Do not lower the bar and do not count direct-status special contracts.

Exit gate:

- Met via:
  `rt_dbscan_grouped_union_no_go__pivot_required_for_second_true_v4_app_win`.

### Goal4672 - Select the next non-parity V4 performance target

Purpose:

- Pick the next target after RTDBSCAN no-go without falling back to parity
  cleanup or process work.
- Prevent old V2.14 primitive/productization work from being counted as a new
  V4 speed win.

Status:

- Prerequisite V2.14 primitive audit complete.
- Target selection complete.
- Report:
  `future/v4/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.md`.
- Evidence:
  `future/v4/evidence/v4_goal4672_v2_14_per_app_primitive_audit_2026-06-25.json`.
- Target-selection report:
  `future/v4/v4_goal4672_next_target_selection_after_v2_14_audit_2026-06-25.md`.
- Target-selection evidence:
  `future/v4/evidence/v4_goal4672_next_target_selection_after_v2_14_audit_2026-06-25.json`.
- Decision:
  `no_clean_existing_app_second_target_found__new_generic_runtime_lever_required`.
- Critical correction:
  `robot_collision` is demoted from clean next target to same-primitive
  improvement candidate because V2.14 already had prepared RTDL/OptiX any-hit
  collision flags and scalar count.

Required work:

- Use the V2.14 primitive audit as a hard input.
- Re-read the Goal4669 app-level rows and current operator catalog.
- Reject rows whose only plausible outcome is `0.98x-1.05x` parity.
- Reject partner-migration rows as proof of V4 speed.
- Reject same-primitive productization rows as proof of V4 speed unless the
  frozen protocol explicitly tests material improvement over the V2.14 route.
- Reject app-identity native kernels.
- Select exactly one target with:
  - app-level mapping;
  - old-version denominator;
  - correctness parity gate;
  - frozen numeric bar;
  - generic V4 lever that could plausibly produce a material win.
- If no such target exists, say so and move to bounded-operator reframe rather
  than inventing a weak target.

Exit gate:

- Machine-readable target-selection artifact.
- Decision label:
  - `next_v4_performance_target_selected`, or
  - `no_nontrivial_second_target_found__bounded_reframe_required`.

Actual exit:

- `no_clean_existing_app_second_target_found__new_generic_runtime_lever_required`.
- This does not force bounded reframe yet; it forces Goal4673 to design/select a
  real new generic runtime lever or a material same-primitive improvement before
  spending POD time.

### Goal4673 - Execute the selected focused target

Purpose:

- Choose/design and then execute the next real V4 target. After Goal4672, there
  is no selected existing app target, so Goal4673 must first name the generic
  runtime lever or material same-primitive improvement target.

Required work:

- Do not start with a POD run.
- Name the generic operator or same-primitive improvement target.
- Prove whether V2.14 already had the same primitive route.
- State whether the goal is a new runtime lever or a same-primitive improvement.
- Freeze V2.14, V3.0.2, and V4 denominators.
- Freeze correctness parity and numeric material-speed bars before running.
- Prove the target is not app-identity.
- Implement only generic V4 operator/runtime changes needed for the selected
  target.
- Run serious same-hardware evidence on the POD.
- Preserve correctness parity and denominator wording.
- Record whether the result is a true V4 runtime win, partner migration,
  algorithmic-control win, parity, or regression.

Exit gate:

- One of:
  - `second_true_v4_app_win_proven`;
  - `selected_target_failed_with_no_goalpost_move`;
  - `selected_target_regressed_or_parity_only`.

### Goal4674 - Formal V4 release decision, docs cleanup, and external review

Purpose:

- Decide honestly whether V4 can be a formal high-performance release or must
  remain bounded operator / app-route-progress.

Required work:

- Apply the frozen bars to Goal4669 plus Goal4670/4671/4673 evidence.
- If the bar fails, do not weaken wording after the fact.
- If the bar passes, identify exactly which apps and routes support the claim.
- Update front page, current docs, tutorials, examples, and machine gates to
  match the selected truth.
- Make runnable tutorials pass.
- Claude review when available.
- Antigravity review if available.
- If either is unavailable, record debt, not approval.
- Do not create internal pseudo-review agents.

Exit gate:

- Final 3-AI consensus if available, or explicit review debt record for every
  missing external seat.
- Release remains unauthorized unless the final decision protocol authorizes it.
- Decision label:
  - `formal_high_performance_v4_supported`, or
  - `bounded_operator_v4_plus_app_route_progress_only`.

## Goal-Level Decision Audit

1. Was I being stupid?
   - I would be stupid if I treated Goal4669's single true Hausdorff app win as
     completed high-performance V4. I am not treating it that way.
2. If yes, what action made it stupid?
   - The stupid action would be jumping from one app win to all-V4 release
     wording while RayDB, triangle, RTDBSCAN, and LibRTS still fail or miss their
     frozen bars.
3. Is there another path that avoids getting stuck on a bad premise?
   - Yes. Goal4670 and Goal4671 have now shown RTDBSCAN is not a second true
     win in its current grouped-union form. The honest path is a different
     app-level target or bounded reframe.
4. Can I now try the different path that actually solves the problem?
   - Yes. Continue with Goal4672 target selection, not release wording and not
     process paperwork.

## Non-Authorization

This plan does not authorize V4 release, broad V4 speedup wording, all-app
speedup wording, unrestricted exact Hausdorff wording, arbitrary callback
support, public true-zero-copy claims, C ABI, embedding, non-Python host
bindings, or app-specific native kernels.
