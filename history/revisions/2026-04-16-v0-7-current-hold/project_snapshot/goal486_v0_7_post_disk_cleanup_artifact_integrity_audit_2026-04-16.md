# Goal 486: v0.7 Post-Disk-Cleanup Artifact Integrity Audit

Date: 2026-04-16
Author: Codex
Status: Accepted

## Scope

Goal486 verifies that the disk-full event and subsequent safe Git temp-garbage cleanup did not leave truncated or invalid v0.7 release evidence artifacts.

Generated artifacts:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal486_post_disk_cleanup_artifact_integrity_audit.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_generated_2026-04-16.md`

## Initial Passing Result

```text
python3 scripts/goal486_post_disk_cleanup_artifact_integrity_audit.py
{"disk_valid": true, "goal484_valid": true, "home_git_garbage_valid": true, "invalid_json_artifacts": 0, "invalid_text_artifacts": 0, "json_artifact_count": 48, "md": "/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_generated_2026-04-16.md", "output": "/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_2026-04-16.json", "text_artifact_count": 1225, "valid": true}
```

## Blocker Found During Rerun

Repeated Goal486 reruns exposed a non-RTDL environmental blocker: a background
`git add` process repeatedly started in `/Users/rl2025`, where the home
directory itself is an active Git repository.

Observed commands included:

- `git add -A` with cwd `/Users/rl2025`
- `git add -- ...` over `.claude/`, `.codex/`, and other home-directory files

Impact:

- new `/Users/rl2025/.git/objects/**/tmp_*` files were created after cleanup
- `git count-objects -vH` intermittently reported fresh Git garbage
- Goal486 cannot be called stable while `/Users/rl2025/.git` remains active and
  background tooling keeps adding the home directory

Immediate mitigation performed:

- stopped the observed home-level `git add` processes
- deleted only newly created `/Users/rl2025/.git/objects/**/tmp_*` files

Required manual decision before Goal486 closure:

- disable the accidental home-directory Git repository by moving
  `/Users/rl2025/.git` aside, or
- identify and stop the background tool that keeps launching home-level
  `git add`

## Resolution

The user approved disabling the accidental home-directory Git repository.

Action performed:

- killed the active home-level `git add -A` process
- moved `/Users/rl2025/.git` to `/Users/rl2025/.git.home-backup-2026-04-16`

This preserves the previous home-directory Git metadata as a backup while
preventing background tooling from treating the whole home directory as the
repository root.

## Passing Rerun After Resolution

```text
python3 scripts/goal486_post_disk_cleanup_artifact_integrity_audit.py
{"disk_valid": true, "goal484_valid": true, "home_git_garbage_valid": true, "invalid_json_artifacts": 0, "invalid_text_artifacts": 0, "json_artifact_count": 48, "md": "/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_generated_2026-04-16.md", "output": "/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_post_disk_cleanup_artifact_integrity_audit_2026-04-16.json", "text_artifact_count": 1228, "valid": true}
```

## Checks Covered

- `48` JSON report artifacts parse successfully.
- `1225` report text artifacts are non-empty.
- Latest Goal484 hold audit remains valid.
- Home-directory Git is disabled and backed up at `/Users/rl2025/.git.home-backup-2026-04-16`.
- No active `/Users/rl2025/.git/objects` path remains for background `git add` temp-object creation.
- Disk free-space threshold is satisfied.
- `git diff --check` is clean.

## Boundary

Goal486 is a post-disk-cleanup artifact-integrity audit only. It does not stage, commit, tag, push, merge, or release.

## External Review

- Claude: ACCEPT, saved at `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_external_review_2026-04-16.md`.
- Gemini: ACCEPT, saved at `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal486_gemini_review_2026-04-16.md`.
- Codex consensus: ACCEPT, saved at `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal486-v0_7-post-disk-cleanup-artifact-integrity-audit.md`.

Goal486 is closed as accepted. No staging, commit, tag, push, merge, or release
was performed.
