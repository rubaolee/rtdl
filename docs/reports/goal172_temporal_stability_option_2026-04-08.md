# Goal 172 Report: Temporal Stability Option

## Result

Goal 172 succeeded.

The orbiting-star demo now supports an optional deterministic temporal blend
step via:

- `temporal_blend_alpha`

The blend is applied as a post-process over already-rendered frame files. This
keeps the RTDL query surface unchanged while giving the visual-demo line a
bounded tool for reducing abrupt dark/light pops between adjacent frames.

## Implementation

- main file:
  - [rtdl_orbiting_star_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/rtdl_orbiting_star_ball_demo.py)
- focused tests:
  - [goal166_orbiting_star_ball_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py)

Key properties:

- default remains unchanged:
  - `temporal_blend_alpha = 0.0`
- the blend is deterministic
- the first frame is preserved
- later frames are blended against the previous output frame

## Verification

- `python3 -m compileall examples/rtdl_orbiting_star_ball_demo.py tests/goal166_orbiting_star_ball_demo_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
  - `Ran 19 tests`
  - `OK`
  - `4 skipped`

## Preview Artifact

- [summary.json](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/summary.json)
- [frame_000.png](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/frame_000.png)
- [frame_001.png](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/frame_001.png)
- [frame_005.png](/Users/rl2025/rtdl_python_only/build/goal172_temporal_blend_preview/frame_005.png)

Preview facts:

- backend:
  - `cpu_python_reference`
- size:
  - `96 x 96`
- frames:
  - `6`
- mesh:
  - `16 x 32`
- `temporal_blend_alpha`:
  - `0.2`
- `query_share`:
  - `0.550872244096217`

## Important Honesty Boundary

- This is a bounded polish option, not a claim of perfect final cinematic
  quality.
- RTDL still only owns the geometric-query work.
- The temporal blend is a Python-side media post-process over finished frames.
