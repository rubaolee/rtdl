# Claude Review: v0.4 GPU Re-work Proposal

Date: 2026-04-10

## Verdict

Approved. The proposal correctly identifies and corrects a structural gap in the
prior `v0.4` closure: the two new public workloads were accepted without GPU
RT-core backend support, which conflicts with RTDL's stated project identity.
The reopened bar — OptiX required, Vulkan runnable and parity-clean — is the
right correction.

## Findings

**The gap in the earlier closure is real and material.**
The current support matrix marks OptiX and Vulkan as "not in v0.4 scope" for
`fixed_radius_neighbors` and `knn_rows`. The release statement explicitly
disclaims "GPU nearest-neighbor backend closure." That is internally consistent
for a CPU/Embree milestone, but it is not consistent with a project whose stated
purpose is GPU RT-core exploitation of geometric-query workloads. The earlier
closure was honest about what it covered; the problem is what it chose not to
cover.

**OptiX-first priority is correct.**
OptiX is the most direct RT-core backend in the current stack. Closing both
workloads on OptiX before addressing Vulkan gives the reopened `v0.4` a clean
initial GPU evidence base and satisfies the project's primary GPU purpose
without waiting for the full Vulkan story. Goals 216 and 217 map cleanly to
this: one workload per goal, each requiring parity against the truth path.

**The Vulkan "runnable and parity-clean, not yet optimized" boundary is honest
and well-calibrated.**
Requiring correctness and row-level parity without requiring performance
optimization is the right trade-off at this stage. It prevents Vulkan from
becoming a blocking dependency on unbounded tuning work while still putting the
backend on the accepted closure surface. The proposal is explicit that this
boundary is not a compromise — it is a deliberate milestone shape. Goals 218 and
219 codify this correctly.

**The goal ladder sequencing is sound.**
Goals 215-221 follow a clean order: freeze the corrected bar, close OptiX per
workload, close Vulkan per workload, refresh benchmark/support evidence, re-audit
the whole line. No step depends on a later step, and no step is deferred
indefinitely. Goal 220 (benchmark and support-matrix refresh) correctly follows
the backend closure steps rather than preceding them.

**The three rejected alternatives are all correctly rejected.**
- Keeping CPU/Embree-only as the final bar would misrepresent the release to
  anyone reading the support matrix against the project's stated GPU purpose.
- Requiring optimized Vulkan before release would make the reopened line open-
  ended in scope and unpredictable in schedule.
- Delaying GPU work to `v0.5` would leave the first new RTDL workload family in
  a published release state that directly contradicts the project's RT-core
  identity. That contradiction would accumulate rather than resolve.

**No gaps or over-constraints are introduced by the proposal.**
The acceptance bar maps each identified gap to a specific remedy: OptiX not
running → Goals 216-217; Vulkan not running → Goals 218-219; docs claiming
CPU/Embree is sufficient → corrected by freezing the new bar in Goal 215 and
updated by the re-audit in Goal 221. The proposal does not add constraints
beyond what the project's stated identity requires.

## Summary

The proposal correctly reopens `v0.4` for the right reason: two public workloads
were closed without reaching the GPU RT-core backends that define RTDL's
purpose. The correction is proportionate — OptiX required, Vulkan correctness-
required, Vulkan optimization explicitly deferred — and the goal ladder that
implements it is complete and correctly sequenced. This is the right rework
proposal for `v0.4` under the clarified project bar.
