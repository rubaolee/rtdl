# Goal 181 Report: Smooth-Camera Flagship Acceptance

Date: 2026-04-08

## Objective

Choose and accept the flagship Windows smooth-camera artifact for the end of the `v0.3` line.

## Why This Exists

The earlier moving-light visual-demo family had real technical value, but it failed as a flagship artifact because visible temporal blinking made it feel unstable and unprofessional. The smooth-camera line is a more credible final `v0.3` flagship candidate because it removes the worst source of that instability.

## Current Candidate A

Finished Windows Embree warm-fill smooth-camera movie:

- artifact:
  - [win_embree_smooth_camera_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/win_embree_smooth_camera_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/frame_160.png)
- summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/summary.json)

Known run facts:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `12`
- phase mode:
  - `uniform`
- wall clock:
  - `1439.1826636000042 s`
- query share:
  - `0.34155148723036616`

## Current Candidate B

Brighter-white secondary-light smooth-camera variant:

- artifact:
  - [win_embree_smooth_camera_whitefill_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f/frame_160.png)
- summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f/summary.json)

Known run facts:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `12`
- phase mode:
  - `uniform`
- wall clock:
  - `1439.6691318000085 s`
- query share:
  - `0.3440608092944337`

## Current Candidate C

Pseudo-one-star brighter-hero smooth-camera variant:

- artifact:
  - [win_embree_smooth_camera_onestar_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_onestar_hd_1024_uniform_320f/win_embree_smooth_camera_onestar_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_onestar_hd_1024_uniform_320f/frame_160.png)
- summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_onestar_hd_1024_uniform_320f/summary.json)

Known run facts:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `12`
- phase mode:
  - `uniform`
- wall clock:
  - `1419.8431366000004 s`
- query share:
  - `0.3406323188516788`

Important boundary:

- this candidate still uses `light_count = 2`
- it is not the true one-light variant the user later requested

## Current Candidate D

True one-light smooth-camera variant:

- artifact:
  - [win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4)
- preview:
  - [frame_160.png](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/frame_160.png)
- summary:
  - [summary.json](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/summary.json)

Known run facts:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `12`
- light count:
  - `1`
- phase mode:
  - `uniform`
- wall clock:
  - `1078.4306103999988 s`
- query share:
  - `0.36087708147453185`

Important boundary:

- this is the first true one-light smooth-camera candidate in the Windows comparison set
- it is the cleanest direct answer to the user's request for an actual one-light movie

## Acceptance Rule

The accepted flagship should be whichever of the smooth-camera candidates is judged better on the actual public-demo criterion:

- more stable temporally
- more intentional visually
- more intuitive visually
- still honest about remaining limitations

## Final Pick

Accepted smooth-camera flagship baseline:

- Candidate D:
  - [win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4](/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4)

Reason for acceptance:

- it is the cleanest true one-light smooth-camera artifact
- it removes the ambiguity of the pseudo-one-star variant
- it is the safest stable baseline from the smooth-camera family
- it is a better technical flagship baseline than the still-flickering moving-star repair line

Important boundary:

- the public-facing front surface now points to the preferred Shorts URL rather than directly to this local movie file
- the moving-star repair movie remains preserved for comparison, but it is not selected as the `v0.3` flagship baseline

## Honesty Boundary

The acceptance of this movie does not change the architecture claim:

- RTDL:
  - geometric-query core
- Python:
  - camera motion
  - lighting composition
  - shading
  - image/video packaging
