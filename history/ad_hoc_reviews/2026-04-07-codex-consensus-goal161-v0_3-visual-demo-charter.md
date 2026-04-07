# Codex Consensus: Goal 161 v0.3 Visual Demo Charter

## Decision

Approve Goal 161.

The first goal for `v0.3` should be a narrow visual-demo charter centered on a
spinning triangulated ball with orbiting lights, real image frames and/or a
short clip, and an explicit RTDL-plus-Python responsibility split.

## Why This Is Correct

- it gives `v0.3` a user-visible application story immediately
- it creates a path where RTDL can plausibly own the dominant heavy geometric
  query cost
- it stays honest about RTDL not becoming a general rendering engine
- it properly identifies the open technical question:
  `ray_tri_hitcount` may be insufficient, so a stronger nearest-hit or hit-row
  surface may be needed

## Bounded Conclusion

Goal 161 is not an implementation claim. It is the correct charter for the
first `v0.3` line.

The right immediate follow-up after this charter is a focused technical
selection/evaluation goal for the minimum public ray-hit surface required by
the planned visual demo.
