Goal 168 report

Summary

The v0.3 visual-demo line has now reached a clear current-state shape:

- the underlying bounded 3D RTDL ray/triangle demo surface is already closed on
  Linux across:
  - `embree`
  - `optix`
  - `vulkan`
- the strongest polished public-facing movie artifact is currently the Windows
  Embree `softvis` MP4
- the Python-side host path is allowed to use stronger practical tooling, such
  as NumPy, because RTDL is the geometric-query core rather than the whole
  application

Current recommended public demo

- preferred artifact:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024.mp4`
- companion preview:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024/frame_180.png`
- companion GIF:
  - `/Users/rl2025/rtdl_python_only/build/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024/win_embree_earthlike_10s_32fps_diag_numpy_softvis_1024.gif`

What is already proven

1. RTDL can serve as the heavy geometric-query engine inside a real
   application-style 3D program.
2. The bounded 3D `ray_triangle_hit_count` visual-demo path is already
   correctness-closed on Linux across:
   - `embree`
   - `optix`
   - `vulkan`
3. A polished Windows Embree public artifact exists at:
   - `1024 x 1024`
   - `320` frames
   - `32 fps`
4. The host-side visual logic can be improved with practical Python tools such
   as NumPy without changing the RTDL-vs-Python honesty boundary.

Current backend reading

- `embree`
  - strongest current polished public movie path
  - especially strong on the powerful Windows CPU workstation
- `optix`
  - part of the already-closed Linux 3D backend surface for the bounded
    ray/triangle demo line
  - still not the preferred polished movie delivery path for the current visual
    artifact
- `vulkan`
  - part of the already-closed Linux 3D backend surface for the bounded
    ray/triangle demo line
  - still correctness-first rather than a polished movie-performance flagship

Focused verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal164_spinning_ball_3d_demo_test tests.goal166_orbiting_star_ball_demo_test`
  - `Ran 16 tests`
  - `OK`

Important honesty boundary

- The recommended public movie is currently based on the Windows Embree path.
- The broader v0.3 backend target still includes:
  - `embree`
  - `optix`
  - `vulkan`
- The fact that the polished ad artifact is currently Embree-based does not
  weaken the already-closed Linux 3D backend surface.
- The `softvis` movie is the best current visual artifact, but it is still not
  claimed to be perfectly artifact-free.
