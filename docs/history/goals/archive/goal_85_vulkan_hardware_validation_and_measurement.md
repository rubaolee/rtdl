## Goal 85: Vulkan Hardware Validation And Measurement

### Objective

Validate the Goal 78 Vulkan positive-hit sparse redesign on real Linux Vulkan
hardware, then measure the backend on accepted county/zipcode positive-hit `pip`
surfaces against PostGIS without weakening the published claim boundaries.

### Required Outcome

- run the Vulkan unit/smoke surface on a Vulkan-capable Linux host
- confirm parity on the accepted goal51 validation ladder
- attempt the accepted long exact-source prepared county surface used by OptiX
  and Embree
- if that surface is still blocked, record the exact blocking reason rather than
  silently substituting a different claim

### Non-Goals

- no fake Vulkan performance win
- no claim that Vulkan joins the OptiX/Embree exact-source long closure unless
  the same surface actually runs and preserves parity
