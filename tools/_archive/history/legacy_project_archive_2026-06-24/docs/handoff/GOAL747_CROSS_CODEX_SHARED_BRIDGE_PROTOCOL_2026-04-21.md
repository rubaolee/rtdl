# Goal 747: Cross-Codex Shared Bridge Protocol

## Purpose

The user should not act as a messenger between Mac/Linux Codex and Windows Codex. RTDL agents should coordinate through the home-network shared directory.

## Shared Mailbox

Mounted on this Mac at:

`/Volumes/192.168.1.20/extra-1/rtdl_codex_bridge`

Expected Windows path:

`Z:\extra-1\rtdl_codex_bridge`

## Folder Contract

| Folder | Writer | Reader | Purpose |
|---|---|---|---|
| `to_windows/` | Mac/Linux Codex | Windows Codex | Requests, validation tasks, implementation handoffs. |
| `from_windows/` | Windows Codex | Mac/Linux Codex | Replies, reports, blocker findings, validation results. |
| `status/` | both | both | Small current-status files. |
| `archive/` | either after closure | both | Completed request/reply pairs. |

## Request Rules

Each request must be self-contained:

- repository URL;
- exact target commit or branch;
- task objective;
- required setup;
- exact commands where possible;
- expected report path;
- whether commits are allowed;
- whether pushes are allowed;
- blocker reporting policy.

## Reply Rules

Each reply must include:

- exact commit hash;
- environment;
- commands run;
- pass/fail status;
- artifacts written;
- blockers or no-blocker verdict;
- whether any files were modified, committed, or pushed.

## Default Policy

Unless a request explicitly says otherwise:

- Windows Codex is validation-only.
- Windows Codex must not commit.
- Windows Codex must not push.
- Windows Codex must report blockers and wait for explicit approval before source changes.

## Current Division Of Labor

Linux is the primary development path for NVIDIA/OptiX and RTX-class GPU performance work.

Windows Codex is an independent portability/validation worker and may run Windows-specific Embree checks, public doc checks, command truth audits, and focused regression tests.

Mac Codex handles orchestration, docs, audits, Apple RT checks, and shared-bridge coordination.
