# Goal1664 Fresh-Student RTDL UX 3-AI Consensus

Date: 2026-05-10

Inputs:

- Codex fresh-student report:
  `docs/reports/goal1664_fresh_student_rtdl_user_experience_report_2026-05-10.md`
- Gemini external review:
  `docs/reviews/goal1664_gemini_fresh_student_ux_review_2026-05-10.md`
- Claude external review:
  `docs/reviews/goal1664_claude_fresh_student_ux_review_2026-05-10.md`

## Consensus Verdict

All three reviewers agree that RTDL is learnable from the current front door.
The README, docs index, quick tutorial, and tutorial ladder now explain the
core language model clearly enough for a fresh user to run first examples and
understand the central authoring pattern:

```text
input -> traverse -> refine -> emit
```

All three reviewers also agree that the next documentation risk is not the
language itself. The risk is secondary-entry inconsistency: app/example pages
still expose version history, goal evidence, and maintainer vocabulary too
early. This can confuse a new learner after the first clean tutorial path.

## Agreed Strengths

- The front page gives a clear product definition.
- The quick tutorial is the best first learning document.
- The first-run CPU Python reference commands work.
- The docs are appropriately conservative about GPU and whole-app performance
  claims.
- The RTDL language surface is small, bounded, and teachable.
- The Python-vs-RTDL boundary is mostly clear: Python owns app orchestration;
  RTDL owns the RT-shaped kernel/query contract.

## Agreed Problems

- `docs/app_example_quickstart.md` still contains v1.0/v1.6 transition wording
  and "proof machinery" language in a page that should feel current and
  user-facing.
- `examples/README.md` still mixes current example inventory with long release
  history and v0.x/v1.x boundary text.
- `docs/release_facing_examples.md` is useful as a command/evidence archive,
  but too historical and goal-heavy to serve as a learner page.
- `backend="rtdl"` in the kernel decorator and `--backend embree/optix/...` at
  runtime use the same word for two different concepts; this needs an early
  explanatory box.
- The distinction between `cpu_python_reference` and `cpu` is not explained
  consistently enough for first-time users.
- The golden path runs, but the documentation has not yet been tested for
  common student mistakes such as missing `PYTHONPATH`, wrong host input shape,
  or unavailable GPU backend.

## Refined Priority Fixes

1. Productize `docs/app_example_quickstart.md`.
   Keep first commands, the app table, and honest "do not claim" boundaries.
   Move version-evolution and proof-machinery text behind history/evidence
   links.

2. Productize `examples/README.md`.
   Keep a compact current inventory. Move old release-boundary material to a
   history or evidence archive.

3. Reframe `docs/release_facing_examples.md`.
   Label it clearly as a command archive/evidence page, not a beginner
   learning page.

4. Add a "two backend meanings" explanation near the first backend discussion.
   Explain that `backend="rtdl"` belongs to the RTDL kernel/lowering contract,
   while `--backend cpu_python_reference|embree|optix|...` selects the runtime
   execution engine.

5. Add a beginner backend table.
   Recommended wording: `cpu_python_reference` is the learning backend;
   `cpu` is the native/oracle validation backend; Embree/OptiX are optional
   native backends with dependency and claim boundaries.

6. Add a short troubleshooting/failure-mode section.
   Cover missing `PYTHONPATH`, unavailable native/GPU backends, wrong runtime
   input shape, and the local Windows Python `<prefix>` warning if it appears
   again on clean machines.

7. Audit `reduce_rows` warnings across entry docs.
   Make sure users do not infer that `reduce_rows` is always backend
   accelerated.

## Non-Blocking Follow-Ups

- A dedicated 4K hidden-star tutorial would be valuable if the video is treated
  as a public showcase. It should be framed as a capstone, not as a release
  blocker.
- A "write your first custom kernel" exercise would improve learning depth.
  Even better, include one intentional mistake and show how to diagnose it.
- The DSL reference should explicitly tell new users not to choose legacy
  `backend="rayjoin"` unless they are maintaining compatibility code.

## Release Guidance

The current docs are acceptable for a technical release candidate and are much
better than a raw research archive. They are not yet ideal beginner-product
docs because secondary pages still leak historical project context.

The next docs pass should be editorial rather than architectural: keep the
language and examples, but clean the route so a new user first sees current
RTDL, then sees evidence/history only when they intentionally ask for it.
