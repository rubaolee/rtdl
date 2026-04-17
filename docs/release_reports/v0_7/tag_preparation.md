# RTDL v0.7.0 Tag Preparation

Date: 2026-04-16
Status: release authorized

## Current Decision

Tag `v0.7.0` from the current `codex/v0_7_rt_db` release commit.

## Why

- the bounded DB line is now release-gated through Goal 470
- Goals 431 and 438 package the branch surface honestly
- Goal 467 handled the newer external correctness and Windows audit reports,
  including a fresh Windows current-branch retest for the stale Embree DLL/API
  blocker
- Goal 469 handled the external v0.7 DB attack report and closed actionable
  local edge-case gaps
- Goal 470 adds current pre-release full local testing, Linux focused
  PostgreSQL/native backend testing, doc refresh, and audit evidence
- Goal 471 handled the newer external Windows v0.6.1 Expert Attack Suite report
  as supporting graph/geometry stress evidence only
- Goal 477 adds newer local broad unittest discovery evidence with Claude and
  Gemini external-review acceptance
- Goal 479 adds the current release-candidate evidence audit after Goal478 with
  Claude and Gemini external-review acceptance
- Goal 482 adds the current post-Goal481 dry-run staging command plan with
  Claude and Gemini external-review acceptance
- Goal 483 refreshes the release-facing reports after Goal482 with Claude and
  Gemini external-review acceptance
- Goal 486 verifies post-disk-cleanup artifact integrity after disabling the
  accidental home-directory Git repository
- Goal 487 verifies the release-hold state remains stable after Goal486
- Goal 488 verifies front-page, tutorial, example, and release-doc consistency
- Goal 489 verifies current-safe history synchronization through the v0.7 hold
  state
- Goal 490 refreshes the advisory pre-stage ledger after Goal489 and preserves
  the no-stage/no-release boundary
- release authorization was explicitly provided after Goal492

## What Is Ready

- bounded DB kernel surface
- cross-engine correctness closure on Linux
- bounded Linux performance package with PostgreSQL included
- native prepared DB dataset support for Embree, OptiX, and Vulkan
- columnar prepared DB dataset transfer for Embree, OptiX, and Vulkan
- refreshed repeated-query performance gate against best-tested PostgreSQL
  modes on Linux
- Goal 452 wording is canonical: query-only results are mixed, while
  setup-plus-10-query total time favors RTDL in the measured Linux evidence
- public examples/tutorials aligned with the achieved backend surface
- app-level and kernel-form v0.7 DB demos are present
- Goal 464 validates the current package from a fresh Linux checkout after
  building missing OptiX/Vulkan backend libraries
- Goal 467 validates the current package response to the newer external reports:
  - macOS user-correctness report is positive
  - Windows stale Embree DLL/API blocker is fixed and retested for the bounded
    graph/API/Embree deployment surface
- Goal 469 validates the imported v0.7 DB attack suite and closes local
  attack-report gaps
- Goal 470 validates the current worktree with:
  - local full unittest discovery: 941 tests, 105 expected skips, no failures
  - Linux focused v0.7 DB/PostgreSQL/native suite: 155 tests, no failures
- Goal 471 preserves the Windows v0.6.1 Expert Attack Suite report and records
  that it is not v0.7 release authorization
- Final broad local unittest discovery passes with 1151 tests and 105 skips,
  has Claude and Gemini external-review acceptance, and is not release
  authorization
- Goal 479 release-candidate audit is valid, has Claude and Gemini
  external-review acceptance, and is not release authorization
- Goal 482 dry-run staging plan is valid, includes `427` release-package paths,
  excludes only `rtdsl_current.tar.gz`, leaves `0` manual-review paths, has
  Claude and Gemini external-review acceptance, and is not staging or release
  authorization
- Goal 483 release-report refresh has Claude and Gemini external-review
  acceptance and is not staging or release authorization
- Goal 486 artifact-integrity audit is valid, has Claude and Gemini
  external-review acceptance, and is not staging or release authorization
- Goal 487 release-hold stability audit is valid, has Claude and Gemini
  external-review acceptance, and is not staging or release authorization
- Goal 488 front/tutorial/example/doc consistency audit is valid, has Claude
  and Gemini external-review acceptance, and is not staging or release
  authorization
- Goal 489 history synchronization audit is valid, has Claude and Gemini
  external-review acceptance, and is not staging or release authorization
- Goal 490 pre-stage ledger refresh is valid, excludes only
  `rtdsl_current.tar.gz` by default, leaves `0` manual-review paths, and is not
  staging or release authorization

## Hardware Caveat

The Goal 464 fresh-checkout run used a GTX 1070. That GPU has no NVIDIA RT
cores, so the run validates backend functionality and bounded Linux performance
but is not RT-core hardware-speedup evidence.

## Release Condition

Release as `v0.7.0` with the documented bounded DB scope. Do not merge to
`main` unless separately instructed.
