# Goal 181: Smooth-Camera Flagship Acceptance

## Why

The moving-light orbit demos proved RTDL can participate in real graphics workloads, but they never became acceptable flagship artifacts because of visible temporal blinking. The smooth-camera line is the first bounded replacement that is structurally aimed at the real problem:

- fixed lights
- smoother camera motion
- lower risk of hard dark/light popping

`v0.3` needs one accepted flagship visual artifact before the line can be called finished.

This package remains centered on the smooth-camera set, but the moving-star repair candidate should still be compared alongside it before the final flagship pick is locked.

## Scope

- evaluate the Windows Embree smooth-camera artifacts as the flagship `v0.3` movie candidate
- include the already-finished warm-fill movie
- include the brighter-white secondary-light variant
- include the newer pseudo-one-star brighter-hero variant
- include the true one-light variant once its Windows render is finished
- record:
  - artifact paths
  - run facts
  - known remaining limitations
- keep the acceptance language honest:
  - RTDL provides the geometric-query core
  - Python provides camera motion, shading, compositing, and media output

## Candidate Set

### Candidate A

- warm-fill smooth-camera movie:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/win_embree_smooth_camera_hd_1024_uniform_320f.mp4`

### Candidate B

- brighter-white secondary-light smooth-camera movie:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f/win_embree_smooth_camera_whitefill_hd_1024_uniform_320f.mp4`

### Candidate C

- pseudo-one-star brighter-hero smooth-camera movie:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_onestar_hd_1024_uniform_320f/win_embree_smooth_camera_onestar_hd_1024_uniform_320f.mp4`

### Candidate D

- true one-light smooth-camera movie:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f/win_embree_smooth_camera_true_onelight_hd_1024_uniform_320f.mp4`

## Success Criteria

- at least one Windows smooth-camera movie is accepted as the flagship `v0.3` visual artifact
- the decision is documented explicitly rather than implied
- the acceptance note includes run facts and known limitations
- review language stays bounded and honest

## Out of Scope

- claiming final cinematic perfection
- replacing the RTDL/Python responsibility split
- reopening backend-correctness work already closed earlier in `v0.3`
