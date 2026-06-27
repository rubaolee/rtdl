# Claude Review - Phoenix V3 RTNN Ranked-Summary Wall-Time Boundary

Reviewer: Claude, via Claude CLI.

Date: 2026-06-21.

## Verdict

Approve with required fixes. No P0 blockers.

The boundary packet is structurally sound: all claim flags are false, the
Markdown and JSON packet agree, the underlying intake already has 2-AI
consensus, and the `3.333x` hot metric is not presented as an end-to-end RTNN
speedup.

## P1 Required Fix

The tutorial table must make wall-ratio inversion explicit. A first-time reader
could see `0.316x` and understand only that OptiX is slower, without realizing
that it means OptiX takes about `3.16x` as long as Embree wall-to-wall.

Required tutorial fix:

```text
Wall ratios: 0.316x means OptiX takes 3.16x as long as Embree wall-to-wall.
```

Equivalent inverse annotations are acceptable.

## P2 Suggestions

- Add one mechanistic sentence explaining that OptiX wins the isolated query
  slice but surrounding overhead dominates wall time at this scale.
- Explain that materialized summary rows keep this from being an in-device or
  zero-copy baseline.
- Make paper-equivalent non-claims visible in the tutorial, not only in the
  boundary packet.

## Answers

1. It is fair to teach this as a `ranked_summary` boundary lesson.
2. Wall ratios below 1.0 were technically stated, but the magnitude needed the
   P1 inverse annotation.
3. The tutorial prevents readers from treating `3.333x` as end-to-end speedup
   because hot and wall columns are adjacent and forbidden wording is explicit.
4. Universal RTNN overclaims are blocked; paper-equivalent context needed a
   tutorial-level guard.
5. Claude approves it as a rebuild tutorial boundary, not as M7, after the P1
   tutorial fix.
