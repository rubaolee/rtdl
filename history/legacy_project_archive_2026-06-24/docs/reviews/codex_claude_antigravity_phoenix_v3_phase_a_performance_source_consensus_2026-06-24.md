# Phoenix V3 Phase A Performance-Source Consensus

Date: 2026-06-24
Status: `phase_a_complete_no_go_enter_phase_h`

## Verdict

```text
phase_a_exit_gate_met: false
phase_a_complete: true
next_phase: H capability/quality release planning
continue_phase_a_candidate_search: false
continue_to_phase_b_high_performance_path: false
release_authorized: false
all_app_authorized: false
public_speedup_wording_authorized: false
```

## Inputs

- Codex packet:
  `docs/reviews/call_for_review_phoenix_v3_phase_a_performance_source_no_go_2026-06-24.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_phase_a_performance_source_no_go_review_2026-06-24.md`
- Antigravity review:
  `docs/reviews/antigravity_phoenix_v3_phase_a_performance_source_no_go_review_2026-06-24.md`

## Independent Verdicts

- Claude:
  `accept_phase_a_no_go_enter_phase_h_capability_quality`
- Antigravity:
  `accept_phase_a_no_go_enter_phase_h_capability_quality`
- Codex proposed:
  `accept_phase_a_no_go_enter_phase_h_capability_quality`

## Evidence Summary

- Barnes-Hut proves the V3 runtime trunk can execute with residency/parity, but
  does not produce a scorecard-moving performance source. It is closed as
  trunk-proof/control with no further tuning.
- RTNN was the reselected anti-avoidance candidate. It executes through the
  productized runner with parity and zero failed checks, but the scorecard-bound
  clustered/262144 OptiX row projects only to `1.03622547722238x`, far below the
  `>=1.20x` Set-A performance-source bar.
- The RTNN cold+query submetric `1.5809404755935226x` is real but cannot replace
  the frozen scorecard-bound runner-wall row.
- Searching for a third winner is forbidden by the anti-avoidance lock and both
  external reviews.

## Immediate Consequence

Phoenix V3 leaves Phase A through the No-Go fork and enters Phase H
capability/quality release planning. The high-performance Phase B path is not
entered unless a future release owner explicitly reopens Phase A with a named,
externally reviewed, non-metric-shopping experiment.

Phase G repository/version-truth cleanup remains required and should be done as
part of making the H branch honest to users.

## Non-Authorization

No V3 release is authorized by this consensus. No all-app benchmark, no public
speedup wording, no broad V3-over-V2 claim, no V4, no embedding, no C ABI, and
no external zero-copy claim are authorized.
