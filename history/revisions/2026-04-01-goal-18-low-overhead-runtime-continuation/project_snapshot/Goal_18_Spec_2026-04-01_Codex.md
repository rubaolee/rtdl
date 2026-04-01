## Goal 18 Spec

Title: Low-Overhead Runtime Continuation

Objective:
- continue the Goal 17 redesign
- make the low-overhead path a first-class RTDL runtime mode
- extend it beyond `lsi` and `pip`

Planned first continuation slice:
- add `result_mode` support to `run_embree(...)`
- extend prepared/raw execution support to the remaining Embree-backed local workloads where feasible
- add packed input support for the needed geometry kinds
- keep DSL kernels unchanged
- benchmark and document the extended low-overhead path honestly

Acceptance bar:
- correctness preserved
- low-overhead mode easier to use directly
- extension beyond the first slice
- no overclaiming beyond measured evidence
