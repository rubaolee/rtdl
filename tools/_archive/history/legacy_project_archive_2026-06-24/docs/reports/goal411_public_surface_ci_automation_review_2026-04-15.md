# Goal 411 Review: Public Surface CI Automation

Date: 2026-04-15
Reviewer: Codex

## Verdict

ACCEPTED

## Review basis

Three-review chain now exists:

- Gemini Flash checker:
  - [goal411_ai_checker_review_2026-04-15.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal411_ai_checker_review_2026-04-15.md)
- Claude verifier:
  - [goal411_ai_verifier_review_2026-04-15.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal411_ai_verifier_review_2026-04-15.md)
- Codex:
  - this review

## Codex position

Goal 411 is accepted.

The important technical bar is met:

- the repo now has a real hosted workflow:
  - [public-surface.yml](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/.github/workflows/public-surface.yml)
- the workflow runs the Goal 410 public harness directly rather than a forked
  or reduced duplicate
- the hosted run on `main` succeeded
- the hosted artifact is preserved in the repo:
  - [goal411_github_actions_public_surface_report_2026-04-15.json](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal411_github_actions_public_surface_report_2026-04-15.json)

The hosted result is also within the correct honesty boundary:

- `24` passed
- `0` failed
- `11` skipped

with:

- `cpu_python_reference = True`
- `cpu = True`
- `embree = False`
- `optix = False`
- `vulkan = False`

That is the right portable CI contract for now:

- continuously enforce the public first-run baseline
- do not pretend hosted CI has Embree or GPU support

The Node 20 deprecation annotation is real, but non-blocking maintenance debt.

## Acceptance statement

Goal 411 is accepted as the first honest repository-hosted automation gate for
the RTDL public first-run surface.
