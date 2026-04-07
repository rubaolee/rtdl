# Goal 146 Jaccard Linux Multi-Backend Stress

## Verdict

Goal 146 is accepted as a **wrapper-level Linux stress and consistency**
package for the narrow Jaccard line.

This goal does **not** close native Embree/OptiX/Vulkan Jaccard support.

## What Changed

Runtime wrapper fallback was added in:

- [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py)
- [optix_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py)
- [vulkan_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py)

New Linux stress code:

- [goal146_jaccard_linux_stress.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal146_jaccard_linux_stress.py)
- [goal146_jaccard_linux_stress.py](/Users/rl2025/rtdl_python_only/scripts/goal146_jaccard_linux_stress.py)

Focused tests:

- [goal146_jaccard_backend_surface_test.py](/Users/rl2025/rtdl_python_only/tests/goal146_jaccard_backend_surface_test.py)

Artifacts:

- [summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal146_jaccard_linux_stress_artifacts_2026-04-07/summary.json)
- [summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal146_jaccard_linux_stress_artifacts_2026-04-07/summary.md)

## Boundary

Accepted claim:

- `embree`, `optix`, and `vulkan` now participate in the public run-surface
  matrix for the Jaccard workloads through documented native CPU/oracle
  fallback

Not claimed:

- native backend-specific Jaccard kernels
- RT-core acceleration
- prepared-path support
- backend-performance competition for native Jaccard execution

## Validation

Local Mac:

- `python3 -m compileall src/rtdsl/goal146_jaccard_linux_stress.py scripts/goal146_jaccard_linux_stress.py`
  - `OK`
- `PYTHONPATH=src:. python3 -m unittest tests.goal146_jaccard_backend_surface_test tests.goal140_polygon_set_jaccard_test tests.goal138_polygon_pair_overlap_area_rows_test`
  - `13` tests, `OK`, `4` skipped
  - skipped because local `geos_c` linkage is still not a full-platform closure

Linux:

- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p "goal146_jaccard_backend_surface_test.py"`
  - `4` tests, `OK`
- `PYTHONPATH=src:. python3 -m unittest tests.goal140_polygon_set_jaccard_test tests.goal138_polygon_pair_overlap_area_rows_test`
  - `9` tests, `OK`

## Linux Stress Result

Dataset:

- source: `MoNuSeg 2018 Training Data`
- xml: `MoNuSeg 2018 Training Data/Annotations/TCGA-38-6178-01Z-00-DX1.xml`
- selected nuclei: `16`
- base left polygons after unit-cell conversion: `8556`
- base right polygons after unit-cell conversion: `8556`

Accepted rows:

- `copies=64`
  - left polygons: `547584`
  - right polygons: `547584`
  - Python: `8.279358 s`
  - CPU: `3.978596 s`
  - Embree: `3.699990 s`
  - OptiX: `3.670949 s`
  - Vulkan: `3.636281 s`
  - consistency vs Python:
    - CPU `true`
    - Embree `true`
    - OptiX `true`
    - Vulkan `true`
  - result:
    - `intersection_area=524160`
    - `left_area=547584`
    - `right_area=547584`
    - `union_area=571008`
    - `jaccard_similarity=0.917955615332885`

- `copies=128`
  - left polygons: `1095168`
  - right polygons: `1095168`
  - Python: `16.526160 s`
  - CPU: `7.673124 s`
  - Embree: `7.421700 s`
  - OptiX: `7.435530 s`
  - Vulkan: `7.400839 s`
  - consistency vs Python:
    - CPU `true`
    - Embree `true`
    - OptiX `true`
    - Vulkan `true`
  - result:
    - `intersection_area=1048320`
    - `left_area=1095168`
    - `right_area=1095168`
    - `union_area=1142016`
    - `jaccard_similarity=0.917955615332885`

## Interpretation

The goal succeeded on the terms it set:

- the public backend run surfaces now accept the narrow Jaccard workloads
- the accepted Linux rows are in the several-second range
- the aggregate result is exactly consistent across all reported backends

The runtime ordering here should not be overinterpreted. These are wrapper
execution times under documented native CPU/oracle fallback, not native Embree,
OptiX, or Vulkan Jaccard kernel timings.
