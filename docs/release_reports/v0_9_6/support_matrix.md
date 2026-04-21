# RTDL v0.9.6 Support Matrix

Status: released as `v0.9.6`.

This matrix describes the released `v0.9.6` boundary.

For developer-facing feature selection, RTDL also maintains a
[machine-readable engine feature support contract](../../features/engine_support_matrix.md).
Every public selectable RTDL feature must have an explicit status on each
engine: `native`, `native_assisted`, `compatibility_fallback`, or
`unsupported_explicit`.

## Prepared/Prepacked Visibility-Count Surface

| Surface | CPU reference | Embree | OptiX | Vulkan | HIPRT | Apple RT |
| --- | --- | --- | --- | --- | --- | --- |
| `ray_triangle_any_hit` 2D | supported | native early-exit | native early-exit | native early-exit | native traversal-loop early-exit | MPS-prism native-assisted early-exit plus exact 2D acceptance |
| `ray_triangle_any_hit` 3D | supported | native early-exit | native early-exit | native early-exit | native traversal-loop early-exit | MPS RT nearest-intersection any-hit |
| `visibility_rows(..., backend=...)` | supported through `backend="cpu"` | dispatches through any-hit | dispatches through any-hit | dispatches through any-hit | dispatches through any-hit | dispatches through any-hit |
| prepared repeated 2D any-hit | not applicable | standard prepared row path | prepared scene plus optional prepacked rays | prepared scene plus optional prepacked rays | prepared scene | prepared scene plus optional prepacked rays |
| prepared scalar visibility count | Python reduction over rows | row output then count | prepared/prepacked scalar count path | prepared/prepacked compact rows then count | prepared 2D any-hit rows then count | prepared/prepacked scalar blocked-ray count |
| `reduce_rows` | Python helper | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows | Python helper after emitted rows |

## Backend Notes

- Embree remains the mature CPU RTDL backend.
- OptiX is the strongest GPU prepared/prepacked scalar count path in current
  evidence, but the Linux measurement host is a GTX 1070 without RT cores.
- Vulkan is a real portability backend with native any-hit and
  prepared/prepacked 2D support; measured wins require prepacked rays.
- HIPRT prepared 2D any-hit is validated on HIPRT/Orochi CUDA over NVIDIA, not
  AMD GPU hardware.
- Apple RT scalar count is fast for the prepared/prepacked 2D app contract; it
  is not evidence that full emitted-row Apple RT output beats Embree.
- `reduce_rows` remains a Python helper over emitted rows, not native backend
  reduction.

## Current Release Performance Snapshot

| Backend | Host / path | Measured path | Result |
| --- | --- | --- | --- |
| Apple RT | Apple M4 / Metal-MPS | prepared scene + prepacked 2D rays + scalar blocked-ray count | `0.00091-0.00133 s` per query for `32768` rays / `8192` triangles |
| OptiX | Linux GTX 1070 / OptiX-CUDA path | prepared scene + prepacked 2D rays + scalar count | about `0.000062-0.000075 s` versus direct around `0.00503 s` |
| HIPRT | Linux GTX 1070 / HIPRT-Orochi-CUDA path | prepared 2D any-hit rows | `0.007464495 s` versus direct `0.580084853 s` for `4096` rays / `1024` triangles |
| Vulkan | Linux GTX 1070 / Vulkan RT | prepared scene + prepacked 2D rays | `0.004496957 s` versus direct `0.008035034 s` for `4096` rays / `1024` triangles; `0.021956306 s` versus `0.028801230 s` for `32768` rays / `8192` triangles |

Allowed conclusion: prepared build-side data, prepacked probe-side data, and
reduced output contracts can make repeated visibility/count workloads faster.

Not allowed: broad speedup claims for DB, graph, one-shot calls, or full
emitted-row outputs.

## Release-Gate Evidence

- Full local discovery after release packaging: `1274` tests OK, `187` skips.
- Public command truth audit: valid, `250` commands across `14` docs.
- Public entry smoke: valid.
- Linux fresh backend gate: OptiX, Vulkan, and HIPRT build and focused tests
  pass on `lx1` / GTX 1070.
- Goal681 consensus: Codex, Claude, and Gemini Flash accepted.
- Goal683 final local gate consensus: Codex, Claude, and Gemini Flash accepted.
- Goal684 release-level flow audit consensus: Codex, Claude, and Gemini Flash
  accepted.
