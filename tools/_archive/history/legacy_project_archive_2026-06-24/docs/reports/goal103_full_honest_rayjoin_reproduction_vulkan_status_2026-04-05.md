# Goal 103 Status: Full Honest RayJoin Reproduction, Vulkan-Only

Date: 2026-04-05
Status: complete

## Current interpretation

Goal 103 should not try to reuse the OptiX/Embree performance story.

The honest Vulkan-only story so far is:

- Vulkan is hardware-validated
- Vulkan is parity-clean on the accepted long exact-source `county_zipcode`
  positive-hit `pip` surface
- Vulkan is measured on both:
  - prepared / prepacked
  - repeated raw-input
- Vulkan remains slower than PostGIS on both accepted long boundaries

That means Goal 103 is still viable, but its value is:

- support
- correctness
- execution completeness

not mature-performance closure.

## Immediate package anchor

Current accepted Vulkan anchor rows:

1. prepared long exact-source `county_zipcode` positive-hit `pip`
   - Goal 87
2. repeated raw-input long exact-source `county_zipcode` positive-hit `pip`
   - Goal 88

These are the natural starting anchors for Goal 103.

## Expected classification pressure

The strict classification rule used in Goal 102 should likely carry forward
unchanged here:

- paper-identical dataset coverage would be required for `exact`
- so the current Vulkan package is likely to close mostly or entirely as
  `bounded_analogue`

## Final evidence position

Accepted Vulkan rows now available for Goal 103:

1. long exact-source `county_zipcode` prepared
   - Goal 87
2. long exact-source `county_zipcode` repeated raw-input
   - Goal 88
3. bounded top4 prepared `county_zipcode`
   - Goal 85
4. hardware smoke / validation ladder
   - Goal 85

Rows without acceptable Vulkan evidence remain explicit non-results for this
goal rather than hidden omissions.
