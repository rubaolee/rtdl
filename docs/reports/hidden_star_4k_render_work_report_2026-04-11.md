# RTDL 4K Hidden-Star Render Work Report

Date: 2026-04-11

## Goal

Produce a stable `4K` RTDL-backed demo video on Windows that is strong enough
to serve as a public-facing visual artifact for the project.

Accepted target:

- Earth-like blue sphere
- hidden moving stars, not visible star sprites
- RTDL used for both:
  - primary camera hit queries
  - shadow visibility queries
- final output:
  - `3840x2160`
  - `320` frames
  - `32 fps`
  - about `10` seconds

## Public Video

- YouTube: [RTDL 4K hidden-star demo](https://youtu.be/d3yJB7AmCLM)

## Final Output

Primary Windows artifact:

- `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_hidden_star_earth_4k_10s_32fps_crossed_dual_rtdl_shadow_left_small_chunked\win_embree_hidden_star_earth_3840x2160_320f_32fps_crossed_dual_hidden_rtdl_light_to_surface_chunked.mp4`

Primary run summary:

- `C:\Users\Lestat\rtdl_python_only_win\build\win_embree_hidden_star_earth_4k_10s_32fps_crossed_dual_rtdl_shadow_left_small_chunked\summary.json`

## Final Render Configuration

The completed render used:

- backend: `embree`
- resolution: `3840x2160`
- total frames: `320`
- fps: `32`
- chunk size: `32` frames
- jobs: `8`
- latitude bands: `80`
- longitude bands: `160`
- shadow mode: `rtdl_light_to_surface`
- scene: `crossed_dual_hidden`

This means the final movie is:

- one yellow hidden star moving horizontally
- one red hidden star moving vertically
- RTDL/Embree handling primary visibility and light-to-surface shadow queries
- Python handling shading, compositing, chunking, and MP4 encoding

## Design Summary

The implementation deliberately separates the work into two layers.

### 1. RTDL layer

RTDL is used as the geometry-query engine:

- generate the sphere mesh
- generate camera rays
- run ray/triangle queries for the main visible surface
- run shadow visibility rays for each light

For the accepted stable version, the shadow logic does **not** use the older
surface-to-light self-shadow construction. Instead it uses:

- `light -> surface` shadow rays

This keeps RTDL responsible for the shadow test while avoiding the unstable
self-hit behavior that caused flicker in the earlier approach.

### 2. Python layer

Python owns the application pipeline:

- scene setup
- phase progression across frames
- light motion
- background generation
- final shading/color blending
- chunk orchestration
- frame streaming into MP4

That split is intentional. RTDL is the spatial query core; Python is the app.

## Why The 4K Render Uses Chunking

The 4K job is too large to treat as one naive all-frames-in-memory render.

The chunked renderer solves that by:

- rendering `32` frames at a time
- writing per-frame temporary `.ppm` files
- streaming those frames directly into the MP4 writer
- deleting the temporary frame files after append
- preserving only:
  - the final `.mp4`
  - the top-level `summary.json`
  - the per-chunk `summary.json` files

This keeps disk and memory usage bounded while still allowing a single final
video output.

## Code Structure

### Main chunked driver

- [examples/visual_demo/render_hidden_star_chunked_video.py](../../examples/visual_demo/render_hidden_star_chunked_video.py)

Role:

- top-level 4K render driver
- manages chunk loop
- calls the stable hidden-star frame renderer for each chunk
- appends chunk frames into one MP4
- writes the top-level summary

### Main scene renderer

- [examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py](../../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)

Role:

- defines the scene
- defines both moving lights
- builds camera rays and sphere mesh
- calls RTDL backend rows
- constructs stable light-to-surface shadow rays
- shades the final pixels

### Helper geometry/render math

- [examples/visual_demo/rtdl_spinning_ball_3d_demo.py](../../examples/visual_demo/rtdl_spinning_ball_3d_demo.py)

Role:

- reusable helper layer for:
  - camera generation
  - UV sphere mesh generation
  - backend row dispatch
  - background helpers
  - image writing

## Stable Shadow Design

The most important design choice in this work is the stable shadow path.

Earlier shadow behavior had temporal instability because the shadow ray started
from the surface and could re-hit nearby mesh triangles in unstable ways.

Accepted fix:

1. RTDL finds the visible Earth surface with camera rays.
2. For each visible hit point, Python constructs one or more shadow rays from
   the light position toward that surface point.
3. RTDL/Embree checks whether any geometry blocks the ray before the target.
4. Python applies the resulting visibility to the final shading.

This kept the image stable while preserving RTDL participation in the shadow
stage.

## Performance Summary

From the saved Windows top-level summary:

- wall clock: `13398.582574999979 s`
- about `3 h 43 m 19 s`
- total RT query time: `442.6564432999876 s`
- total RT shadow query time: `4132.832507602725 s`
- total shading time: `58527.090045699966 s`

Important interpretation:

- RTDL/Embree query work is real and substantial
- total render time is still dominated by Python-hosted shading/compositing work
- this is a real RTDL-plus-Python application artifact, not a pure native
  renderer benchmark
