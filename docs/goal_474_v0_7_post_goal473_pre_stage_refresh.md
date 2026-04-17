# Goal 474: v0.7 Post-Goal473 Pre-Stage Refresh

Date opened: 2026-04-16

## Objective

Refresh the advisory pre-stage package/filelist evidence after Goals 466-473.

## Scope

- Generate a current dirty-tree filelist ledger.
- Generate advisory dry-run `git add` command groups.
- Validate closed-goal evidence coverage through Goal 473.
- Keep Goal 439 as an open external-tester intake ledger.
- Exclude archive artifacts.
- Obtain 2-AI consensus before closure.

## Non-Goals

- Do not stage files.
- Do not commit, tag, push, merge, or release.
- Do not change runtime behavior.

## Acceptance Criteria

- `scripts/goal474_post_goal473_pre_stage_refresh.py` runs successfully.
- Generated JSON reports `valid: true`.
- The generated refresh records `staging_performed: false` and
  `release_authorization: false`.
- At least one Claude or Gemini review accepts the refresh.
