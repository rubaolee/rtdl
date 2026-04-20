# Goal650 Vulkan Native Early-Exit Any-Hit

Date: 2026-04-20

## Goal

Upgrade Vulkan `ray_triangle_any_hit` from compatibility projection
(`ray_triangle_hit_count` then `hit_count > 0`) to a native Vulkan RT any-hit
path, while keeping Apple RT honestly documented as compatibility until a
separate Apple-specific implementation exists.

## Implementation

- Added `RtdlRayAnyHitRow { ray_id, any_hit }` to the Vulkan native ABI.
- Added exported Vulkan C ABI functions:
  - `rtdl_vulkan_run_ray_anyhit(...)`
  - `rtdl_vulkan_run_ray_anyhit_3d(...)`
- Added a 2D Vulkan ray-tracing any-hit pipeline:
  - reuses the existing custom 2D triangle-AABB intersection shader;
  - uses a dedicated any-hit shader that sets `anyHit = 1`;
  - calls `terminateRayEXT` after the first accepted hit.
- Added a 3D Vulkan ray-tracing any-hit pipeline:
  - uses Vulkan native triangle geometry;
  - uses a dedicated any-hit shader that sets `anyHit = 1`;
  - calls `terminateRayEXT` after the first accepted hit.
- Updated Python Vulkan dispatch:
  - dictionary mode uses native `rtdl_vulkan_run_ray_anyhit*` symbols when
    available;
  - stale rebuilt-library fallback still projects hit-count rows to any-hit;
  - raw mode now works for native Vulkan any-hit and returns raw any-hit rows.

## Tests

Local macOS:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/vulkan_runtime.py
PYTHONPATH=src:. python3 -m unittest tests.goal636_backend_any_hit_dispatch_test tests.goal506_public_entry_v08_alignment_test tests.goal515_public_command_truth_audit_test tests.goal512_public_doc_smoke_audit_test tests.goal646_public_front_page_doc_consistency_test -v
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Results:

- Python compile: OK.
- Local combined tests: 18 tests OK, 4 skips.
- Public command truth audit: `valid: true`, 248 public commands across 14
  public docs.

Linux `lestat-lx1`:

```bash
cd /home/lestat/work/rtdl_goal650_vulkan_anyhit
make build-vulkan
PYTHONPATH=src:. RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so \
  python3 -m unittest tests.goal636_backend_any_hit_dispatch_test -v
```

Result:

- `make build-vulkan`: OK.
- Any-hit backend test suite: 8 tests OK, 4 skips.
- The Vulkan tests included:
  - 2D `ray_triangle_any_hit` dictionary mode against CPU;
  - 2D `ray_triangle_any_hit` raw native rows against CPU;
  - 3D `ray_triangle_any_hit` dictionary mode against CPU;
  - 3D `ray_triangle_any_hit` raw native rows against CPU.

## Bounded Timing Probe

Linux timing probe, 384 rays x 384 overlapping triangles, repeated in one
process after warm-up:

| Workload | Median whole-call time | First row |
| --- | ---: | --- |
| Vulkan `ray_triangle_hit_count` | 0.006942163978237659 s | `{ray_id: 0, hit_count: 384}` |
| Vulkan native `ray_triangle_any_hit` | 0.005916182999499142 s | `{ray_id: 0, any_hit: 1}` |

Interpretation:

- This is bounded evidence only.
- Whole-call time still includes Vulkan/BVH/output setup costs.
- The result is consistent with native early-exit helping dense-hit traversal,
  but it is not a broad Vulkan performance claim.

## Apple RT Boundary

Apple RT is not upgraded by this goal. It remains documented as compatibility
for any-hit:

- Apple RT can execute backend hit-count traversal and project to `any_hit`.
- This is real backend execution and correctness parity.
- It is not a native early-exit Apple RT performance claim.
- Native Apple early-exit should be a separate goal because the Metal/MPS RT
  path has different API constraints and must be validated separately for both
  2D and 3D shapes.

## Codex Verdict

ACCEPT for Vulkan. Current `main` now has a native Vulkan early-exit any-hit
path when `librtdl_vulkan` is rebuilt from current source. Apple RT remains a
separate pending backend-specific goal.

## External Consensus

- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal650_claude_review_2026-04-20.md`
  - Verdict: ACCEPT.
  - Key point: both 2D and 3D Vulkan any-hit shaders set the payload and call
    `terminateRayEXT`, so this is native early-exit rather than hit-count
    projection.
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal650_gemini_flash_review_2026-04-20.md`
  - Verdict: ACCEPT after re-run with the report content supplied directly.
  - Key point: Vulkan has dedicated native ABI functions and Apple RT is
    honestly scoped as a pending compatibility path.

Final Goal650 closure: ACCEPT by Codex + Claude + Gemini Flash.
