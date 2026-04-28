# Goal1064 Claude Review: RTX Runbook Sync After Goal1063

Date: 2026-04-28

## Verdict

ACCEPT.

Goal1064 correctly syncs the runbook and its test suite to the state established
by Goal1062 and Goal1063.

## Criteria Check

### 1. Goal1062 Is the Current Pod Path

PASS. The runbook replaces the stale "Current Post-Goal1048 Runner" heading with
"Current Post-Goal1063 Runner" and explicitly instructs:

> "prefer the generated Goal1062 runner over the older Goal1053 or
> Goal759/Goal761 grouped paths"

The primary command is `bash scripts/goal1062_blocked_rtx_wording_rerun_runner.sh`.
All four Goal1062 rows are enumerated by name (correctness-validation and
large timing-repeat for both `facility_knn_assignment` and
`robot_collision_screening`). The stale Goal1053 11-command broad-batch reference
is demoted to historical fallback only, and the rg search reported no surviving
stale-primary-runner strings.

### 2. Rejected Rows Remain Local-Only Until Code or Scale Changes

PASS. The runbook states:

> "Goal1063 says the broader rejected not-reviewed rows remain local-only until
> code or scale changes. Do not use the Goal1053 11-command batch to collect
> those rows again unless a later local audit supersedes Goal1063."

This is consistent with the Goal1063 audit (`valid: True`) which assigned
`no_pod_until_code_or_scale_changes` or `no_pod_until_scale_contract_changes`
to all eight rejected rows and with the Goal1063 two-AI consensus (ACCEPT).

### 3. Skip-Validation Boundaries Preserved

PASS. The runbook explicitly prohibits adding `--skip-validation` to the two
correctness-validation rows:

> "Do not edit the generated runner on the pod to add `--skip-validation` to the
> two correctness-validation rows."

The Goal1062 manifest confirms the split: correctness-validation rows have
`Skip validation: False`; large timing-repeat rows have `Skip validation: True`
with a `0.100` s timing floor. The test
`test_runbook_prefers_goal1062_for_current_post_goal1063_batch` asserts this
constraint is present in the runbook text. Group B and Group G also retain their
existing skip-validation prohibitions unchanged.

### 4. No Authorization of Cloud, Release, or Public Speedup Wording

PASS. The runbook's Claim Boundary section is unchanged:

> "This runbook collects evidence. It does not authorize public RTX speedup
> claims."

The Goal1064 report boundary is explicit:

> "This is a documentation and test sync only. It does not run cloud, change
> public wording, authorize release, or authorize public RTX speedup claims."

The runbook further requires artifact-intake and 2+ AI review before any large
timing-row evidence can be used to change public wording status.

## Test Coverage

The test suite (`tests/goal829_rtx_cloud_single_session_runbook_test.py`) was
updated with a new `test_runbook_prefers_goal1062_for_current_post_goal1063_batch`
test that asserts all key Goal1062/Goal1063 strings are present and that the
rejected-rows local-only policy is enforced. The report claims 14 tests pass.
The test assertions are tight and cover the primary pod runner, the
correctness-validation skip-validation prohibition, the local-only boundary for
rejected rows, and the artifact copy-back requirement.

## Consistency With Prior Consensus

Goal1062 two-AI consensus: ACCEPT (local-only manifest, correct validation split).
Goal1063 two-AI consensus: ACCEPT (eight rejected rows local-only, four Goal1062
rows pod-ready). Goal1064 does not contradict either; it propagates those
decisions into the runbook and its guard tests without expanding scope.

## No Issues Found

- No stale primary-runner strings (rg search clean).
- No new cloud authorization language.
- No `--skip-validation` added to correctness-validation rows.
- Broader OOM-safe groups (A–H) retained as historical fallback only, not
  promoted.
- Deferred-retry shape, bootstrap ABI rules, artifact copy rules, and shutdown
  rule are all unchanged.

## Boundary

This review is documentation only. It does not run a pod, change public wording,
authorize release, or authorize public RTX speedup claims.
