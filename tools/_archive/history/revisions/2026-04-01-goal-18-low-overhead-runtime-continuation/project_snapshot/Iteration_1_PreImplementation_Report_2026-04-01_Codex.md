## Goal 18 Pre-Implementation Report

Goal 17 established that the successful low-overhead path is:

- packed inputs
- prepared execution
- raw-row result views

But Goal 17 still left two practical problems:

1. the fast path is still a side API rather than a first-class runtime mode
2. only `lsi` and `pip` are covered

The continuation slice therefore proposes:

1. make `run_embree(...)` capable of returning raw-row views directly
2. extend prepared/raw support to the remaining Embree-backed workloads where practical
3. add any missing packers for triangles/rays/segments/polygons/points needed by that extension
4. test parity on the extended workload set
5. keep native-comparison claims limited to workloads that actually have native baselines

Questions for review:

1. Is this the right continuation slice?
2. Which workloads should be mandatory in this round?
3. What would count as sufficient evidence for closure?
