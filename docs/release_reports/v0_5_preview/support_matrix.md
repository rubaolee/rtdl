# RTDL v0.5 Preview Support Matrix

Date: 2026-04-12
Status: current development-state preview, not final release sign-off

## Reading Guide

Status wording used below:

- `accepted`: part of the current honest `v0.5` preview claim surface
- `accepted, bounded`: supported under a narrower or explicitly limited
  contract
- `supporting baseline`: useful for validation/comparison, not the primary RTDL
  execution path
- `not yet closed`: not yet part of the honest current claim surface

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux | primary validation platform for the `v0.5` 3D nearest-neighbor line | accepted |
| local macOS | development, focused regression, bounded local checks | accepted, bounded |
| Windows | secondary portability/bring-up host; no current large-scale `v0.5` NN performance claim | accepted, bounded |

## Backend Roles

| Backend | Role in current `v0.5` preview | Current status |
| --- | --- | --- |
| Python reference | correctness / truth path | accepted |
| native CPU / oracle | compiled correctness baseline | accepted |
| PostGIS | external correctness and timing anchor | supporting baseline |
| Embree | accelerated CPU backend | accepted |
| OptiX | accelerated GPU backend | accepted |
| Vulkan | accelerated GPU backend | accepted, bounded |
| cuNSearch | external research comparison path with explicit duplicate/large-set boundaries | accepted, bounded |

## Current Workload Surface

| Surface | Boundary | Status |
| --- | --- | --- |
| `fixed_radius_neighbors` 2D | carried from released NN line | accepted |
| `knn_rows` 2D | carried from released NN line | accepted |
| `bounded_knn_rows` 2D | paper-fidelity RTNN extension line | accepted |
| `fixed_radius_neighbors` 3D | closed on CPU/oracle, Embree, OptiX, Vulkan; Linux-validated | accepted |
| `bounded_knn_rows` 3D | closed on CPU/oracle, Embree, OptiX, Vulkan; Linux-validated | accepted |
| `knn_rows` 3D | closed on CPU/oracle, Embree, OptiX, Vulkan; Linux-validated | accepted |

## Platform/Backend Boundary Summary

### Linux

Current honest state:
- CPU/oracle 3D NN line: closed
- PostGIS 3D anchor: closed
- Embree 3D NN line: closed
- OptiX 3D NN line: closed
- Vulkan 3D NN line: closed
- large-scale backend evidence exists through `32768 x 32768`

### local macOS

Current honest state:
- Python/oracle/Embree-focused development and regression work is real
- bounded Embree 3D nearest-neighbor correctness is verified locally against the
  RTDL truth path for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- Vulkan and OptiX are not being claimed as validated macOS `v0.5` runtime
  lines
- no large-scale macOS NN performance claim

### Windows

Current honest state:
- Windows remains a valid host for bounded portability/bring-up work
- bounded Embree 3D nearest-neighbor correctness is verified on the Windows
  probe host against the RTDL truth path for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
  - `knn_rows`
- no current `v0.5` large-scale nearest-neighbor performance claim is being
  made for Windows
- Windows is not required for the current Linux performance story

## Current Linux Backend Ordering

At the current same-scale large Linux point (`32768 x 32768`):

### `fixed_radius_neighbors`
- `OptiX < Vulkan < Embree < PostGIS`

### `bounded_knn_rows`
- `OptiX < Vulkan < Embree < PostGIS`

### `knn_rows`
- `OptiX < Vulkan < Embree < PostGIS`

## Honest Summary

- `v0.5` has moved beyond planning and now has a real 3D nearest-neighbor
  backend line on Linux
- CPU/oracle, Embree, OptiX, and Vulkan are all in the current honest Linux
  preview surface for the 3D point nearest-neighbor trio
- PostGIS remains the external correctness/timing anchor, not the target
  production runtime
- Vulkan is now part of the current Linux `v0.5` story, but its cross-platform
  maturity is still bounded
- Windows and macOS are part of the current bounded Embree correctness surface,
  but not part of the large-scale `v0.5` nearest-neighbor performance claim
  surface
