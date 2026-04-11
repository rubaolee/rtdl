# Goal 220: v0.4 GPU Status Refresh

Date: 2026-04-10
Status: completed

## Goal

Refresh the live `v0.4` status pages so they match the reopened GPU-required bar
and the now-running nearest-neighbor GPU workload surfaces.

## Why this goal exists

Goal 215 reopened `v0.4` under a stricter rule:

- OptiX is required for the new nearest-neighbor workloads
- Vulkan must run correctly for the same workloads

Since then, the live engineering state has moved beyond the older CPU/Embree-only
story:

- `fixed_radius_neighbors` runs on CPU/oracle, Embree, OptiX, and Vulkan
- `knn_rows` runs on CPU/oracle, Embree, OptiX, and Vulkan
- Linux validation is now available for both new GPU paths
- Windows portability reruns are now green for the pre-release audit surface

The public status pages must say that honestly.

## Required outputs

- refreshed `v0.4` support matrix
- a concise live status note for readers landing in the docs after the reopened
  GPU push
- explicit statement that Vulkan is correctness-first, not yet performance-optimized

## Current honest state

- `fixed_radius_neighbors`
  - CPU/oracle: running
  - Embree: running
  - OptiX: running
  - Vulkan: running
- `knn_rows`
  - CPU/oracle: running
  - Embree: running
  - OptiX: running
  - Vulkan: running

## Remaining work after this refresh

- external review closure for the new GPU goals
- benchmark/support evidence refresh
- final re-audit under the reopened `v0.4` bar
