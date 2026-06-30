# Goal 482: v0.7 Post-Goal481 Dry-Run Staging Plan

Date: 2026-04-16
Status: Pending review

## Objective

Generate a current dry-run staging command plan for the full v0.7 package after Goal481, without executing any staging command.

## Acceptance Criteria

- Enumerate the current dirty worktree with `git status --porcelain=v1 --untracked-files=all`.
- Include release-package paths, including Goal481 evidence.
- Ignore Goal482 self-artifacts so reruns remain stable.
- Exclude `rtdsl_current.tar.gz` as an archive artifact.
- Verify no manual-review paths remain.
- Generate JSON and Markdown artifacts with grouped `git add -- ...` command strings.
- Verify command strings are advisory only and are not executed.
- Obtain Claude and Gemini external review before calling the goal closed.
- Do not stage, commit, tag, push, merge, or release.
