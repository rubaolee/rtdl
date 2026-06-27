Please perform a comprehensive repository audit for the current RTDL v0.5 preview state in `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`.

Start by reading these files first:

1. `/Users/rl2025/refresh.md`
2. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/v0_5_goal_sequence_2026-04-11.md`
3. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/support_matrix.md`
4. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal320_v0_5_preview_readiness_audit_2026-04-12.md`
5. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/comprehensive_v0_5_transition_audit_report_2026-04-12.md`
6. `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md`

Then audit the repo with these goals:

## 1. Code-file audit

- Check whether each important `v0.5` code file is covered by meaningful tests.
- Focus especially on:
  - `src/rtdsl/`
  - `src/native/oracle/`
  - `src/native/embree/`
  - `src/native/optix/`
  - `src/native/vulkan/`
  - `scripts/` used for `v0.5` validation/perf/reporting
- Identify missing tests, weak tests, stale tests, fake tests, or places where the claimed closure is stronger than the actual verification.

## 2. Documentation audit

- Check whether each important `v0.5` doc/report/support file is in the correct status.
- Identify:
  - stale wording
  - incorrect release/preview status
  - contradictions between docs
  - overclaims
  - missing honesty boundaries
  - places where backend/platform support is unclear
  - bad version labeling
  - docs that should not be front-facing
  - docs that are orphaned or duplicated

## 3. Goal-process audit

- Check whether each `v0.5` goal appears to follow the required closure flow from `refresh.md`:
  - bounded scope
  - saved review artifact
  - Codex consensus
  - honest closure language
- Identify any goals that appear structurally incomplete, suspicious, inconsistent, or improperly closed.

## Output requirements

Write your report to:

`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/gemini_v0_5_full_repo_audit_review_2026-04-12.md`

The report must be detailed and use tables.

Required table structure:

### 1. Code Audit

Columns:
- `Path`
- `Purpose`
- `Test Coverage Status`
- `Problems`
- `Recommended Fix`

### 2. Doc Audit

Columns:
- `Path`
- `Current Role`
- `Status Correct?`
- `Problems`
- `Recommended Fix`

### 3. Goal Flow Audit

Columns:
- `Goal`
- `Scope Bounded?`
- `Review Saved?`
- `Consensus Saved?`
- `Closure Honest?`
- `Problems`
- `Recommended Fix`

### 4. Top Risks

Columns:
- `Risk`
- `Severity`
- `Why It Matters`
- `Recommended Action`

### 5. Final Verdict

Include:
- overall assessment of the `v0.5 preview` state
- whether it is preview-ready
- whether any goals should be reopened
- whether any docs should be rewritten before broader external review

Important instructions:

- Be strict.
- Prefer finding real problems over being polite.
- Do not just summarize the repo; audit it.
- If something looks unverified, say so explicitly.
- If something is acceptable but bounded, say that clearly.
- Keep the review aligned with the current repo state, not older states.
