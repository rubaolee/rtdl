# Goal 316 Report: Linux Large-Scale Embree vs OptiX vs Vulkan Performance

Date:
- `2026-04-12`

Goal:
- add Vulkan to the current large-scale Linux accelerated backend table

Scope:
- Linux only
- real KITTI data
- accelerated backend comparison only:
  - Embree
  - OptiX
  - Vulkan

Dataset and pair:
- source root:
  - `/home/lestat/data/kitti_raw`
- sequence:
  - `2011_09_26_drive_0014_sync`
- duplicate-free pair:
  - query frame `0000000000`
  - search frame `0000000004`
- point count:
  - `32768 x 32768`
- duplicate match count:
  - `0`

Benchmark driver:
- `scripts/goal316_kitti_embree_optix_vulkan.py`

Linux probe workspace:
- `/home/lestat/work/rtdl_v05_vulkan_probe`

Pinned backend libraries during the clean rerun:
- `RTDL_EMBREE_LIB=/home/lestat/work/rtdl_v05_vulkan_probe/build/librtdl_embree.so`
- `RTDL_OPTIX_LIB=/home/lestat/work/rtdl_v05_perf/build/librtdl_optix.so`
- `RTDL_VULKAN_LIB=/home/lestat/work/rtdl_v05_vulkan_probe/build/librtdl_vulkan.so`

Important intermediate finding:
- the first Vulkan `knn_rows` pass at `32768` was not parity-clean
- the mismatch shape was a near-tie rank boundary:
  - same query
  - same rank
  - slightly different neighbor chosen
- the fix was:
  - oversample Vulkan 3D KNN candidates with slack
  - exact-sort by `(query_id, distance, neighbor_id)` on the host
  - trim back to `k` and assign final ranks on the host
- after that repair:
  - Embree vs Vulkan parity became clean on the saved `32768` package pair

Clean rerun evidence:
- summary file:
  - `/home/lestat/work/rtdl_v05_vulkan_probe/build/goal316_kitti_embree_optix_vulkan_32768_fix2/summary.json`

Results at `32768 x 32768`, `repeats=3`:

### fixed_radius_neighbors
- Embree hot median:
  - `1.2434870510478504 s`
- OptiX hot median:
  - `0.04714724700897932 s`
- Vulkan hot median:
  - `0.057063574029598385 s`
- parity:
  - Embree vs OptiX: `true`
  - Embree vs Vulkan: `true`
  - OptiX vs Vulkan: `true`

### bounded_knn_rows
- Embree hot median:
  - `1.3748652570066042 s`
- OptiX hot median:
  - `0.18232789495959878 s`
- Vulkan hot median:
  - `0.2053437699796632 s`
- parity:
  - Embree vs OptiX: `true`
  - Embree vs Vulkan: `true`
  - OptiX vs Vulkan: `true`

### knn_rows
- Embree hot median:
  - `75.73891976498999 s`
- OptiX hot median:
  - `2.123993885994423 s`
- Vulkan hot median:
  - `2.3458052719943225 s`
- parity:
  - Embree vs OptiX: `true`
  - Embree vs Vulkan: `true`
  - OptiX vs Vulkan: `true`

Immediate read:
- OptiX remains the fastest backend on the current Linux `32768` line
- Vulkan is far faster than Embree on the current Linux `32768` line
- Vulkan is competitive with OptiX on:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
- Vulkan trails OptiX on `knn_rows`, but both are still dramatically faster
  than Embree at this scale

Speed ratios from the clean rerun:
- fixed-radius:
  - Vulkan vs Embree: about `21.8x` faster
  - OptiX vs Vulkan: about `1.2x` faster
- bounded-KNN:
  - Vulkan vs Embree: about `6.7x` faster
  - OptiX vs Vulkan: about `1.1x` faster
- KNN:
  - Vulkan vs Embree: about `32.3x` faster
  - OptiX vs Vulkan: about `1.1x` faster

Honesty boundary:
- this slice does not re-run PostGIS
- PostGIS remains the external correctness/timing anchor from the already
  closed smaller-scale and same-scale backend line
- this slice is only the accelerated Linux backend race after the Vulkan 3D
  capability closure
- this slice does not claim Windows or macOS Vulkan performance readiness

Conclusion:
- Goal 316 is technically closed pending saved review
- Linux now has a parity-clean large-scale accelerated backend table across:
  - Embree
  - OptiX
  - Vulkan
