# Codex Consensus: Phoenix V3 Aggregate Release Readiness

Date: 2026-06-21
Status: `claude_codex_consensus_phoenix_v3_aggregate_release_not_ready_fix_p0`
Verdict: `not-release-ready-fix-p0`

External review:

```text
docs/reviews/claude_phoenix_v3_aggregate_release_readiness_review_2026-06-21.md
```

## Consensus Decision

Codex accepts the Claude aggregate review. The scoped installer closure and the
single-RTX hardware-scope waiver are real closure credit:

```text
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
```

They do not authorize release.

## Remaining P0 Release Blockers

Only these remain as aggregate release P0 blockers:

```text
release_authorization_false
eleven_row_surface_still_too_narrow_for_major_release
aggregate_release_readiness_consensus_blocks_release
```

The previous `current_eleven_row_release_readiness_consensus_blocks_release`
state is superseded by this aggregate consensus. The broad V3-over-V2 speedup
issue remains a hard forbidden-claim constraint, but it is not a separate P0
release blocker if the release continues to prohibit broad speedup wording.

## Required Claim Constraints

These fields must remain false:

```text
broad_v3_faster_than_v2_claim_authorized: false
public_speedup_claim_authorized: false
package_install_claim_authorized: false
multi_gpu_performance_portability_claim_authorized: false
secondary_rt_performance_confirmation_authorized: false
release_authorized: false
```

## Gate Implication

`v3_phoenix_release_readiness_gate.py` should require this aggregate Claude
review plus this Codex consensus, keep `status: blocked_not_release`, and use
the three aggregate P0 blockers above.

## Goal-Level Decision Self-Audit

1. Was I foolish?

No. I did not turn scoped sub-blocker closure into release authorization, and I
accepted the external review's narrower P0 list without weakening forbidden
claim fields.

2. If yes, what actions made the decision foolish?

Not applicable. The foolish action would have been either releasing on green
structural gates or keeping stale blocker wording after external review refined
the blocker list.

3. Was there another path that would have avoided getting stuck on that idea?

Yes. Keep the older four-blocker list unchanged, but that would misclassify a
forbidden claim boundary as a release P0 even when the wording gate keeps the
claim forbidden.

4. Can I now try a different path that actually solves the problem?

Yes. Update the gate and docs so release remains blocked for the true P0
reasons: no release authorization, eleven-row surface too narrow, and aggregate
consensus still not release-ready.
