# Goal 172: Temporal Stability Option

## Objective

Add a bounded temporal-stability option to the orbiting-star visual demo line so
the current movie path can reduce abrupt frame-to-frame lighting pops without
changing the RTDL geometric-query surface.

## Accepted Scope

- add an optional temporal post-blend step to:
  - [rtdl_orbiting_star_ball_demo.py](/Users/rl2025/rtdl_python_only/examples/visual_demo/rtdl_orbiting_star_ball_demo.py)
- keep the default behavior unchanged when the new option is disabled
- add focused tests for:
  - payload blending
  - summary persistence
  - deterministic file behavior
- produce a small preview artifact that demonstrates the option

## Out of Scope

- claiming perfect cinematic polish
- changing the RTDL backend surface
- changing the Windows MP4 recommendation yet
- any claim that the RTDL part now does image compositing or video effects

## Success Criteria

- optional `temporal_blend_alpha` exists and defaults to `0.0`
- focused tests pass
- a small preview run is saved in the repo
- external AI review is saved
- Codex consensus is saved
