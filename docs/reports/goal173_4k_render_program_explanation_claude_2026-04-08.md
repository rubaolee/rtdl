# Goal 173: 4K Render Program Explanation

**Date:** 2026-04-08  
**Subject:** Windows Embree 4K movie, how the program works

## Overview

The accepted Windows 4K artifact is a 320-frame, 10-second MP4 at `3840x2160`,
rendered at `32 fps` using the orbiting-star scene in
[`rtdl_orbiting_star_ball_demo.py`](/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py),
built on top of
[`rtdl_spinning_ball_3d_demo.py`](/Users/rl2025/rtdl_python_only/examples/rtdl_spinning_ball_3d_demo.py).
The render ran on `lestat@192.168.1.8` using `8` parallel jobs and took about
`4560.9` seconds of wall clock time.

RTDL supplies the geometric ray-triangle query kernel. Everything else, scene
construction, shading, frame composition, optional temporal blending, and final
media packaging, is Python code. The program is not a general rendering engine;
it is a Python-controlled animation loop that delegates BVH traversal to RTDL
and does the rest itself.

## Pipeline

1. **Mesh construction (Python)**  
   `make_uv_sphere_mesh()` builds a UV-sphere triangle mesh in pure Python. The
   mesh stays fixed across frames; the visible change comes from the light path
   and the scene composition.

2. **Camera ray generation (Python)**  
   `make_camera_rays()` emits one `rt.Ray3D` per pixel using a pinhole camera
   model. At 4K, that is `8,294,400` rays per frame.

3. **Primary hit query (RTDL / Embree)**  
   The frame renderer hands rays and triangles to the Embree backend through the
   RTDL runtime. BVH traversal returns per-ray hit counts. This is the core RTDL
   execution step for primary rays.

4. **Intersection refinement (Python)**  
   For each hit pixel, Python computes the exact sphere-ray intersection with
   `_ray_sphere_intersection()` to recover the hit point and surface normal.
   RTDL determines which rays hit; Python determines where the visible hit lies
   on the intended sphere surface.

5. **Shadow query (RTDL / Embree)**  
   Python builds shadow rays toward the orbiting light and sends them through
   the same backend path. Returned hit counts indicate whether a visible point
   is shadowed.

6. **Shading (Python)**  
   `_shade_orbit_hit()` and `_shade_pending_hits_numpy()` compute the surface
   look: Lambertian lighting, specular response, Fresnel rim, the blue body
   gradient, and the warm yellow sunlight contribution.

7. **Frame composition (Python)**  
   Python paints the background gradient, the ground shadow, the light halo, the
   sun disc overlay, and the moving ground highlight. Optional temporal blending
   can be applied after PPM frames are written.

8. **Frame export and movie packaging (Python + external tool)**  
   `_write_ppm()` writes each frame as a PPM image. The accepted MP4 is then
   assembled from those frames during a later packaging step.

## Runtime Split

| Stage | Owner | Notes |
|---|---|---|
| Scene and mesh setup | Python | Sphere mesh, light phase, frame orchestration |
| Camera ray generation | Python | One `Ray3D` per pixel |
| BVH build and primary ray traversal | RTDL (Embree) | Geometric query core |
| Shadow ray traversal | RTDL (Embree) | Same backend reused for occlusion |
| Hit-point and normal computation | Python | Analytic sphere refinement |
| Shading | Python | Scalar or NumPy-assisted pixel math |
| Frame compositing | Python | Background, halo, ground-light overlays |
| Frame export / MP4 packaging | Python + external packaging step | PPM output, then movie assembly |

The run summary is consistent with this split. For frame `0`, primary query time
is about `41.75 s`, shadow query time is about `25.63 s`, and shading time is
about `107.97 s`. Across the whole 4K run, RTDL query share is about
`13.93%` of wall time, which is consistent with RTDL serving as the
geometric-query engine while Python owns the heavier scene and media logic.

**Why Embree on Windows:**  
OptiX required an NVIDIA GPU stack not used on the Windows workstation for this
path. Vulkan was not the accepted Windows movie path. The CPU Python reference
backend is far too slow at 4K. Embree provided a correct, multi-core CPU BVH
backend that made the Windows 4K render practical.

## Known Limitation

The accepted artifact still has a visible **left-bottom dark blink** in some
frames. This is understood as a scene/light temporal artifact rather than a
codec issue or a backend correctness failure. The movie was accepted as-is with
that limitation recorded explicitly.

So the correct interpretation is:

- the 4K artifact is real and accepted
- the RTDL/Python split remains honest
- the result is useful as a `v0.3` public output
- but it is not claimed to be a perfectly polished final cinematic render
