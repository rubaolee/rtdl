# Goal 135: System Midterm Check

## Goal

Treat current `main` as one system, not as separate `v0.1` and `v0.2`
branches, and answer four questions:

1. Do the accepted features on current `main` still work?
2. What are the real correctness and performance results on the accepted
   platforms?
3. Where does current `main` still fail as a whole-system branch?
4. Do the front-door docs match the actual live branch state?

## Acceptance

- broad local and Linux test evidence is recorded
- Linux whole-system evidence is taken from a clean checkout of current `main`
- any real code defect found by the audit is fixed before close
- correctness and performance conclusions are summarized in one report
- the front-door docs are updated if they materially lag the live branch state
- an external-review handoff is produced for Claude/Gemini plus Codex consensus

## Boundaries

- Linux is the primary validation platform
- this Mac is still treated as a limited local platform for Python reference,
  C/oracle, and Embree
- local failures caused by missing `geos_c` linkage are reported honestly as
  platform-boundary failures, not silently treated as code regressions
