# Goal 113 Generate-Only Maturation Plan

Date: 2026-04-05
Author: Codex
Status: proposed

## Planning question

How do we make generate-only mode stronger than Goal 111 without letting it
turn into broad, low-signal template growth?

## Immediate planning answer

Goal 113 should not begin by adding many workloads.

The safer first move is:

- keep `segment_polygon_hitcount` as the seed family
- strengthen the request contract and generated-program quality
- add one real improvement that users would notice

## Recommended first target

The strongest first Goal 113 target is:

- improve the generated-program handoff quality and request expressiveness

Concretely, that likely means:

- clearer request schema
- a small amount of useful generated variation
- stronger generated verification contract
- better separation between generator logic and rendered program blocks

## What Goal 113 should avoid

- adding multiple workload families immediately
- adding fake options that do not change user value
- claiming general code generation too early
- broad native-code targets before the Python RTDL path is clearly stronger

## Product-value test

Goal 113 should survive only if a reviewer can say:

- this is visibly better than Goal 111 for a real user scenario

It should not survive if the honest answer is:

- “it is the same generator, but with more flags”
