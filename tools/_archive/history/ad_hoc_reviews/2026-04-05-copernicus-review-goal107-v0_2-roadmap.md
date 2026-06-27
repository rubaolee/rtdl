# Copernicus Review: Goal 107 v0.2 Roadmap

Date: 2026-04-05
Reviewer: Copernicus
Status: complete

## Verdict

Weak proposal. Promising direction, but not yet a credible v0.2 roadmap
without much tighter scoping, harder entry criteria, and a clearer definition
of who this is for.

## Criticisms

- The roadmap still hides its central problem behind clean language: there is
  no concrete user. “Broader programmable system with clearer product value”
  is not a market, workflow, or buyer.
- “Broader workload support” is scope creep with nicer wording. The proposed
  workload groups are already too many directions.
- The plan overestimates conceptual unity. The repo proves a RayJoin-centered
  story, not yet a coherent sorting-plus-graphs-plus-codegen product.
- Generate-only mode is especially risky. The repo’s current value comes from
  audited execution and bounded evidence; codegen-only could become the least
  trustworthy part of the system.
- The performance pillar is still under-disciplined and could again dominate
  the release in practice.

## Strongest Rebuttals

- Deferring AMD/Intel native backends is the right call.
- Requiring a formal scope charter first is sensible.
- Requiring verification after generate-only mode is correct.
- Keeping Vulkan as a correctness/portability backend and Embree as a strong
  CPU baseline is strategically cleaner than pretending every backend has the
  same role.

## Recommendation

Do not treat the first draft as an approved roadmap. Force these changes
first:

1. pick one primary v0.2 user and one primary use case
2. reduce the roadmap to a smaller set of true priorities
3. define a kill criterion for generate-only mode
4. ban vague workload expansion until the scope charter names one exact new
   family and one exact success metric
