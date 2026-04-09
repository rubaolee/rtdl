# Goal 178 Smooth Camera Orbit Demo Status

## Intent

Replace the flicker-prone moving-light composition with a smoother demo shape:

- static hero sphere
- fixed key light
- fixed fill light
- camera glides across a front-side orbit arc

This keeps the RTDL boundary intact while shifting the visual motion source from lighting changes to viewpoint changes.

## Implemented Files

- `/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_smooth_camera_orbit_demo.py`
- `/Users/rl2025/rtdl_python_only/tests/goal178_smooth_camera_orbit_demo_test.py`

## Local Verification

- `python3 -m compileall examples/visual_demo/rtdl_smooth_camera_orbit_demo.py tests/goal178_smooth_camera_orbit_demo_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal178_smooth_camera_orbit_demo_test`

Result:

- `Ran 7 tests`
- `OK`
- `2 skipped`

## Local Preview

Preview artifact directory:

- `/Users/rl2025/rtdl_python_only/build/goal178_smooth_camera_orbit_preview_small`

Important preview facts:

- backend:
  - `cpu_python_reference`
- size:
  - `96 x 96`
- frames:
  - `8`
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.1`
- `camera_motion = front_arc`
- `query_share = 0.6247820427259767`

Representative preview frame:

- `/Users/rl2025/rtdl_python_only/build/goal178_smooth_camera_orbit_preview_small/frame_004.png`

## Windows Validation

Windows host:

- `lestat@192.168.1.8`

Windows focused tests:

- `py -3 -m unittest tests.goal178_smooth_camera_orbit_demo_test`

Result:

- `Ran 7 tests`
- `OK`
- `2 skipped`

Windows one-frame Embree smoke:

- backend:
  - `embree`
- size:
  - `64 x 64`
- frames:
  - `1`
- `jobs = 12`
- output:
  - `C:\Users\Lestat\rtdl_python_only_win\build\goal178_windows_smooth_diag`

Important smoke facts:

- `camera_motion = front_arc`
- `query_share = 0.43778877592369203`
- wall clock:
  - `0.9263188999902923 s`

## Finished Windows Artifact

Windows production output directory:

- `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_smooth_camera_hd_1024_uniform_320f`

Copied-back local artifact directory:

- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f`

Final settings:

- backend:
  - `embree`
- size:
  - `1024 x 1024`
- frames:
  - `320`
- jobs:
  - `12`
- `phase_mode = uniform`
- `temporal_blend_alpha = 0.10`

Finished local files:

- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/win_embree_smooth_camera_hd_1024_uniform_320f.mp4`
- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/frame_160.png`
- `/Users/rl2025/rtdl_python_only/build/win_embree_smooth_camera_hd_1024_uniform_320f/summary.json`

Finished run facts:

- final frames:
  - `320`
- raw checkpoint frames:
  - `320`
- wall clock:
  - `1439.1826636000042 s`
- `query_share = 0.34155148723036616`

So the Windows Embree HD smooth-camera movie is finished and copied back locally.

## Honesty Boundary

- this is an application-side visual refinement
- RTDL still owns the heavy geometric-query work
- Python still owns motion, scene setup, shading, and media output
- the goal is to reduce temporal instability by changing the demo composition, not by claiming RTDL is a full renderer
