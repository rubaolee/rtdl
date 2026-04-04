## Goal 77: Runtime Cache End-to-End Measurement

### Objective

Measure whether the Goal 76 runtime prepared-execution cache reduces repeated-call end-to-end cost without requiring programmers to hand-manage prepared kernels.

### Scope

- repeated identical raw-input RTDL calls
- prepared-execution cache now owned by runtime
- focus on the same backend families where prepared execution already mattered:
  - Embree
  - OptiX
  - Vulkan

### Required Outcome

- a measured package that compares repeated raw-input calls before and after runtime-owned cache reuse
- explicit statement of what timing boundary is used
- no invented speedup claims

### Non-Goals

- no new semantics
- no user-facing optimization knobs
- no change to oracle or PostGIS truth contracts
