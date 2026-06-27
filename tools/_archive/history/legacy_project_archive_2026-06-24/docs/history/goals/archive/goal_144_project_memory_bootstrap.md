# Goal 144: Project Memory Bootstrap

## Goal

Create one canonical single-file context document so future Codex sessions can
recover the live RTDL state quickly without replaying the entire conversation
history.

## Required Outcome

- add a single handoff/bootstrap file that covers:
  - project identity
  - trust model
  - platforms
  - current feature surface
  - strongest current stories
  - completed goal lines
  - review workflow
  - remote Linux workflow
  - main honesty boundaries
- update `docs/handoff/START_HERE.md` to point to it first

## Acceptance

- a future Codex session can read one file and know:
  - what RTDL is
  - what `main` currently supports
  - which platform is primary
  - which docs to trust first
  - how to reach the Linux host
  - what claims must stay narrow
