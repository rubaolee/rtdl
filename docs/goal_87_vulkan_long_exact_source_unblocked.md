## Goal 87: Vulkan Long Exact-Source Unblocked

### Objective

Replace Vulkan's worst-case positive-hit candidate allocation contract so the
accepted long exact-source `county_zipcode` prepared boundary can run on Linux
hardware without tripping the old `512 MiB` guardrail.

### Why

Goal 85 proved that Vulkan was parity-clean on bounded accepted surfaces, but
the true long exact-source prepared row still failed before execution because
the sparse positive-hit path budgeted output as if every `(point, polygon)` pair
might become a candidate.

### Required Outcome

- keep exact parity
- preserve the public positive-hit `pip` contract
- run the same long exact-source prepared surface already used by OptiX and
  Embree
- record the actual performance result honestly, even if Vulkan remains slower

### Non-Goals

- no fake claim that Vulkan beats PostGIS unless the measured row proves it
- no change to full-matrix Vulkan semantics
- no weakening of host exact finalization
