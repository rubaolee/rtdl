# Claude External Review: Phoenix V3 Core Gaps Status And Next Work After Redirect

Date: 2026-06-22
Reviewer: Claude (independent external reviewer)
Packet under review:
`docs/reviews/call_for_review_phoenix_v3_core_gaps_status_and_next_work_after_claude_2026-06-22.md`
Protocol:
`docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`
Raw capture:
`docs/reviews/claude_phoenix_v3_core_gaps_status_and_next_work_after_claude_review_2026-06-22.raw.md`

## Verdict

```text
verdict: approve_blocked_not_release
```

Claude's judgment: AABB M2.1 advances Gap 1 but does not close it. The
grouped-stream runner route remains neutral. The direction is correct, but
there is no basis for `release_ready`; there is also no reason to downgrade to
`block_p0` or `block_p1`.

## Non-Authorization

```text
v3_release_authorized: false
public_speedup_wording_authorized: false
broad_v3_over_v2_wording_authorized: false
true_zero_copy_wording_authorized: false
all_app_rerun_authorized: false
set_a_set_b_bar_frozen_as_official: false
aabb_m2_1_may_proceed_to_m7_review: true, with Codex consensus and restricted claim shape
```

## Highest-Severity Findings

### F1: Gap 1 Still Needs A Second Material Set-A Probe

Only one material productized-path Set-A probe currently exists: AABB M2.1.
The grouped-stream route is valid route evidence but neutral at `0.9979x`.
Before any all-app pod run can be authorized, a second Set-A focused pod A/B
must show a material wall-level gain from `prepared_execution_session_runner`,
with `runtime_executed: true` in route metadata.

Claude's lower bound for the second focused probe is at least `1.15x` wall via
the productized path, with `1.20x` preferred.

### F2: AABB M2.1 Is Valid, But The Claim Shape Must Include Slower Prepare

Claude accepts AABB M2.1 as valid Set-A productized-path evidence because it
executes through `prepared_execution_session_runner`, records
`runtime_executed_count: 50`, records `cache_hit_count: 49`, preserves CPU
reference correctness, and reports wall-level wins:

```text
runner wall: 1.337x
cold-plus-collect wall: 1.346x
```

The acceptable claim must also say that OptiX prepare is slower than Embree:

```text
OptiX / Embree prepare speedup: 0.700x
```

Any AABB M2.1 M7 record must carry the full phase table inline and must not
imply cold-start or prepare-phase speedup.

### F3: Set A / Set B Membership Is Not Yet Frozen

Claude accepts the Set A / Set B proposal as the working measurement bar, but
not as an official frozen bar. Before any formal all-app use, a separate
classification record must list every row and its Set-A or Set-B assignment
with a one-line rationale, committed before results are seen.

### F4: "M7 Qualified" Status Labels Can Mislead Users

Claude flagged the current grouped-reduction device-column status label
`m7_qualified_row_scoped_after_claude_codex_consensus` as externally confusing.
The row remains valid scoped evidence, but user-facing/current packets should
rename that status to a safer shape such as
`m7_row_evidence_scoped_not_release`.

### F5: Aggregate "Release Ready" Status Names Can Mislead Users

Claude flagged `aggregate_13_row_external_review_status:
external_verdict_obtained_claude_release_ready_after_dossier` as a confusing
historical field name because V3 remains `redo_required`. Current docs should
qualify that older verdict as scoped dossier evidence, not aggregate release
authorization.

## Answers Accepted From Claude

- Current status remains `approve_blocked_not_release`.
- AABB M2.1 may proceed toward M7 review after Codex consensus, with restricted
  wording and full phase disclosure.
- Set A / Set B should be the working bar, but only after membership is frozen
  before a run.
- The next engineering priority should be RTDBSCAN / grouped-reduction /
  component-union continuation through the runner, not another app-specific
  benchmark route.
- The four-gap structure is correct, with Gap 1 as parent blocker. The
  remaining Gap-1 work is breadth, not existence.
- Current AABB work is not app-development drift, but the next
  component-union route must stay generic.

## Required Fixes

| Priority | Required fix |
| --- | --- |
| P1 | Produce a second material Set-A runner-backed focused pod result, at least `1.15x` wall via productized path. |
| P1 | Freeze Set A / Set B membership before any all-app run. |
| P2 | Rename the grouped-reduction `m7_qualified_row_scoped` current status label to avoid implying release qualification. |
| P2 | Qualify the older aggregate `release_ready` field as scoped dossier evidence, not release authorization. |
| P2 | Confirm surviving docs do not quote deleted release-report paths as authoritative. |

## Codex Consensus Instruction From Claude

Claude explicitly instructs Codex to accept this verdict with this framing:

- `approve_blocked_not_release` is the correct aggregate state.
- AABB M2.1 Set-A evidence and M7 progression are accepted, restricted to the
  claim shape above.
- Set A / Set B is accepted as the working bar pending membership-list freeze.
- F4 and F5 are P2 cleanup items, not blockers for the next probe run.
- RTDBSCAN/component-union is the accepted next-work priority.
- This packet is not external aggregate release authorization; the gate remains
  `redo_required`.
