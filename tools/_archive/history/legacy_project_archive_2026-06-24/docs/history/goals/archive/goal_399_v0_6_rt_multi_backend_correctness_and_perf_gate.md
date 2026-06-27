# Goal 399: v0.6 RT Multi-Backend Correctness And Performance Gate

## Objective

Run the first bounded integration gate across the corrected RT-kernel graph line
to establish what is already proven across:

- Python truth path
- native/oracle
- Embree
- OptiX
- Vulkan

for both opening workloads:

- `bfs`
- `triangle_count`

## Why This Goal Exists

Goals 389-398 closed the workload steps one by one. The next missing bounded
milestone is an integrated gate that states:

- which backends are row-parity clean
- which backends are only locally skipped on this machine
- which performance comparisons are honestly available now

## Required Outcome

This goal is complete only when the repo contains:

- a bounded integrated test pass across the graph backend goals
- explicit backend-availability reporting for the current machine
- explicit honesty language separating:
  - correctness already proven
  - performance evidence already measured
  - platform-specific gaps still pending

## Honesty Boundary

This goal does not claim:

- full release closure
- cross-platform GPU parity beyond the environments actually exercised
- final benchmark conclusions for OptiX or Vulkan on this macOS machine

This goal is only the first bounded multi-backend correctness/performance gate.
