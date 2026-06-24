# Codex Consensus: Phoenix V3 Source-Tree / Pod-Gated Scoped Release Wording

Date: 2026-06-21

Status:
`claude_codex_consensus_source_tree_pod_gated_scoped_installer_closure_not_release`

External review:
`docs/reviews/claude_phoenix_v3_source_tree_pod_gated_scoped_release_wording_review_2026-06-21.md`

Claude verdict: `accept-with-amendments-not-release`

Codex verdict: accept Claude's scoped installer-blocker closure after applying
the two P0 amendments.

## Decision

Phoenix V3 may close the installer/reproducibility blocker only under this
machine-readable scope:

```text
release_scope: source_tree_pod_gated_eleven_row
installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row
```

The install gate may now report:

```text
installer_closes_release_blocker: true
source_tree_pod_gated_scoped_release_wording_reviewed: true
```

The install gate status remains:

```text
staged_pod_gate_present_general_release_installer_not_ready
```

because a general release installer is still not ready.

## Fields That Must Remain False

This consensus does not authorize release. These fields must remain false:

```text
release_authorized: false
general_release_installer_ready: false
package_install_claim_authorized: false
secondary_rt_performance_confirmation_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## P0 Amendments Applied

Claude required two P0 amendments before any gate field could change.

P0 Amendment 1: the scoped wording candidate must specify the exact gate script
delta. This is now present in:

```text
docs/rebuild/v3/v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md
```

P0 Amendment 2: the scope must be machine-readable in the gate payload. The
accepted fields are:

```text
release_scope: source_tree_pod_gated_eleven_row
installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row
```

Claude's recommended single-hardware disclosure and post-acceptance
`required_next_action` were also applied.

## Claim Boundary

Allowed scoped wording:

```text
Phoenix V3 has a reviewed source-tree/pod-gated reproducibility path for its
current eleven exact row-scoped M7-qualified evidence rows on the documented
RTX 4000 Ada pod environment.
```

Required attached boundaries:

```text
This is not a general package installer.
This does not authorize package-install wording.
This is source-tree/pod-gated evidence from a single RTX 4000 Ada pod.
This does not confirm performance across RT-core hardware classes.
This does not authorize broad V3-over-V2 speedup wording.
This does not authorize whole-app, paper-reproduction, or unscoped benchmark
speedup claims.
This does not by itself authorize V3 release.
```

Forbidden wording:

```text
V3 is release-ready.
V3 is finished.
V3 has a general installer.
pip install rtdl gives a finished V3 GPU release.
V3 performance is confirmed across RT-core hardware.
V3 broadly beats V2.x.
All benchmark apps are release-ready.
The eleven M7 rows imply full-app acceleration.
```

## Remaining P0s

After this consensus, the installer/reproducibility blocker is closed only
under `source_tree_pod_gated_eleven_row` scope.

The remaining independent blockers are:

- `secondary_rt_performance_confirmation_not_closed`;
- `current_eleven_row_release_readiness_consensus_blocks_release`;
- `release_authorization_false`;
- `eleven_row_surface_still_too_narrow_for_major_release`;
- `broad_v3_faster_than_v2_claim_not_authorized`.

The next required action is:

```text
Close secondary RT performance blocker with a second RTX/RT-core run or an
explicit 2-AI-reviewed hardware-scoped waiver. Then obtain a new aggregate
release-readiness external review.
```

## Goal-Level Decision Audit

Decision: close the installer/reproducibility blocker only under the
machine-readable `source_tree_pod_gated_eleven_row` scope.

1. Was I foolish?
   No. Claude accepted the scoped path only after requiring machine-readable
   scope fields, and this consensus keeps all release-authorizing fields false.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to set
   `installer_closes_release_blocker: true` without `release_scope` and
   `installer_closes_release_blocker_scope`.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Build a general package installer instead. That remains the path for
   future package-install wording.
4. Can I now try a different path that actually solves the problem?
   Yes. With installer/reproducibility scoped-closed, move to secondary
   RT-core evidence or hardware-scoped waiver, then request final aggregate
   release-readiness review.
