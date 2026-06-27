# Goal 110 v0.2 Workload Family Critique And Rebuttal

Date: 2026-04-05
Author: Codex
Status: proposed

## Critique 1

`segment_polygon_hitcount` may still be too small and may look like a side
case.

### Rebuttal

That risk is real, but the answer is not to jump immediately to a harder and
less closable family.

Goal 110 is the *first* v0.2 closure proof.
It should optimize for:

- clean semantics
- honest backend closure
- visible user value

If RTDL cannot close `segment_polygon_hitcount` cleanly, it has not earned a
more ambitious flagship.

## Critique 2

Choosing `segment_polygon_hitcount` dodges the harder `lsi` problem.

### Rebuttal

Yes, deliberately.

Goal 110 is about scope expansion, not about reopening every hard edge from the
v0.1 RayJoin-heavy slice.

`lsi` remains valid work, but it also carries:

- float-valued output comparison
- broader parity/scalability history
- much higher risk that the first v0.2 closure turns into reopened v0.1 repair

So the rebuttal is technical first, not merely stylistic.

## Critique 3

`segment_polygon_hitcount` may not showcase RT advantage strongly enough.

### Rebuttal

The goal is not to claim immediate paper-scale superiority.

The goal is to show that RTDL can express and run a broader spatial
filter/refine workload with a coherent backend story.

That is a language/runtime proof first.

## Critique 4

Vulkan support complicates the story.

### Rebuttal

That is why Goal 110 should define:

- Embree
- OptiX

as the primary closure backends, with Vulkan only as support if useful.

## Final recommendation

Proceed with `segment_polygon_hitcount` as the Goal 110 flagship family.

If it closes cleanly, RTDL v0.2 gains a credible second workload story.
If it fails, the failure will still be informative and much easier to diagnose
than a diffuse broader family.
