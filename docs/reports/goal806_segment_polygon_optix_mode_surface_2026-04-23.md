# Goal806: Segment/Polygon OptiX Mode Surface

## Objective

Expose the existing segment/polygon native OptiX hit-count path through the
public app CLI instead of requiring users or cloud scripts to know the hidden
`RTDL_OPTIX_SEGPOLY_MODE=native` environment switch.

## Changes

- Added `--optix-mode auto|host_indexed|native` to
  `examples/rtdl_segment_polygon_hitcount.py`.
- `native` explicitly requests the experimental native custom-AABB OptiX path.
- `host_indexed` explicitly clears the native-mode environment variable during
  the call, then restores the caller's environment.
- `auto` preserves the existing default behavior.
- Updated the RTX manifest deferred segment/polygon entry to use
  `--optix-mode native` instead of an environment override.

## Boundaries

- This does not promote segment/polygon to an RTX claim candidate.
- The app still reports `host_indexed_fallback` as its OptiX performance class
  until a focused native-vs-host-indexed-vs-PostGIS correctness/performance
  gate passes.
- This only makes the experimental path explicit and replayable.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal806_segment_polygon_optix_mode_surface_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal692_optix_app_correctness_transparency_test

Result: 14 tests OK
```
