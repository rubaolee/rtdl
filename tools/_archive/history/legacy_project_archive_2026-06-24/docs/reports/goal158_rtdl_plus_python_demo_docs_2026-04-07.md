# Goal 158 Report: RTDL-Plus-Python Demo Docs

## Objective

Document the new `rtdl_lit_ball_demo.py` example as a concrete RTDL-plus-Python
application, then align front-door and tutorial docs with that broader user
story.

## What Changed

Added the new demo:

- [rtdl_lit_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_lit_ball_demo.py)

Updated the following docs to mention the demo and the RTDL-plus-Python model:

- [README.md](/Users/rl2025/rtdl_python_only/README.md)
- [docs/README.md](/Users/rl2025/rtdl_python_only/docs/README.md)
- [quick_tutorial.md](/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md)
- [release_facing_examples.md](/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md)
- [v0_2_user_guide.md](/Users/rl2025/rtdl_python_only/docs/v0_2_user_guide.md)
- [rtdl_feature_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md)
- [ray_tri_hitcount feature home](/Users/rl2025/rtdl_python_only/docs/features/ray_tri_hitcount/README.md)

## Core Message

The repo should not be read only as a fixed list of named workloads. RTDL
already works well with Python user applications when the problem shape fits
the current language/runtime surface:

- RTDL handles the geometry-query core
- Python handles surrounding application logic

The lit-ball demo is the concrete small example of that pattern.

## Honesty Boundary

The docs explicitly keep these limits:

- the demo is a user-level RTDL-plus-Python application
- RTDL v0.2.0 is still a non-graphical ray-tracing system
- the demo is not a claim that RTDL v0.2.0 is a full rendering system
- the demo is a 2D lit-ball slice built from RTDL hit relationships plus Python
  post-processing

## Validation

- `python3 -m compileall examples/visual_demo/rtdl_lit_ball_demo.py`
- `PYTHONPATH=src:. python3 examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend none --width 240 --height 240 --triangles 512 --output build/rtdl_lit_ball_demo_hq.pgm`

Result:

- the demo runs successfully
- it prints ASCII output
- it writes a real `.pgm` image

## Review Plan

- Claude review required before online
- Gemini audit required before online
- then Codex consensus
