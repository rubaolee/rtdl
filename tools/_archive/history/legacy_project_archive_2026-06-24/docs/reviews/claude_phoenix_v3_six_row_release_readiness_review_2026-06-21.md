# Claude Review - Phoenix V3 Six-Row Release Readiness

Reviewer: Claude, via Claude CLI.

Date: 2026-06-21.

## Verdict

Bounded six-row exact-claim surface only. Release remains blocked.

Claude found the six M7-qualified rows real and reviewed, but rejected broad V3
release, broad V3-over-V2 speedup, whole-app wording, and paper-reproduction
wording.

## P0 Release Blockers

Claude identified these release blockers:

- external review remains blocked or incomplete for multiple boundary packets;
- release installer and reproducible GPU setup are not packaged;
- system Python packaging gap remains unresolved because the pod path depends
  on a rebuild virtual environment for CuPy/Numba;
- the wording gate is a first-pass scanner, not a comprehensive release
  authorization scanner;
- second-machine confirmation has not yet run a calibrated performance suite;
- the six-row surface is too narrow for an unqualified major release.

Claude also flagged Robot Collision P1 amendments as needing verification. That
specific point was based on this review request not including the final Robot
Collision packet itself. Codex verifies below that those amendments are already
applied and gate-protected.

## P1/P2 Fixes

- Verify Robot Collision triangle-count and prepared-phase disclosure
  amendments are applied.
- Resolve or waive external review blocks for negative/boundary rows such as
  RTNN, Contact Manifold, Spatial RayJoin, and M10 same-stream interpretation.
- Decide the second-machine performance strategy: calibrated subset on `lx1`,
  or explicit release waiver.
- Close or waive the system Python packaging gap with a documented runbook.
- Update `docs/performance_model.md` where body text still referred to fewer
  than six M7 rows.

## Answers To User Questions

1. Are we building V3 rather than isolated apps?

   Claude's answer: the six M7 rows use reusable generic engine contracts, but
   the broad engine has not been fundamentally transformed. The current state
   is specific-primitive speedups in OptiX-friendly shapes, parity elsewhere,
   and losses in some domains.

2. Is this real optimization beyond V2.x or just 1.01x wording?

   Claude's answer: real technical wins exist in specific rows, including AABB,
   Triangle, Robot Collision prepared phase, and grouped sum. But the same-row
   geomean remains 1.012x, so broad V3-over-V2 speedup is not supported.

3. Is V3 ready for a major release?

   Claude's answer: no. It is only a narrow scoped six-row surface, not a
   responsible major release.

4. Was this work materially necessary?

   Claude's answer: yes, the repair pass was necessary because it prevented a
   false major release and replaced broad claims with exact rows. But more row
   classification will not itself make V3 release-ready.

5. What must happen next?

   Claude's answer: installer, external review cleanup, second-machine
   performance decision, comprehensive wording scanner, and a clear V3 value
   proposition.

## What Claude Says Codex Should Tell The User

V3 is technically honest now, but not release-ready:

- six exact rows have real, reviewed, row-scoped speedup claims;
- the engine does not broadly outperform V2.14;
- user-facing release requirements are not met;
- the latest work was correct but did not turn V3 into a major release.

Next work should move from row classification to installer, reviews,
second-machine decision, scanner, and product scope.

