# Codex Consensus: Phoenix V3 Secondary RT Hardware Scope Waiver

Date: 2026-06-21
Status: `claude_codex_consensus_secondary_rt_hardware_scope_waiver_not_release`
Verdict: `accept-with-amendments-not-release`

External review:

```text
docs/reviews/claude_phoenix_v3_secondary_rt_hardware_scope_waiver_review_2026-06-21.md
```

Candidate:

```text
docs/rebuild/v3/v3_secondary_rt_hardware_scope_waiver_candidate_2026-06-21.md
```

## Consensus Decision

Codex accepts Claude's `accept-with-amendments-not-release` verdict after
implementing the required gate and documentation amendments. The waiver closes
only the previous `secondary_rt_performance_confirmation_not_closed` release
blocker, and only under this explicit performance-hardware scope:

```text
single_rtx_4000_ada_driver_550_127_05_pod
```

This is a waiver, not second-machine RT performance confirmation. It does not
authorize V3 release, multi-GPU portability, broad V3-over-V2 speedup, or
package-install wording.

## Machine-Readable Fields

```text
secondary_rt_hardware_scope_waiver_reviewed: true
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
hardware_performance_scope: single_rtx_4000_ada_driver_550_127_05_pod
secondary_rt_performance_confirmation_authorized: false
multi_gpu_performance_portability_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
package_install_claim_authorized: false
release_authorized: false
```

The expected secondary-platform gate status is:

```text
compatibility_confirmed_hardware_scope_waiver_reviewed_not_release
```

## Remaining Release Blockers

The release-readiness gate must remain `blocked_not_release` until a later
aggregate release review supersedes the current not-ready consensus. The
remaining blockers are:

```text
release_authorization_false
eleven_row_surface_still_too_narrow_for_major_release
broad_v3_faster_than_v2_claim_not_authorized
current_eleven_row_release_readiness_consensus_blocks_release
```

This consensus does not authorize release. It only removes the stale secondary
hardware blocker from the current source-tree/pod-gated eleven-row release gate.

## Goal-Level Decision Self-Audit

1. Was I foolish?

No. The decision accepts the waiver only after external review and keeps all
overclaim fields false.

2. If yes, what actions made the decision foolish?

Not applicable. The foolish action would have been treating the reachable RTX
4000 Ada pod as a second hardware class, or using the waiver to imply broad
hardware portability.

3. Was there another path that would have avoided getting stuck on that idea?

Yes. A true second RTX-class machine would be stronger evidence and would avoid
the waiver path, but that hardware is not present in the known current machine
set.

4. Can I now try a different path that actually solves the problem?

Yes. The current path is to keep V3 release blocked, remove only the stale
secondary blocker under the single-pod scope, and seek a new aggregate
release-readiness review that covers the eleven-row surface, scoped installer
closure, and this hardware-scoped waiver.
