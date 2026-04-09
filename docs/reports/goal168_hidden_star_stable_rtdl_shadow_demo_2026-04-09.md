# Goal 168 Hidden-Star Stable RTDL-Shadow Demo

## Summary

This document describes the design, implementation, outputs, and measured behavior of the stable hidden-star Earth animation demo built on top of RTDL + Embree on Windows.

The final accepted version keeps RTDL in both geometry passes:

- primary camera visibility: RTDL `ray-triangle` query over the Earth triangle mesh
- shadow visibility: RTDL `ray-triangle` query using light-to-surface visibility rays

The accepted result is:

- visually stable
- free of the late-frame left-side blinking observed in the original user-facing demo
- identical in output quality to the analytic-lighting stable baseline for this single convex Earth sphere scene
- more representative of RTDL usage because RTDL participates in the shadow stage as well as the primary camera-hit stage

## User Goal

The user wanted a real RTDL-user demo, not a backend-only microbenchmark:

- Earth is a blue sphere in dark space
- Earth does not spin
- a bright yellow star moves behind Earth from the viewer's right to the viewer's left
- the star itself is not visible
- only the illuminated area on Earth should move across the surface
- output target: `10` seconds, `32 fps`

The user also wanted the final retained version to use RTDL for the shadow part when possible.

## Starting Point

The original public example used for this effort was:

- `examples/visual_demo/rtdl_orbiting_star_ball_demo.py`

That example already demonstrated a 3D mesh + ray-query workflow:

- generate camera rays
- build a UV sphere mesh
- run RTDL + Embree for camera-ray hit queries
- generate shadow rays from surface hit points
- run RTDL + Embree again for shadow visibility
- shade and encode frames in Python

To support the user's requested scene, this work first added a user-facing single-light option to the orbiting-star example so the star could be hidden and treated as a single moving light source instead of the original paired-light layout.

## Problem in the Original Shadow Path

The original hidden-star render produced a severe late-frame blinking artifact on the left side of the Earth.

Observed behavior:

- the artifact was visible in the source `.ppm` frames, not only in the encoded `.mp4`
- the blinking was strongest near the end of the clip, when the moving light approached the left limb of the Earth
- the Earth silhouette itself remained stable
- the unstable region was the illuminated / shadowed surface band

Interpretation:

- the primary camera-hit query appeared stable
- the unstable stage was the shadow/self-occlusion path
- the previous approach launched shadow rays from the surface hit point toward the light
- for a triangle-mesh sphere, this surface-origin shadow construction is sensitive to self-hit behavior, local mesh adjacency, and grazing-angle visibility tests

This means the visible bug was not best explained as "RTDL cannot do rendering" or "Embree is broken." It was better explained as an unstable user-side construction of shadow semantics on top of a working RTDL `ray-triangle` query kernel.

## Stable Analytic Baseline

Before restoring RTDL to the shadow pass, a stable user-side baseline was created:

- `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py`

Initial mode:

- RTDL / Embree remained responsible for primary camera-ray hits
- the unstable shadow-ray stage was removed
- lighting was computed analytically in Python from:
  - hit-point normal
  - view direction
  - moving light direction

This produced a stable video and demonstrated that the late-frame blinking was not caused by the primary RTDL camera-hit path.

However, this baseline did not satisfy the stronger "RTDL does the shadow part too" goal.

## Accepted Final Design

The accepted design keeps the current RTDL `ray-triangle` kernel and changes only how the shadow query is constructed.

### Core Idea

Do not shoot shadow rays from the surface point to the light.

Instead:

- compute the visible surface hit point `P` from the primary camera pass
- for light-facing surface points only, construct a shadow ray from the light position `L` toward `P`
- clamp `tmax` to stop just before `P`
- interpret any hit before `P` as occlusion

This is the final accepted `shadow_mode`:

- `rtdl_light_to_surface`

### Why This Works

For the current scene:

- there is one convex Earth sphere
- the only shadowing geometry is the Earth mesh itself

The light-to-surface construction removes the unstable part of the original scheme:

- the ray origin is no longer on the Earth surface
- therefore there is no immediate "surface re-hit" ambiguity at the start of the ray
- the query becomes a straightforward visibility question:
  - does any Earth triangle intersect the segment from `L` to `P` before `P`?

