# Call For Review: Phoenix V3 Phase A Performance Source

Date: 2026-06-24
Status: `request_phase_a_external_review_no_release_no_all_app`

This is the Phase A review packet required by the Claude A-H roadmap. It asks
whether Phase A has honestly failed to prove a V3 performance source and should
therefore enter Phase H capability/quality release planning.

## Roadmap Gate Under Review

Claude A-H Phase A exit gate:

- `>=2` named blockers moved by the runner
- `runtime_executed: true`
- hot-path host materialization measured false
- correctness parity verified
- `win_source` recorded

Decision fork:

- blockers move -> Phase B
- blockers do not move and the cost is the kernel/scorecard-bound path itself
  -> Phase H capability branch

## Evidence 1: Barnes-Hut Goal 0

Primary external verdict:

- `docs/reviews/claude_goal0_verdict_barnes_hut_2026-06-24.md`
- Verdict: `goal0_trunk_proven__barnes_hut_backend_bound__reclassify_and_reselect`

Local evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_m72_barnes_hut_native_leafdfs_t2_20260624_101218/`
- `docs/rebuild/v3/evidence/phoenix_v3_phaseA_barnes_hut_backend_bound_confirm_20260624/`

Read:

- Runtime trunk executes and correctness/residency evidence holds.
- Barnes-Hut does not cross parity or Set-A `>=1.20x`.
- Best native leaf-DFS evidence recovered the `0.844x` scorecard row only to
  about `0.899x` geomean; a separate 32-thread remote-only run projected about
  `0.953x`. The user explicitly rejected continuing `0.953 -> 0.98` as trivial.
- Claude classified Barnes-Hut as trunk proof/control, not a V3 performance
  source. No more Barnes-Hut tuning is allowed.

## Evidence 2: RTNN Reselected Candidate

Mandatory anti-avoidance lock:

- `docs/rebuild/v3/phoenix_v3_phase_a_anti_avoidance_lock_rtnn_2026-06-24.md`

Focused POD evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_phaseA_rtnn_clustered262144_20260624_110456/summary.json`

Shape:

- Family: `fixed_radius_ranked_summary_3d_prepared_session`
- Pressure app: `rtnn`
- Distribution/size: `clustered`, `262144`
- Repeat/warmup: `repeat=50`, `warmups=3`
- Routes: same-contract legacy `prepared_optix_ranked_summary` vs productized
  V3 `prepared_execution_ranked_summary`
- CuPy skipped to save time; parity is runner-vs-legacy.

Measured result:

| Field | Value |
| --- | ---: |
| failed checks | `0` |
| runtime trunk executes | `true` |
| runner-vs-legacy parity | `true` |
| runner vs legacy hot speedup | `0.995625837843205x` |
| runner vs legacy cold+query speedup | `1.5809404755935226x` |
| runner vs legacy runner-wall speedup | `1.03855736873106x` |
| projected frozen OptiX scorecard row, hot | `0.9933903412717201x` |
| projected frozen OptiX scorecard row, runner wall | `1.03622547722238x` |
| runtime-sourced material gain candidate | `false` |

Interpretation:

- The trunk runs and parity holds, but the scorecard-bound row does not move to
  `>=1.20x`.
- The cold+query submetric is strong, but the frozen scorecard row is not moved
  enough on same-contract runner wall. Counting the submetric as the V3 answer
  would repeat the old error of replacing the release metric with a narrower
  internal metric.
- Under Claude's kill condition for the reselected family, this misses the bar.

## Phase A Decision Proposed By Codex

```text
phase_a_exit_gate_met: false
named_blockers_moved_to_bar: 0
trunk_existence_proven: true
performance_source_proven: false
continue_to_phase_b: false
enter_phase_h_capability_quality_branch: true
release_authorized: false
all_app_authorized: false
public_speedup_wording_authorized: false
```

Codex should not search for a third winner. The selected RTNN candidate was the
only remaining plausible Set-A performance-source test after Barnes-Hut. It
failed the scorecard-bound `>=1.20x` gate with parity. Continuing to Triangle,
RayDB, or another already favorable row would be metric shopping.

## Questions For Reviewer

1. Do you agree that Phase A's performance-source exit gate is not met?
2. Do you agree that Barnes-Hut is closed as trunk proof/control and should not
   receive more tuning?
3. Do you agree that the RTNN result proves execution/parity but misses the
   scorecard-bound `>=1.20x` performance-source bar?
4. Do you agree that searching for a third winner is forbidden by the
   anti-avoidance lock?
5. Should Phoenix V3 now enter Phase H capability/quality release planning,
   with no broad V3-over-V2 speedup claim?
6. Are there any concrete, non-metric-shopping grounds to keep Phase A open?

## Acceptable Verdict Labels

- `accept_phase_a_no_go_enter_phase_h_capability_quality`
- `revise_phase_a_before_no_go_due_to_missing_evidence`
- `reject_phase_a_no_go_continue_with_named_non_metric_shopping_experiment`

If rejecting the No-Go, the reviewer must name the exact family, scorecard row,
dominant measured phase, concrete `>=1.20x` runtime-sourced hypothesis, and why
this does not violate the no-third-search anti-avoidance lock.

## Non-Authorization

This packet authorizes no V3 release, no all-app benchmark, no public speedup
wording, no broad V3-over-V2 wording, no V4, no embedding, no C ABI, no external
zero-copy claim, and no further Phase A candidate search unless an external
review explicitly rejects the No-Go with a named non-metric-shopping experiment.
