# Claude Review: v0.4 Working Plan

Date: 2026-04-09
Reviewer: Claude (Sonnet 4.6)

## Verdict

The plan is sound. Approve the 9-goal ladder, the dataset ladder, and the PostGIS role as written. No blocking concerns.

## Findings

**Goal ladder — size and order**

The 9-goal count is right. The separation is deliberate and justified: contract before surface, truth path before backend closure, external baselines before the second workload, GPU backends deferred until the CPU/Embree path is trusted, release material last. That ordering reflects the main lesson from v0.3.0 and should be kept intact.

One minor watch point: Goal 8 combines OptiX and Vulkan into a single slice. If one backend proves significantly harder than the other, that goal may need to split at execution time. The plan does not have to pre-split it now, but the implementer should watch for this early and not let one backend block the other indefinitely.

**Dataset ladder — realism and honesty**

The ladder is realistic. All four tiers name real, publicly accessible sources: in-repo synthetics, Natural Earth (public domain), NYC Street Tree Census (stable city open data), and Geofabrik OSM regional extracts. No paywalled or fragile sources appear. The intended use for each tier is correctly bounded — tutorials and correctness at the small end, stress tests and benchmark subsets only at the large end. The optional literature-comparison baselines (RTNN, PCLOctree, FRNN, FastRNN) are correctly marked non-blocking.

**PostGIS role — scope containment**

The PostGIS role is correctly bounded. `ST_DWithin` and the `<->` operator are appropriate verification tools for moderate-scale radius and nearest-order checks. The plan is explicit that PostGIS is not the primary truth path, not the only benchmark story, and not the implementation model for RTDL semantics. `scipy.spatial.cKDTree` is correctly named as the primary CPU development baseline. That ordering is the right call.

**Non-graphical and workload-first**

The plan is entirely workload-first and contains no graphical scope. All nine goals concern contract design, correctness infrastructure, backend closure, or release evidence. Goal 9 releases examples, docs, and a benchmark report — not a visual demo. The v0.4 identity remains: RTDL adds a first-class nearest-neighbor workload family.

## Summary

The 9-goal ladder is the right size and the right order. The dataset ladder is honest and uses real public sources with appropriate tier boundaries. The PostGIS role is clearly a support role, not a product-identity claim. The milestone is non-graphical and workload-first throughout. The only item to watch at execution time is whether Goal 8 needs to split if OptiX and Vulkan close at very different rates.
