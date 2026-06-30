# Goal 67 Codex Rebuttal and Repair Direction

Date: `2026-04-04`

## Codex Assessment of Gemini Review

Gemini is correct on the important point.

The initial Vulkan tiling attempt should **not** be accepted as the next
scaling fix.

Why:

- the patch did not convert Vulkan `lsi` into a meaningfully more scalable
  accepted path
- it still discarded the GPU `lsi` results
- it still relied on full host-side exact `O(N*M)` truth
- therefore it reduced one immediate failure mode without solving the actual
  large-package maturity problem

## Decision

The initial Vulkan scaling proposal is rejected locally.

Action:

- revert the code experiment
- preserve the proposal and review trail
- continue only with the doc-repair half of the round

## Live-Doc Repair Direction

After Gemini’s review, the repair list is:

1. fix stale Vulkan wording in:
   - `docs/rtdl/README.md`
   - `docs/rtdl/programming_guide.md`
   - `rtdl_status_summary.js`

2. fix stale future-tense wording in:
   - `docs/v0_1_roadmap.md`

3. keep Vulkan status wording honest:
   - parity-clean on the accepted bounded Linux surface
   - still provisional for larger-scale use

## Current Round State

- Vulkan scaling proposal: rejected
- doc repair: still active locally
- docs-only review: approved by Gemini after the stale wording sweep
- consensus on the doc repair sub-round: reached locally between Codex and Gemini
