# Goal2106 v2.0 Release-Hold Checkpoint

Status: complete.

Purpose: record the user's release-edge decision after the documentation
re-engineering pass.

## Decision

The project may continue doing all normal v2.0 release-preparation work and
keep that work synced online. The only forbidden step is the final release
action:

- no `v2.0` tag;
- no GitHub release publication;
- no final release announcement;
- no final-release wording replacing pre-release/hold wording.

## Work Completed Before This Checkpoint

| Area | Status |
| --- | --- |
| Public learner docs | Cleaned to current v2.0-facing surface. |
| Docs lanes | Learn, Research, Audit, and History separated. |
| Front-page navigation | Active local links clean; old-version active markers removed. |
| Examples | Current wrappers kept at root; archived helpers moved internal. |
| Root clutter | Tracked `apps/`, `generated/`, `schemas`, and `build` front-door paths removed. |
| Scripts/tests | Reader indexes added. |
| Gemini review | Goal2105 accepted the Goal2104 summary. |

## Release-Hold Artifact

Added `docs/release_reports/v2_0_release_hold_checkpoint.md` as the standing
release-edge note for reviewers and future agents.

## Boundary

This checkpoint does not authorize release. It makes the hold explicit so the
repo can stay clean and online while final release authority remains reserved
for the user's explicit button press.

