# Goal 146: Jaccard Linux Multi-Backend Stress

## Why

The narrow Jaccard line is real in Python and native CPU, but the public
backend surfaces still need a consistent Linux execution story for:

- `embree`
- `optix`
- `vulkan`

This goal is intentionally **not** a native-backend-maturity goal. It is a
wrapper-level usability and stress-consistency goal.

## Scope

For the current narrow unit-cell pathology-style Jaccard line:

- accept `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` through the
  public `run_embree`, `run_optix`, and `run_vulkan` surfaces
- route those surfaces through the accepted native CPU/oracle implementation
- reject `raw` mode on those fallback paths
- run large Linux stress rows until backend runtimes are in the multi-second
  range
- prove exact result consistency across:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`

## Not Claimed

- no native Embree Jaccard kernel
- no native OptiX Jaccard kernel
- no native Vulkan Jaccard kernel
- no prepared-path story for Jaccard here
- no RT-core maturity claim
- no PostGIS timing comparison in this goal

## Acceptance

- wrapper fallback support exists for the two Jaccard workloads in the public
  backend run surfaces
- local focused tests pass with accepted local platform skips
- focused Linux tests pass
- accepted Linux stress rows reach several seconds on the wrapper backend
  surfaces
- all accepted Linux stress rows are exactly consistent with the Python truth
  row
- the final report keeps the fallback boundary explicit
