# Goal 103 Plan: Full Honest RayJoin Reproduction, Vulkan-Only

Date: 2026-04-05
Status: in progress

## Core question

What is the fullest honest RayJoin paper experiment surface that RTDL can
reproduce today using Vulkan only?

## Planned structure

### Phase 1: Freeze the Vulkan-only matrix

Build one explicit matrix covering:

- Table 3 style rows
- Figure 13 style rows
- Figure 14 style rows
- Table 4 / Figure 15 style rows

Each row gets one of:

- `exact`
- `bounded_analogue`
- `unavailable`
- `not_applicable`

### Phase 2: Gather accepted Vulkan evidence

Carry forward already accepted Vulkan evidence where valid:

- long exact-source prepared `county_zipcode` positive-hit `pip`
- long exact-source repeated raw-input `county_zipcode` positive-hit `pip`
- bounded package support rows only if Vulkan has an accepted artifact there

### Phase 3: Fill missing runnable Vulkan rows

Run the remaining rows that are:

- available
- not already closed by accepted Vulkan artifacts
- relevant to a Vulkan-only reproduction package

### Phase 4: Final package

Produce:

- one final Vulkan-only reproduction matrix report
- one machine-readable summary
- one explicit unavailable-row list

## Current working assumption

The likely strongest Vulkan row is still:

- `county_zipcode`
- positive-hit `pip`

but unlike Goal 102, the Vulkan-only package will likely close as:

- parity-clean
- measured on both prepared and repeated raw-input boundaries
- slower than PostGIS

That is still a useful reproduction package because it proves supported
correctness and hardware execution on the same RayJoin-facing surface.
