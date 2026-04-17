# Goal 215: v0.4 GPU Re-work Proposal

Date: 2026-04-10
Status: proposed

## Goal

Re-open `v0.4` under the stricter project bar that new public workloads must
reach GPU RT-core backends, not only CPU/oracle and Embree.

## Why this proposal exists

The current nearest-neighbor line closed:

- public contracts
- DSL surfaces
- Python truth paths
- native CPU/oracle
- Embree
- external baselines
- examples/docs/audits

That is a coherent workload-family closure if the release is interpreted as a
CPU-plus-Embree milestone.

It is not sufficient if `v0.4` is interpreted through RTDL's deeper project
identity:

- RTDL is supposed to exploit GPU RT cores, not only CPU traversal
- new workload families should not be considered release-closed without GPU
  support
- OptiX should be the first serious GPU closure target
- Vulkan should be runnable and parity-clean even if it is not yet optimized

## Proposed correction

Re-open `v0.4` and change the release bar to:

- `fixed_radius_neighbors`
  - CPU/oracle: required
  - Embree: required
  - OptiX: required
  - Vulkan: required to run correctly
- `knn_rows`
  - CPU/oracle: required
  - Embree: required
  - OptiX: required
  - Vulkan: required to run correctly

## Priority order

### Priority 1: OptiX closure

OptiX is top priority because it is the strongest direct RT-core backend in the
current stack and the backend that most directly satisfies the project's GPU
purpose.

Required result:

- `fixed_radius_neighbors` runs on OptiX with row parity against truth path
- `knn_rows` runs on OptiX with row parity against truth path
- release docs can honestly call OptiX part of the `v0.4` closure surface

### Priority 2: Vulkan runnable closure

Vulkan is second priority, but still part of the release bar.

Required result:

- `fixed_radius_neighbors` runs correctly on Vulkan
- `knn_rows` runs correctly on Vulkan
- row parity is proven on bounded accepted packages
- performance optimization is explicitly not required for this step

## Proposed revised goal ladder

### Goal 215

Freeze the new release bar and reopen `v0.4` honestly in docs/process.

### Goal 216

OptiX `fixed_radius_neighbors` closure:

- lowering/runtime support
- bounded parity tests
- accepted backend report

### Goal 217

OptiX `knn_rows` closure:

- lowering/runtime support
- bounded parity tests
- accepted backend report

### Goal 218

Vulkan `fixed_radius_neighbors` runnable closure:

- runnable path
- bounded parity tests
- explicit performance honesty

### Goal 219

Vulkan `knn_rows` runnable closure:

- runnable path
- bounded parity tests
- explicit performance honesty

### Goal 220

Nearest-neighbor GPU benchmark and support-matrix refresh:

- OptiX evidence
- Vulkan evidence
- revised support matrix
- revised release statement

### Goal 221

Final `v0.4` re-audit after GPU closure.

## Acceptance bar for the reopened line

`v0.4` should not be called ready again until:

- both new workloads run on OptiX
- both new workloads run on Vulkan
- row-level parity is recorded against accepted trust paths
- docs stop claiming CPU/Embree-only closure is enough
- release reports state clearly that Vulkan is correctness-first and may remain
  slower

## What this proposal rejects

### Rejected: keep CPU/oracle plus Embree as the final v0.4 bar

Reason:

- too weak for RTDL's GPU identity
- would make nearest-neighbor look like a CPU-only feature family with optional
  GPU ambition

### Rejected: require optimized Vulkan before release

Reason:

- too costly for the current reopened scope
- runnable, parity-clean Vulkan is a better milestone than blocking on
  performance tuning

### Rejected: delay GPU work to `v0.5`

Reason:

- would leave the first new workload family in a release state that conflicts
  with the project's stated RT-core purpose

## Required review questions

- Is the reopened release bar technically and strategically justified?
- Is the OptiX-first, Vulkan-second order correct?
- Is the Vulkan "runnable and parity-clean, not yet optimized" boundary honest?
- Does this proposal correct the earlier `v0.4` closure standard cleanly?
