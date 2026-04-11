# Goal 227: Beginner Tutorial Reorganization

## Why

The existing beginner-facing docs were workable, but still too fragmented:

- one long quick tutorial
- one flat release-facing example index
- separate user-guide and feature/reference pages

That made it harder for a new user to answer:

- where should I start?
- which example should I read next?
- how do hello-world, sorting, workloads, and 3D demos fit together?

## Goal

Reorganize the beginner learning surface so it teaches RTDL through a clear
tutorial ladder:

1. first successful run
2. smallest kernel example
3. compact programmable demo
4. released workload families
5. active nearest-neighbor preview workloads
6. RTDL-plus-Python rendering/app demos

## Scope

- rewrite `docs/quick_tutorial.md` into a true front-door quick-start
- add a tutorial hub under `docs/tutorials/`
- add separate tutorials for:
  - hello world
  - sorting demo
  - segment/polygon and overlap workloads
  - nearest-neighbor workloads
  - RTDL-plus-Python rendering demos
- wire the new tutorial surface into the docs/example entry pages

## Out Of Scope

- rewriting the full archive
- changing workload contracts
- performance claims
- release actions

## Acceptance

- a beginner can identify a recommended learning order without reading deep
  reference docs first
- hello-world, sorting, workload tutorials, and 3D demos each have an honest
  place in the learning structure
- the tutorial surface remains consistent with the current released `v0.2`
  scope and active `v0.4` preview scope
- review closure is recorded under at least `2+` AI consensus
