## Goal 86: Backend Comparison Closure

### Objective

Consolidate the current accepted backend-vs-PostGIS status after the OptiX,
Embree, and Vulkan rounds.

### Scope

- workload family: `county_zipcode`
- query shape: positive-hit `pip`
- compared systems:
  - PostGIS
  - RTDL + OptiX
  - RTDL + Embree
  - RTDL + Vulkan

### Required Outcome

- one honest backend comparison summary
- explicit separation of:
  - long exact-source prepared / repeated-call wins
  - bounded Vulkan hardware-backed status
- explicit note where Vulkan still cannot join the long exact-source row
