# Goal 313 Report: Linux 32768 Backend Table on Expanded KITTI Data

Date: 2026-04-12
Status: implemented locally, Linux-measured, pending saved external review

## Purpose

Record the first same-scale Linux backend table on the expanded KITTI data
pool using the new larger `2011_09_26_drive_0014_sync` sequence.

## Scope

Platform:
- Linux only
- host: `lestat-lx1`

Dataset:
- official KITTI raw data under `/home/lestat/data/kitti_raw`
- expanded pool now includes:
  - `2011_09_26_drive_0001_sync`
  - `2011_09_26_drive_0014_sync`

Selected same-scale pair:
- sequence: `2011_09_26_drive_0014_sync`
- query frame: `0000000000`
- search frame: `0000000004`
- duplicate match count: `0`

Scale:
- `32768 x 32768`

Backends reported:
- PostGIS
- Embree
- OptiX

Workloads:
- `fixed_radius_neighbors`
- `bounded_knn_rows`
- `knn_rows`

## Implementation

Embree-versus-OptiX script:
- `scripts/goal313_kitti_embree_optix.py`

PostGIS same-package timing script:
- `scripts/goal313_kitti_postgis_from_package.py`

Saved Linux output artifacts:
- Embree/OptiX summary:
  - `/home/lestat/work/rtdl_v05_perf/build/goal313_kitti_embree_optix_32768_0014_rerun/summary.json`
- PostGIS summary:
  - `/home/lestat/work/rtdl_v05_perf/build/goal313_kitti_embree_optix_32768_0014_rerun/postgis_report.json`

## Linux Result

### fixed_radius_neighbors

- PostGIS median:
  - `14.218156 s`
- Embree hot median:
  - `1.246501 s`
- OptiX hot median:
  - `0.047735 s`
- parity at this scale:
  - Embree vs OptiX: `true`

### bounded_knn_rows

- PostGIS median:
  - `14.293810 s`
- Embree hot median:
  - `1.362631 s`
- OptiX hot median:
  - `0.190078 s`
- parity at this scale:
  - Embree vs OptiX: `true`

### knn_rows

- PostGIS median:
  - `452.598168 s`
- Embree hot median:
  - `75.158956 s`
- OptiX hot median:
  - `2.063342 s`
- parity at this scale:
  - Embree vs OptiX: `true`

## Most Important Technical Result

The first `32768` Embree-versus-OptiX KNN run was not parity-clean.

Observed boundary:
- the mismatch occurred at the `4th/5th` neighbor boundary on a near-tie case
- OptiX had already truncated to exactly `k` candidates on the GPU
- exact host-side reranking then exposed that the wrong `4th` neighbor had been
  kept

Fix applied:
- OptiX 3D KNN now requests `k + slack` candidates from the GPU
- the host re-sorts by:
  - `query_id`
  - exact `distance`
  - `neighbor_id`
- the host trims back to `k` and reassigns `neighbor_rank`

After that fix:
- the `32768` Embree-versus-OptiX `knn_rows` path became parity-clean on the
  saved `0014_sync` packages

## Honest Read

At `32768 x 32768` on the expanded KITTI pool:

- OptiX is the fastest backend on all three workloads by a large margin
- Embree remains the viable accelerated CPU backend
- PostGIS remains useful as an external timing/correctness anchor, but it is no
  longer competitive at this scale

Useful ratios from this same-scale table:
- fixed-radius:
  - Embree is about `11.4x` faster than PostGIS
  - OptiX is about `297.8x` faster than PostGIS
- bounded-KNN:
  - Embree is about `10.5x` faster than PostGIS
  - OptiX is about `75.2x` faster than PostGIS
- KNN:
  - Embree is about `6.0x` faster than PostGIS
  - OptiX is about `219.4x` faster than PostGIS

## Verification

Local syntax:
- `python3 -m py_compile scripts/goal313_kitti_embree_optix.py scripts/goal313_kitti_postgis_from_package.py`

Linux Embree/OptiX run:
- `PYTHONPATH=src:. python3 scripts/goal313_kitti_embree_optix.py /home/lestat/data/kitti_raw --point-counts 32768 --output-dir build/goal313_kitti_embree_optix_32768_0014_rerun --query-start-index 108 --max-search-offset 128 --max-frames 1 --repeats 5`

Linux PostGIS same-package run:
- `PYTHONPATH=src:. python3 scripts/goal313_kitti_postgis_from_package.py /home/lestat/work/rtdl_v05_perf/build/goal313_kitti_embree_optix_32768_0014_rerun/points_32768 --postgis-dsn "dbname=rtdl_postgis" --fixed-repeats 3 --bounded-repeats 3 --knn-repeats 1 --output build/goal313_kitti_embree_optix_32768_0014_rerun/postgis_report.json`

## Honesty Boundary

This slice closes the first same-scale `32768` backend table only.

It does not claim:
- Windows large-scale backend closure
- macOS large-scale backend closure
- Vulkan 3D point nearest-neighbor support
- final cross-platform backend maturity

Important backend boundary:
- Vulkan is not included in this table because the current Vulkan path still
  does not honestly support the 3D point nearest-neighbor line

Important correctness boundary:
- this slice directly re-proves Embree-versus-OptiX parity at `32768`
- it does not separately re-prove PostGIS row parity at `32768`
- PostGIS remains the external anchor based on the already closed smaller-scale
  3D parity line plus the same-scale timing run reported here
