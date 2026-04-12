# Goal 256: Hidden-Star 4K Artifact Integration

Date: 2026-04-11

## Purpose

Integrate the new Windows-produced hidden-star `4K` artifact into the live
`v0.4.0` repo and public surfaces.

## Imported Source

Windows desktop workpack:

- `C:\Users\Lestat\Desktop\rtdl_4k_hidden_star_workpack_2026-04-11`

Imported source files examined:

- `docs/reports/hidden_star_4k_render_work_report_2026-04-11.md`
- `examples/render_hidden_star_chunked_video.py`
- `examples/rtdl_hidden_star_stable_ball_demo.py`
- `examples/rtdl_spinning_ball_3d_demo.py`

## Code Integrated

Merged into live repo:

- [examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py](../../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
  - added `crossed_dual_hidden` scene support
  - added second moving red light
  - extended shading to multiple lights
  - batched shadow rays for larger renders
  - added frame-offset / phase-offset controls for chunk orchestration
- [examples/visual_demo/rtdl_spinning_ball_3d_demo.py](../../examples/visual_demo/rtdl_spinning_ball_3d_demo.py)
  - small `memoryview(...)` write-path optimization for `.ppm` output
- [examples/visual_demo/render_hidden_star_chunked_video.py](../../examples/visual_demo/render_hidden_star_chunked_video.py)
  - new chunked `4K` driver
  - streams frames into MP4 via `imageio`
  - deletes temporary frame files after append

## Public-Surface Updates

Updated to point at the new public `4K` video:

- [README.md](../../README.md)
- [docs/README.md](../README.md)
- [docs/current_milestone_qa.md](../current_milestone_qa.md)
- [docs/release_reports/v0_4/README.md](../release_reports/v0_4/README.md)
- [docs/tutorials/rendering_and_visual_demos.md](../tutorials/rendering_and_visual_demos.md)
- [examples/README.md](../../examples/README.md)

New preserved report:

- [hidden_star_4k_render_work_report_2026-04-11.md](hidden_star_4k_render_work_report_2026-04-11.md)

New public video:

- [RTDL 4K hidden-star demo](https://youtu.be/d3yJB7AmCLM)

## Dependency Update

Added to [requirements.txt](../../requirements.txt):

- `imageio>=2.37`
- `imageio-ffmpeg>=0.6`

This makes the chunked MP4 path explicit instead of relying on undeclared local
packages.

## Verification

Unit slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal168_hidden_star_stable_ball_demo_test tests.goal256_hidden_star_4k_workpack_test`
- `Ran 11 tests`
- `OK (skipped=2)`

Direct hidden-star smoke:

- `PYTHONPATH=src:. python3 examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py --backend cpu_python_reference --compare-backend none --width 20 --height 20 --latitude-bands 6 --longitude-bands 12 --frames 2 --jobs 1 --shadow-mode rtdl_light_to_surface --scene crossed_dual_hidden --output-dir build/goal256_hidden_star_smoke`
- passed

Direct chunked-video smoke in isolated venv:

- `python3 -m venv build/goal256_venv`
- `source build/goal256_venv/bin/activate`
- `python -m pip install -r requirements.txt`
- `PYTHONPATH=src:. python examples/visual_demo/render_hidden_star_chunked_video.py --backend cpu_python_reference --compare-backend none --width 20 --height 20 --latitude-bands 6 --longitude-bands 12 --frames 3 --chunk-frames 2 --jobs 1 --fps 32 --shadow-mode rtdl_light_to_surface --scene crossed_dual_hidden --output-dir build/goal256_chunked_smoke`
- passed

## Honest Boundary

- this integrates a real public-facing `4K` demo artifact into `v0.4.0`
- it does **not** change the core released workload catalog
- the demo remains an RTDL-plus-Python application artifact, not a renderer
  claim
- the full `4K` render evidence is Windows/Embree-based, not a cross-backend
  movie benchmark
