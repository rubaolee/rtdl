# Goal 314 Report: Current Linux Nearest-Neighbor Performance

Date: 2026-04-12
Status: implemented locally, pending saved external review

## Purpose

Summarize the current Linux nearest-neighbor performance state for the `v0.5`
line after the current large-scale backend tests are complete.

## Scope

Platform:
- Linux only
- host: `lestat-lx1`

Current backend picture covered here:
- PostGIS
- native CPU/oracle
- Embree
- OptiX

Workload line:
- 3D point nearest-neighbor workloads on KITTI-derived point packages
- `fixed_radius_neighbors`
- `bounded_knn_rows`
- `knn_rows`

## Source Reports

This consolidated report is derived from the already closed performance slices:

- `docs/reports/goal310_v0_5_linux_large_scale_embree_nn_perf_2026-04-12.md`
- `docs/reports/goal312_v0_5_linux_large_scale_native_embree_optix_perf_2026-04-12.md`
- `docs/reports/goal313_v0_5_linux_32768_backend_table_2026-04-12.md`

## Backend Roles

### PostGIS

Current role:
- external correctness and timing anchor

Strength:
- technically coherent 3D external baseline
- fixed-radius and bounded-KNN use the correct `gist_geometry_ops_nd` broad
  phase

Boundary:
- full 3D `knn_rows` is not being claimed as indexed 3D KNN acceleration
- PostGIS is not the target production runtime for this line

### Native CPU/Oracle

Current role:
- truth-preserving CPU baseline

Strength:
- parity anchor for RTDL backend bring-up
- full 3D nearest-neighbor surface is now closed on the CPU/oracle path

Boundary:
- not the target high-performance backend

### Embree

Current role:
- accelerated CPU backend

Strength:
- materially faster than the CPU/oracle baseline for the Linux large-scale
  fixed-radius and bounded-KNN workloads
- substantially faster than PostGIS at `32768`

Boundary:
- still much slower than OptiX on the current large-scale Linux line
- KNN required a real optimization pass before it became acceptable

### OptiX

Current role:
- accelerated GPU backend

Strength:
- fastest measured backend on the current Linux nearest-neighbor line
- parity-clean at the current published large-scale points

Boundary:
- Linux is the current validated OptiX platform
- this report does not claim Windows or broader cross-platform OptiX maturity

### Vulkan

Current role:
- not part of the current honest 3D point nearest-neighbor performance story

Boundary:
- Vulkan is still excluded from these performance claims because the current
  Vulkan path does not yet honestly support the 3D point nearest-neighbor line

## Most Important Results

### First Large-Scale Linux Embree Result at 16384

From Goal 310:

- `fixed_radius_neighbors`
  - native `0.456193 s`
  - Embree `0.144591 s`
- `bounded_knn_rows`
  - native `0.478540 s`
  - Embree `0.224777 s`
- `knn_rows`
  - native `13.604190 s`
  - Embree `18.862430 s`

Meaning:
- Embree is already stronger than native CPU/oracle for:
  - fixed-radius
  - bounded-KNN
- Embree KNN needed a backend optimization before this line became usable

### First Three-Backend Linux Result at 16384

From Goal 312:

- `fixed_radius_neighbors`
  - native `0.499760 s`
  - Embree `0.155707 s`
  - OptiX `0.021086 s`
- `bounded_knn_rows`
  - native `0.524166 s`
  - Embree `0.242003 s`
  - OptiX `0.110671 s`
- `knn_rows`
  - native `13.606308 s`
  - Embree `18.833467 s`
  - OptiX `0.131348 s`

Meaning:
- OptiX is already the fastest backend on all three workloads at `16384`
- OptiX parity was preserved after the host-side exact re-sort and rank repair

### Current Same-Scale Linux Backend Table at 32768

From Goal 313:

- `fixed_radius_neighbors`
  - PostGIS `14.218156 s`
  - Embree `1.246501 s`
  - OptiX `0.047735 s`
- `bounded_knn_rows`
  - PostGIS `14.293810 s`
  - Embree `1.362631 s`
  - OptiX `0.190078 s`
- `knn_rows`
  - PostGIS `452.598168 s`
  - Embree `75.158956 s`
  - OptiX `2.063342 s`

Meaning:
- OptiX is overwhelmingly fastest on the current `32768` Linux line
- Embree is the viable accelerated CPU backend
- PostGIS remains useful as an external anchor, but it is not competitive at
  this scale

## Current Honest Read

The Linux nearest-neighbor backend story is now clear:

- correctness:
  - RTDL is on solid ground against the external anchors already closed in the
    earlier parity line
- CPU acceleration:
  - Embree is a real accelerated backend, especially for fixed-radius and
    bounded-KNN
- GPU acceleration:
  - OptiX is the leading backend on the current Linux large-scale line
- external database anchor:
  - PostGIS remains technically useful, but performance is far behind the
    optimized RTDL backends at the current large-scale point

## Current Performance Ranking

At the current largest published same-scale point (`32768`):

For `fixed_radius_neighbors`:
- `OptiX < Embree < PostGIS`

For `bounded_knn_rows`:
- `OptiX < Embree < PostGIS`

For `knn_rows`:
- `OptiX < Embree < PostGIS`

## Next Correct Move

The next performance work should not be more Linux-only proof at the same
point.

The higher-value next move is:
- extend the accelerated backend performance line onto the next required
  platform, starting with Windows, while keeping the Vulkan boundary honest

## Honesty Boundary

This report summarizes the current Linux nearest-neighbor performance state.

It does not claim:
- Windows large-scale backend closure
- macOS large-scale backend closure
- Vulkan 3D point nearest-neighbor support
- final cross-platform backend maturity
