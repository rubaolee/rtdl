# Goal651 Apple RT 3D Any-Hit Native-Assisted Path

Date: 2026-04-20

## Goal

Improve Apple RT any-hit support after Goal650 by adding a real Apple MPS RT
3D any-hit path where the Apple API naturally supports it, while keeping Apple
RT 2D honestly scoped as compatibility until a dedicated 2D early-exit path is
implemented and measured.

## Implementation

- Added native Apple row ABI:
  - `RtdlRayAnyHitRow { ray_id, any_hit }`
- Added exported Apple C ABI:
  - `rtdl_apple_rt_run_ray_anyhit_3d(...)`
- Implemented 3D any-hit through Apple `MPSRayIntersector`:
  - builds an `MPSTriangleAccelerationStructure`;
  - runs `MPSIntersectionTypeNearest`;
  - emits one `{ray_id, any_hit}` row per input ray;
  - treats nearest-hit existence as any-hit truth instead of counting all hits.
- The new one-shot 3D any-hit path autoreleases its owned Metal/MPS objects
  under the local `@autoreleasepool`; older Apple RT functions still use the
  pre-existing broader manual-retain pattern and should be handled separately.
- Updated Python dispatch:
  - `ray_triangle_any_hit_apple_rt(...)` uses
    `rtdl_apple_rt_run_ray_anyhit_3d` for 3D when the loaded library exports it;
  - stale libraries or 2D shapes keep the existing hit-count projection path.

## Boundary

- This is native-assisted Apple MPS RT 3D any-hit, not programmable
  shader-level any-hit like OptiX/Vulkan.
- Apple RT 2D any-hit is still compatibility dispatch by projecting
  `ray_triangle_hit_count` to `any_hit`.
- No broad Apple performance claim is made.

## Verification

Commands run from `/Users/rl2025/rtdl_python_only`:

```bash
make build-apple-rt
nm -gU build/librtdl_apple_rt.dylib | rg 'rtdl_apple_rt_run_ray_anyhit_3d|rtdl_apple_rt_run_ray_hitcount_2d|rtdl_apple_rt_run_ray_hitcount_3d'
PYTHONPATH=src:. RTDL_APPLE_RT_LIB=$PWD/build/librtdl_apple_rt.dylib \
  python3 -m unittest \
    tests.goal636_backend_any_hit_dispatch_test \
    tests.goal651_apple_rt_3d_anyhit_native_test -v
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/vulkan_runtime.py
PYTHONPATH=src:. python3 -m unittest tests.goal506_public_entry_v08_alignment_test tests.goal515_public_command_truth_audit_test tests.goal512_public_doc_smoke_audit_test tests.goal646_public_front_page_doc_consistency_test -v
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Results:

- Apple RT build: OK.
- Exported symbol confirmed:
  - `_rtdl_apple_rt_run_ray_anyhit_3d`
  - `_rtdl_apple_rt_run_ray_hitcount_2d`
  - `_rtdl_apple_rt_run_ray_hitcount_3d`
- Apple/backend any-hit suite plus direct Goal651 native-symbol regression:
  9 tests OK, 4 skips.
- Direct Goal651 test proves the loaded Apple RT library exports
  `rtdl_apple_rt_run_ray_anyhit_3d` and that public
  `run_apple_rt(..., native_only=True)` 3D dispatch matches CPU.
- After the Objective-C object cleanup in the new path, `make build-apple-rt`
  and the same 9-test Apple any-hit suite were rerun successfully.
- Python compile: OK.
- Public doc/alignment tests: 10 tests OK.
- Public command truth audit: `valid: true`, 248 public commands across 14
  public docs.
- Full local unittest discovery after updating stale Goal505/509/510/603 checks:
  1223 tests OK, 180 skips.

## Codex Verdict

ACCEPT for Apple RT 3D. Current `main` now has Apple MPS RT 3D any-hit through
nearest-intersection existence. Apple RT 2D remains compatibility any-hit and
should be handled by a separate goal if we need native 2D early-exit.

## External Consensus

- Claude Sonnet 4.6 review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal651_claude_review_2026-04-20.md`
  - Verdict: ACCEPT.
  - Re-reviewed after the Objective-C object cleanup patch and confirmed the
    native function, Python dispatch, docs, tests, and Metal object lifecycle.
- Gemini 2.5 Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal651_gemini_flash_review_2026-04-20.md`
  - Verdict: ACCEPT.
  - Confirmed Apple RT 3D is MPS RT-backed and Apple RT 2D is honestly scoped
    as compatibility.
