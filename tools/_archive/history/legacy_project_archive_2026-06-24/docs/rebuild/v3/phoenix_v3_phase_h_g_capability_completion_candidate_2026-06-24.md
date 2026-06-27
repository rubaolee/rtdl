# Phoenix V3 Phase H/G Capability Completion Candidate

Date: 2026-06-24
Status: `candidate_pending_external_review`

## Verdict Requested

Review whether Phoenix V3 is ready to be completed as a capability/quality
release scope, not as a high-performance release.

Accepted verdict labels:

- `accept_phase_h_g_capability_release_ready`
- `accept_with_required_amendments`
- `reject_overclaims_or_missing_gates`
- `reject_wrong_branch_reopened_performance_path`

## Controlling Decision

Phase A is complete and did not prove a broad high-performance V3 path:

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

Consensus file:
`docs/reviews/codex_claude_antigravity_phoenix_v3_phase_a_performance_source_consensus_2026-06-24.md`

This candidate therefore does not ask reviewers to approve:

- broad V3-over-V2 speed superiority;
- a high-performance major release;
- all-app benchmark victory;
- V4, embedding, C ABI, external device buffers, or true zero-copy;
- any row beyond exact row-scoped evidence.

## What Is Being Completed

Phoenix V3 is being completed as:

- a Python-hosted RTDL source-tree branch;
- a productized prepared-execution/runtime trunk branch;
- an explicit backend/partner-boundary branch;
- a row-scoped evidence branch with thirteen exact rows/supplemental rows;
- a cleaned documentation/tutorial branch that sends users to one current path
  and keeps old V3/V4 release material in history;
- a claim-boundary branch that forbids broad speed claims and release wording
  until the capability/quality review is accepted and the release owner
  authorizes publication.

## Current Version Truth

```text
VERSION: v3-capability-branch-2026-06-24
pyproject: 3.0.0.dev20260624
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The source-tree doctor now checks the capability branch marker and reports
`v3_capability_branch_ready` when required checks pass.

## Current User-Facing Doors

- `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `docs/learn/current_claim_boundaries.md`
- `tutorials/README.md`
- `tutorials/current/README.md`
- `examples/README.md`
- `examples/current/README.md`
- `docs/rebuild/v3/README.md`
- `docs/rebuild/v3/phoenix_v3_phase_h_capability_branch_status_2026-06-24.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`

## Evidence Basis

- Serious same-RT-hardware V2.14 vs Phoenix V3 evidence remains near parity:
  same-row geomean `1.012x`.
- Phase A re-tested the trunk-first performance-source hypothesis and did not
  move a frozen scorecard row to the Set-A bar.
- RTNN proved runner/parity but not material scorecard speed:
  - hot speedup: `0.995625837843205x`;
  - runner-wall speedup: `1.03855736873106x`;
  - projected frozen scorecard row wall: `1.03622547722238x`.
- The exact row-scoped surface remains useful evidence, but it does not
  authorize broad performance wording.

## Current Local Gates

Local gates run after the H/G front-door and blocker-ledger update:

```text
py -3 -m unittest tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_major_performance_mandate_gate_test tests.v3_rebuild_reset_test tests.goal4278_source_tree_doctor_test
19 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
final_public_surface_gate: true
violations: []

py -3 scripts/rtdl_source_tree_doctor.py --json --run-smoke
ok: true
status: v3_capability_branch_ready
required_failures: []
```

The `v3_phoenix_release_readiness_gate_test` passing means the gate correctly
reports the current high-performance branch as `redo_required`; it is expected
behavior, not release authorization.

The full `v3_rebuild` matrix must be rerun after this candidate file is written
and recorded before external review is finalized.

Completed rerun:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 148
tests: 754
status: OK
```

The wording gate scans every lesson in `tutorials/current/`, including lessons
08-15 that teach negative routes and boundary cases.

## What Changed In Phase H/G

- Front doors no longer promote V4 or old V3.0.2 release wording.
- `VERSION` and `pyproject.toml` are non-release capability branch markers.
- Source-tree doctor now checks the capability branch state rather than the old
  V3.0.2/V4 surface.
- The release blocker ledger now separates:
  - current capability/quality branch blockers, and
  - blocked high-performance branch claims.
- The final wording gate now says release wording is blocked until Phase H
  external review and release-owner authorization, while broad speed wording
  remains blocked because the high-performance branch failed.
- Public documentation uses `V3 Capability-Branch Tutorial Path` rather than
  treating "rebuild" as a user-facing product label.

## Open Before Publication

Publication is still not authorized until:

1. external review accepts this H/G capability scope;
2. the release owner explicitly authorizes the final wording;
3. any reviewer-required amendments are applied;
4. the committed repository truth is made consistent with the V3-only mandate.

## Review Questions

1. Does this candidate correctly follow the Phase A No-Go fork into Phase H?
2. Does it avoid reopening Phase B/C/D high-performance work after A failed?
3. Are the docs and gates honest that V3 is not broadly faster than V2.x?
4. Are the current front doors clean enough for a user not to fall into old V3/V4
   material?
5. Is the release blocker ledger now correctly dual-track: capability branch
   pending review, high-performance branch blocked?
6. Are the local gates sufficient for sending the candidate to final release
   owner decision after reviewer amendments?
7. What must be fixed before `accept_phase_h_g_capability_release_ready`?

## Non-Authorization

This packet authorizes no release, no public speedup wording, no all-app run, no
broad V3-over-V2 claim, no V4, no embedding, no C ABI, and no external zero-copy
claim.