This is exactly the kind of question the current RTDL `ray-triangle` hit-count kernel can answer without modification.

## Design Constraints

This work intentionally preserved the current RTDL kernel:

- no new RTDL kernel was introduced
- no OptiX/Vulkan/Embree backend code was changed
- no RTDL DSL semantics were changed

The work was done strictly at the user/demo layer:

- geometry setup in Python
- RTDL input generation in Python
- output interpretation in Python

This was important because the user explicitly wanted to understand what a real RTDL user can do with the current implementation.

## Implementation Details

### Kernel Used

The same RTDL kernel continues to power both geometry passes:

- `examples/visual_demo/rtdl_spinning_ball_3d_demo.py`
- kernel: `ray_triangle_hitcount_3d_demo()`

That kernel is a generic ray-vs-triangle hit-count query:

- input rays
- input triangles
- traverse with BVH
- refine with approximate ray-triangle hit counting
- emit `ray_id` and `hit_count`

### New Demo File

The stable hidden-star implementation lives in:

- `examples/rtdl_hidden_star_stable_ball_demo.py`

Key logic in that file:

- `_frame_light(phase)`
  - defines the hidden star motion from viewer-right to viewer-left
- `_stable_shade_hit(...)`
  - computes the visible Earth color from the surface normal, view direction, and light direction
- `_light_facing_visibility(...)`
  - checks whether a surface point is light-facing before creating an RTDL shadow ray
- `_make_light_to_surface_shadow_ray(...)`
  - creates the final accepted RTDL shadow ray from the light to the surface hit point
- `_render_stable_frame(...)`
  - runs per-frame light placement
  - optionally launches the second RTDL shadow query
  - shades the image
- `render_hidden_star_stable_ball_frames(...)`
  - top-level render driver
  - supports:
    - `shadow_mode="analytic"`
    - `shadow_mode="rtdl_light_to_surface"`

### Shadow Optimization

The final implementation does not generate RTDL shadow rays for every visible pixel.

Instead it first computes whether the surface point is front-facing to the light:

- if `normal · light_dir <= 0`, the point is definitely dark and no shadow ray is needed
- if `normal · light_dir > 0`, a shadow visibility ray is generated

This avoids wasting the second RTDL pass on points that are geometrically guaranteed to be unlit.

### Tests

Focused tests were added in:

- `examples/goal168_hidden_star_stable_ball_demo_test.py`

They verify:

- the hidden star moves right-to-left
- the analytic mode emits zero shadow rays
- the RTDL-shadow mode emits nonzero shadow rays
- both modes write valid frame outputs and persist summary metadata

## Why the Final RTDL-Shadow Video Matches the Analytic Video

The final accepted RTDL-shadow output is visually identical to the analytic stable output.

This is expected for the current scene.

Reason:

- the Earth is a single convex sphere
- for a convex sphere:
  - if a point is front-facing to the light, the segment from light to point is unobstructed
  - if a point is back-facing, it is unlit without needing explicit occlusion from separate geometry

Therefore, in this exact scene, the RTDL shadow pass serves as a geometric confirmation of the analytic result rather than adding new visible structure.

This is still useful because:

- it demonstrates a stable RTDL shadow workflow
- it keeps RTDL in the shadow path
- it will generalize to more complex scenes with actual occluding geometry

## Performance Results

### 256x256 Accepted Comparison

Analytic stable baseline:

- output:
  - `build/win_embree_hidden_star_earth_256_10s_32fps_user_stable_analytic_compare`
- `shadow_mode = analytic`
- total wall clock:
  - `51.30369870000868 s`
- total primary RTDL query:
  - `0.6211602999828756 s`
- total shadow RTDL query:
  - `0.0 s`

Accepted RTDL-shadow version:

- output:
  - `build/win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow`
- `shadow_mode = rtdl_light_to_surface`
- total wall clock:
  - `65.93256990000373 s`
- total primary RTDL query:
  - `0.5894302999950014 s`
- total shadow RTDL query:
  - `181.25928710013977 s`

Difference:

- wall-clock increase:
  - `14.628871199995046 s`
- wall-clock ratio:
  - `1.2851426226700604x`
- roughly:
  - `28.5%` slower than the analytic-shadow baseline

