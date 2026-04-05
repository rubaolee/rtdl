# Copernicus Review: Goal 108 v0.2 Workload Scope Charter

Date: 2026-04-05
Reviewer: Copernicus
Status: complete

## Verdict

Still too soft. Better than the first roadmap, but not tight enough to prevent
scope creep or identity drift. It narrows the mess without actually closing
the loopholes.

## Criticisms

- The biggest loophole is “programmable counting/ranking kernels with real
  geometric candidate structure.” That category can justify almost anything
  with a geometric pretext.
- The classification rule is too subjective to act as a hard gate.
- Identity is still unstable if RTDL is defined more by execution mechanism
  than by a crisp problem class.
- “Additional spatial filter/refine workloads” still covers too much surface
  area if left unprioritized.
- Generate-only mode remained politically alive simply by being present in the
  charter.
- Entry criteria were necessary but not sufficient because they did not impose
  a comparative standard for scarce project time.

## Strongest Rebuttals

- Moving generate-only mode out of core scope is the right correction.
- Explicitly pushing distributed execution, exact overlay materialization, and
  unsupported AMD/Intel native backends out of scope is good.
- The insistence on one correctness boundary and one realistic backend story is
  directionally sound.
- The “choose one in-scope family and close it end-to-end” consequence is the
  right instinct if actually enforced.

## Recommendation

Do not accept the first-draft charter as final. Tighten it further by:

1. collapsing the in-scope set to one flagship family and one backup
2. narrowing or demoting the counting/ranking category
3. replacing abstract criteria with at least one hard exclusion test
4. adding explicit negative examples for gray-area novelty demos
