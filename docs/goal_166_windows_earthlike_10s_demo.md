# Goal 166: Windows Earth-like 10s Demo

## Why

The first attractive `v0.3` visual artifact should be a clean, cinematic RTDL
demo that users can understand immediately.

The earlier spinning/swirling ball line proved backend closure, but it was not
the right final user-facing composition.

This goal tightens the scene to:

- one large static dark-blue hero ball
- one moving sun-like light direction
- no visible little light ball by default
- broad day/night-style brightness sweep across the ball
- a moving light cue on the ground

and uses the powerful Windows Embree workstation as the primary render path.

## Goal

Produce a real Windows-rendered Earth-like 3D demo artifact with:

- `1024 x 1024` frames
- `240` frames
- about `10` seconds at `24 fps`
- a static hero ball
- a broad moving light sweep
- real movie packaging

while keeping the RTDL-vs-Python boundary honest.

## Scope

In scope:

- the new Earth-like orbit demo program
- focused demo tests
- Windows Embree rendering
- saved movie artifact and summary
- explicit timing comparison against the smaller Linux OptiX comparison run

Out of scope:

- claiming RTDL is now a general rendering engine
- claiming Linux OptiX is the preferred delivery path for this demo
- claiming the Python-side shading path is already fully optimized

## RTDL / Python Split

RTDL owns:

- primary ray/triangle hit queries
- shadow-ray visibility queries
- backend-heavy geometric query work

Python owns:

- scene definition
- orbit-phase sampling
- shading math
- image/frame writing
- GIF packaging

## Success Criteria

The goal is successful if:

- a real `10s` Windows movie exists
- the repo has a checked-in demo and focused tests
- the strongest path is honestly identified as Windows Embree
- the package records real timing data
- the package has `2+` AI consensus before closure
