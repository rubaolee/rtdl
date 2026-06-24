# Goal 109 Archive RTDL v0.1 Baseline

Date: 2026-04-05
Author: Codex
Status: complete

## Purpose

This goal freezes RTDL v0.1 into a named archival baseline so users can keep
using the reviewed v0.1 release even as v0.2 work changes the live branch.

## Frozen baseline

The archived v0.1 baseline is:

- tag: `v0.1.0`
- tag object: `d82a2c28201ed43cddb3da62ba093d6118a2c84f`
- target commit: `85fcd90a7462ef01137426af7b0224e7da518eb4`
- short target commit: `85fcd90`

The tag has been created, and the archive note treats it as the canonical
frozen baseline identifier.

## Archive surface added

New archive docs:

- `docs/archive/README.md`
- `docs/archive/v0_1/README.md`

Front-door links added:

- `README.md`
- `docs/README.md`

## What the archive note provides

The archive note tells users:

- what v0.1 is
- which tag/commit defines it
- how to check it out
- where its canonical release reports live
- why they should prefer the tag over the evolving `main` branch when they
  want the stable v0.1 baseline

## Final position

Goal 109 gives RTDL a stable historical release anchor instead of forcing users
to infer v0.1 from branch history.
