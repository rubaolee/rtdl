# Goal 223: Vulkan Harness Integration

Date: 2026-04-10
Status: in progress

## Goal

Expose Vulkan through the baseline/harness surface for the new nearest-neighbor
workloads so the reopened `v0.4` line no longer has a harness visibility gap.

## Acceptance

- `baseline_runner` accepts `backend="vulkan"`
- the Vulkan harness path is enabled for:
  - `fixed_radius_neighbors`
  - `knn_rows`
- parity is reported against the Python truth path
- unsupported workloads fail honestly with a bounded error instead of being
  silently misrouted

## Boundary

- This goal does not make Vulkan a universal harness backend for every older
  RTDL workload.
- It only closes the harness exposure gap for the reopened nearest-neighbor
  line.
