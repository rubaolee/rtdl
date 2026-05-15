# Goal 471: v0.7 External v0.6.1 Expert Attack Suite Intake

Date opened: 2026-04-16

## Objective

Preserve and triage the newer external Windows RTDL v0.6.1 Expert Attack Suite
validation report without widening the current v0.7 release claim.

## Scope

- Preserve the external report under `docs/reports/`.
- Record the report in the external tester intake ledger.
- Accept the positive Windows Embree graph/geometry stress evidence.
- Keep a clear boundary that this report is not a v0.7 DB/PostgreSQL release
  gate and does not authorize staging, tagging, merging, or release.
- Obtain 2-AI consensus before calling the intake closed.

## Non-Goals

- Do not rerun the Windows v0.6.1 attack suite from this goal.
- Do not change runtime code unless the intake reveals a real defect.
- Do not treat external wording such as "certified for deployment" as RTDL
  release authorization.

## Acceptance Criteria

- The external report is preserved at:
  `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/rtdl_v0_6_1_expert_attack_suite_validation_report_2026-04-16.md`
- The intake ledger contains rows for the positive evidence and the wording
  boundary.
- A Goal 471 response report states exactly what the evidence supports and what
  it does not support.
- At least one Claude or Gemini review accepts the Goal 471 intake.
