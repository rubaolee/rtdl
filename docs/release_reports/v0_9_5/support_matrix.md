# RTDL v0.9.5 Support Matrix

Date: 2026-04-19

Status: released support matrix for `v0.9.5`.

## New v0.9.5 Surface

| Feature | CPU Python reference | CPU/oracle | Embree | OptiX | Vulkan | HIPRT | Apple RT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ray_triangle_any_hit` | supported | supported | native early-exit | native early-exit | compatibility projection | native early-exit | compatibility projection |
| `visibility_rows_cpu` | supported | n/a | n/a | n/a | n/a | n/a | n/a |
| `visibility_rows(..., backend=...)` | supported through `backend="cpu"` | supported | dispatches through any-hit | dispatches through any-hit | dispatches through compatibility any-hit | dispatches through any-hit | dispatches through compatibility any-hit |
| `reduce_rows` | Python helper | Python helper | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows |

## Backend Boundary

- Embree native any-hit uses `rtcOccluded1`.
- OptiX native any-hit uses `optixTerminateRay()`.
- HIPRT native any-hit uses a traversal loop that stops after the first
  accepted hit.
- Vulkan and Apple RT support the row contract by projecting existing
  hit-count rows. That is backend execution, but not native early-exit
  performance evidence.
- `reduce_rows` is not a backend primitive. It runs in Python over rows already
  emitted by RTDL kernels or standard-library helpers.

## Existing v0.9.4 Apple RT Boundary Still Applies

`v0.9.5` does not change the `v0.9.4` Apple DB/graph boundary:

- Apple geometry and nearest-neighbor slices use Apple MPS RT where supported.
- Apple DB and graph slices use Metal compute/native-assisted execution.
- Current DB and graph workloads on Apple Silicon must not be marketed as Apple
  ray-tracing-hardware traversal.

## Evidence

- Local full test: `1207 tests`, `179 skips`, `OK`.
- Linux focused backend test: `23 tests`, `2 skips`, `OK`.
- Public command truth audit: `valid: true`, `245` commands.
- Tutorial/example check after Goal644: `63 passed`, `0 failed`, `26 skipped`.
