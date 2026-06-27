# Goal 192: v0.3 Comprehensive Documentation Review

## Objective

Perform a comprehensive pre-release documentation review so that the final `v0.3`
surface is internally consistent, technically honest, and easy for users to follow.

## Why

The repo now has:

- a clarified public front page
- release-facing docs
- goal/review history
- a bridged `v0.2.0` to `v0.3` story
- 3D demo documentation that must remain secondary to the core RTDL positioning

Before release, the docs need one deliberate end-to-end review instead of piecemeal patching.

## Scope

- review the live front surface
- review tutorial/onboarding flow
- review release-facing docs
- review support matrix / release statement alignment
- review version positioning from `v0.2.0` to `v0.3`
- review path consistency after the `examples/visual_demo/` reorganization
- review honesty language around:
  - RTDL vs rendering
  - backend support boundaries
  - demo artifacts vs release surface

## Required Surfaces

- `README.md`
- `docs/README.md`
- `docs/current_milestone_qa.md`
- `docs/quick_tutorial.md`
- `docs/v0_2_user_guide.md`
- release statement / support matrix docs
- the main `v0.3` status and acceptance package docs

## Non-goals

- no new feature work
- no repo-history archaeology outside live or release-relevant docs
- no major marketing rewrite detached from the technical truth of the repo

## Success Criteria

- live docs are mutually consistent
- release-facing language is accurate and non-overclaiming
- new paths are used consistently where relevant
- the final review report explicitly identifies:
  - corrected mismatches
  - accepted limitations
  - any remaining release blockers
- the goal closes only under:
  - Codex consensus
  - Claude review
  - Gemini review

## Release Relationship

- This is one of the two final pre-release goals before `v0.3` release packaging.
