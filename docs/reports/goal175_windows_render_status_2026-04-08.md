# Goal 175 Windows Render Status

## Current State

The Goal 175 two-star 4K movie is actively rendering on the Windows workstation.

Windows host:

- `lestat@192.168.1.8`

Remote output directory:

- `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_earthlike_4k_10s_32fps_two_star_yellow_red_jobs8_foreground`

## Render Settings

- backend:
  - `embree`
- size:
  - `3840 x 2160`
- frames:
  - `320`
- jobs:
  - `8`
- scene:
  - primary yellow diagonal star
  - delayed red horizontal secondary star
  - `temporal_blend_alpha = 0.15`

## Verified Before Launch

- local compile:
  - `python3 -m compileall examples/rtdl_orbiting_star_ball_demo.py tests/goal166_orbiting_star_ball_demo_test.py`
- local tests:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal166_orbiting_star_ball_demo_test`
  - `Ran 24 tests`
  - `OK`
  - `4 skipped`
- Windows smoke:
  - `128 x 128`
  - `2` frames
  - `embree` vs `cpu_python_reference`
  - frame `0` compare:
    - `matches = true`

## Progress Signal

At the last probe during the active render:

- multiple Windows `python` workers were active
- `17` 4K PPM frames had already been written
- `summary.json` was not present yet, which is expected before final completion

## Pending Finish Steps

1. wait for the foreground Windows render session to complete
2. run the prepared MP4 packaging script on Windows:
   - `C:\Users\Lestat\win_encode_goal175_4k_mp4.py`
3. copy back:
   - MP4
   - representative PNG
   - `summary.json`
4. finalize Goal 175 docs/review/consensus and commit only the bounded slice
