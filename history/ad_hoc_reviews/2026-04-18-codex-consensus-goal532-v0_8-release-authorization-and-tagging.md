# Codex Consensus: Goal532 v0.8 Release Authorization And Tagging

Date: 2026-04-18
Verdict: **ACCEPT**

Goal532 is accepted as the correct conversion from the bounded v0.8 release
candidate to the `v0.8.0` release.

## Basis

- The user explicitly authorized release if the pre-release test,
  documentation, and audit gates had passed.
- The pre-release gate chain is already recorded:
  - Goal528 macOS audit: `232` tests OK and `62/62` public command harness pass.
  - Goal529 Linux validation: `232` tests OK and `88/88` public command harness
    pass with Embree, OptiX, and Vulkan available.
  - Goal530 release-candidate package: Claude/Gemini/Codex accepted.
  - Goal531 public release-candidate links: Claude/Gemini/Codex accepted.
- Goal532 local validation passes:
  - focused Goal530-532 release guards: `10` tests OK.
  - full local unit discovery: `232` tests OK.
  - stale candidate wording check over live v0.8 public docs: clean.
  - `git diff --check`: clean.
- External AI review is complete:
  - Claude: ACCEPT, tag safe after the Goal532 commit.
  - Gemini Flash: ACCEPT, tag safe after the commit.

## Boundary

The release remains bounded:

- `v0.8.0` is an app-building release over the released `v0.7.0`
  language/runtime surface.
- It does not widen the v0.7 DB/language/backend contract.
- It does not claim RTDL is a DBMS, ANN system, robotics stack, clustering
  engine, simulation framework, renderer, or universal speedup system.

## Decision

Commit the Goal532 release conversion, then create and push annotated tag
`v0.8.0` on that Goal532 release commit.
