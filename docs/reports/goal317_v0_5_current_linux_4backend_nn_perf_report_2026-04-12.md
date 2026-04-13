# Goal 317 Report: Current Linux 4-Backend Nearest-Neighbor Performance

Date:
- `2026-04-12`

Goal:
- consolidate the current Linux nearest-neighbor backend picture into one
  explicit four-backend report

Scope:
- Linux only
- current published/per-review-closed nearest-neighbor line
- current backend set:
  - PostGIS
  - Embree
  - Vulkan
  - OptiX

Source reports:
- `docs/reports/goal313_v0_5_linux_32768_backend_table_2026-04-12.md`
- `docs/reports/goal316_v0_5_linux_large_scale_embree_optix_vulkan_perf_2026-04-12.md`
- `docs/reports/goal314_v0_5_current_linux_nn_perf_report_2026-04-12.md`

Current same-scale Linux pair:
- sequence:
  - `2011_09_26_drive_0014_sync`
- duplicate-free frame pair:
  - query `0000000000`
  - search `0000000004`
- scale:
  - `32768 x 32768`

## Backend Roles

### PostGIS
- current role:
  - external correctness and timing anchor
- strongest use here:
  - fixed-radius and bounded-KNN 3D validation/timing with the correct
    `gist_geometry_ops_nd` broad phase
- explicit boundary:
  - full 3D `knn_rows` is reported honestly as a timing anchor
  - it is not being sold as indexed 3D KNN acceleration

### Embree
- current role:
  - accelerated CPU backend
- current read:
  - viable and parity-clean
  - materially faster than PostGIS
  - much slower than the GPU backends on the current large-scale point

### Vulkan
- current role:
  - accelerated GPU backend
- current read:
  - parity-clean at the current large-scale point
  - competitive with OptiX on fixed-radius and bounded-KNN
  - slightly slower than OptiX on the current KNN line

### OptiX
- current role:
  - fastest current Linux backend
- current read:
  - parity-clean at the current large-scale point
  - still the top backend across all three measured workloads

## Current Linux 4-Backend Table

### fixed_radius_neighbors
- PostGIS:
  - `14.218156 s`
- Embree:
  - `1.246501 s`
- Vulkan:
  - `0.057063574029598385 s`
- OptiX:
  - `0.04714724700897932 s`

### bounded_knn_rows
- PostGIS:
  - `14.293810 s`
- Embree:
  - `1.362631 s`
- Vulkan:
  - `0.2053437699796632 s`
- OptiX:
  - `0.18232789495959878 s`

### knn_rows
- PostGIS:
  - `452.598168 s`
- Embree:
  - `75.158956 s`
- Vulkan:
  - `2.3458052719943225 s`
- OptiX:
  - `2.123993885994423 s`

## Current Ordering

At the current large-scale Linux point:

### fixed_radius_neighbors
- `OptiX < Vulkan < Embree < PostGIS`

### bounded_knn_rows
- `OptiX < Vulkan < Embree < PostGIS`

### knn_rows
- `OptiX < Vulkan < Embree < PostGIS`

## Practical Read

The current Linux backend story is now clear:

- PostGIS remains useful as the external correctness/timing anchor
- Embree is the viable accelerated CPU backend
- Vulkan is a real GPU backend for the 3D point nearest-neighbor line and is
  already competitive with OptiX on two of the three measured workloads
- OptiX remains the fastest current Linux backend

Most important ratio signals at `32768`:
- fixed-radius:
  - OptiX is about `301x` faster than PostGIS
  - Vulkan is about `249x` faster than PostGIS
  - Embree is about `11.4x` faster than PostGIS
- bounded-KNN:
  - OptiX is about `78.4x` faster than PostGIS
  - Vulkan is about `69.6x` faster than PostGIS
  - Embree is about `10.5x` faster than PostGIS
- KNN:
  - OptiX is about `213x` faster than PostGIS
  - Vulkan is about `193x` faster than PostGIS
  - Embree is about `6.0x` faster than PostGIS

## Honesty Boundary

This report is a consolidation slice.

It does not claim:
- new PostGIS re-validation beyond the already closed slices
- new Windows backend performance closure
- new macOS backend performance closure
- final cross-platform backend maturity

Conclusion:
- Linux now has an explicit four-backend nearest-neighbor performance picture
- the current backend ordering is:
  - OptiX
  - Vulkan
  - Embree
  - PostGIS
