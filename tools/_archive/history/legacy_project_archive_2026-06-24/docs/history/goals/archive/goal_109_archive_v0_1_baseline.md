# Goal 109: Archive RTDL v0.1 Baseline

Date: 2026-04-05
Status: complete

## Goal

Freeze RTDL v0.1 into a stable archived baseline so users can continue to
access and use the v0.1 release even as v0.2 work changes the live branch.

## Required outputs

- one frozen `v0.1.0` git tag
- one archive entry point under `docs/archive/v0_1/`
- one front-door link to the archived baseline
- one archive note describing:
  - what v0.1 is
  - what commit/tag defines it
  - how to check it out
  - where its canonical release reports live
  - what bounded claims it makes

## Acceptance

- the exact archived v0.1 baseline is named explicitly by tag and commit
- the archive docs point to the correct release-report package
- users can discover v0.1 from the front door without reading git history
- future v0.2 changes no longer threaten the discoverability of v0.1