Per-frame shadow cost at 256:

- average shadow query time:
  - `0.5664352721879368 s / frame`
- average shadow rays:
  - roughly `30k–31k / frame`

### 1024x1024 HD Accepted Render

HD output:

- `build/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow`

Measured result:

- `1024x1024`
- `320` frames
- total wall clock:
  - `939.6691023999883 s`
- total primary RTDL query:
  - `7.001239000004716 s`
- total shadow RTDL query:
  - `2294.6646096999175 s`
- total shading:
  - `18668.016605800047 s`

Average per-frame HD shadow query cost:

- `2294.6646096999175 / 320`
- about `7.17 s / frame`

Average per-frame HD shadow-ray count:

- roughly `481k–507k / frame`

## Stability Result

The final stability check showed:

- the RTDL-shadow frames are byte-for-byte identical to the analytic frames at `256x256`
- the late-frame left-side brightness progression is smooth
- the large left-side flicker from the original surface-origin shadow construction is gone

This confirms that the accepted fix is stable for the target scene.

## Files Produced by This Work

### Source Files

- `examples/rtdl_orbiting_star_ball_demo.py`
  - user-facing single-light support added earlier in the effort
- `examples/goal166_orbiting_star_ball_demo_test.py`
  - focused single-light test added earlier in the effort
- `examples/rtdl_hidden_star_stable_ball_demo.py`
  - final stable hidden-star implementation
- `examples/goal168_hidden_star_stable_ball_demo_test.py`
  - focused tests for analytic and RTDL-shadow stable modes

### Accepted 256 Outputs

- `build/win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow/summary.json`
- `build/win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow/win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow.mp4`

### HD 1024 Outputs

- `build/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow/summary.json`
- `build/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow.mp4`

## Recommended Copy Set for the Main Repo

If another machine is going to import this work into the main repo, the minimum recommended copy set is:

1. source
   - `examples/rtdl_hidden_star_stable_ball_demo.py`
   - `examples/goal168_hidden_star_stable_ball_demo_test.py`

2. this report
   - `docs/reports/goal168_hidden_star_stable_rtdl_shadow_demo_2026-04-09.md`

3. chosen generated artifacts
   - `build/win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow/win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow.mp4`
   - `build/win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow/summary.json`
   - `build/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow.mp4`
   - `build/win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow/summary.json`

Optional comparison artifacts:

- `build/win_embree_hidden_star_earth_256_10s_32fps_user_stable_analytic_compare/summary.json`

## Reproduction Commands

### Tests

```powershell
$env:PYTHONPATH='src;.'
python -m unittest examples.goal168_hidden_star_stable_ball_demo_test
```

### Accepted 256 RTDL-Shadow Render

```powershell
python examples\rtdl_hidden_star_stable_ball_demo.py `
  --backend embree `
  --compare-backend none `
  --width 256 `
  --height 256 `
  --frames 320 `
  --jobs 32 `
  --latitude-bands 80 `
  --longitude-bands 160 `
  --shadow-mode rtdl_light_to_surface `
  --output-dir build\win_embree_hidden_star_earth_256_10s_32fps_user_stable_rtdl_shadow
```

### Accepted 1024 RTDL-Shadow Render

```powershell
python examples\rtdl_hidden_star_stable_ball_demo.py `
  --backend embree `
  --compare-backend none `
  --width 1024 `
  --height 1024 `
  --frames 320 `
  --jobs 32 `
  --latitude-bands 80 `
  --longitude-bands 160 `
  --shadow-mode rtdl_light_to_surface `
  --output-dir build\win_embree_hidden_star_earth_1024_10s_32fps_user_stable_rtdl_shadow
```

## Final Conclusion

This work successfully produced a stable hidden-star Earth animation that:

- uses RTDL + Embree for the primary camera-hit pass
- uses RTDL + Embree for the shadow visibility pass
- keeps the current RTDL `ray-triangle` kernel unchanged
- avoids the original blinking artifact
- preserves the same visual output as the stable analytic baseline for the current convex-sphere scene

For this specific Earth-only demo, the RTDL shadow pass is more about correct geometric participation than visual necessity. For richer scenes with true occluding geometry, the accepted light-to-surface RTDL shadow construction should remain the preferred stable design direction.
