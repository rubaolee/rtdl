# Goal 161 Report: v0.3 Visual Demo Charter

## Decision

The first goal for `v0.3` should be a **visual demo charter** rather than
another abstract workload-selection exercise.

The motivating target is:

- a spinning triangulated ball
- two or more orbiting lights
- real image frames and/or a short clip

## Why This Is The Right First v0.3 Goal

This direction does three useful things at once:

1. it gives RTDL a user-attractive demo surface
2. it reinforces the RTDL-plus-Python application story
3. it creates a case where RTDL can honestly own the heavy geometric-query
   side of the workload

That is stronger than the current ASCII lit-ball demo, which proves
integration but does not yet make RTDL clearly dominant in runtime.

Important technical note:

- the existing demo is a 2D lit-ball slice
- the proposed v0.3 target is a 3D spinning-ball visual demo
- so the next line is not just animation polish
- it includes a real 2D-to-3D lift plus the needed query-surface decision

## Required Technical Question

The key technical question for the next implementation goal is:

- is the current `ray_tri_hitcount` surface sufficient,
- or does RTDL need a stronger public nearest-hit / hit-row query surface
  before the visual demo can be compelling?

That question should be answered before writing the larger animated demo.

## Honest Boundary

This is not a project pivot into a general rendering engine.

The intended story remains:

- RTDL = heavy geometric query core
- Python = surrounding application logic and visual output

## Proposed Next Step After This Charter

The likely immediate follow-up after Goal 161 is:

- a narrow technical evaluation/selection goal for the minimum ray-hit surface
  needed by the visual demo
