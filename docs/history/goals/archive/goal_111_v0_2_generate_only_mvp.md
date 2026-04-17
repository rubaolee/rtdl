# Goal 111: v0.2 Generate-Only MVP

Date: 2026-04-05
Status: accepted

## Goal

Attempt one tightly constrained RTDL generate-only MVP for v0.2.

The MVP should prove or disprove whether RTDL can provide useful code
generation without executing locally, while staying within the workload-first
discipline established by Goals 107, 108, and 110.

## Why this goal now

Goal 110 already provides the first release-defining v0.2 workload-family
closure. That makes code generation the next legitimate secondary bet rather
than a distraction from proving RTDL can expand beyond the v0.1 RayJoin-heavy
slice.

This goal is still gated and killable.

## MVP scope

Goal 111 should target exactly one accepted family:

- `segment_polygon_hitcount`

But the MVP must prove more than "we can generate another example file."

The generator input contract must therefore be explicit and structured. The
minimum accepted input shape is:

- workload family
- dataset choice from an accepted set
- backend choice from an accepted set
- output mode

The generated output must produce:

- one runnable Python program
- one RTDL kernel
- one dataset/case construction block
- one backend runner
- one verification block tied to the requested dataset/output contract

The generated artifact must target at least:

- `cpu`

with optional support for:

- `cpu_python_reference`
- `embree`
- `optix`

## Explicit non-goals

Goal 111 does **not** try to:

- generate arbitrary multi-file projects for every RTDL workload
- generate native C++ or CUDA directly as the first MVP
- solve backend performance
- become a generic AI-codegen benchmark
- replace the normal executable RTDL path

## Required outputs

- one clear generate-only product contract
- one accepted generated artifact shape
- one end-to-end worked example
- one verification rule for judging generated output quality
- one critique/rebuttal pass on whether the MVP is genuinely useful or should
  be cut back

## Acceptance boundary

Goal 111 is accepted only if all of the following become true:

1. the generator input contract is explicit and documented
2. the generated output is runnable without manual reconstruction
3. the generated output targets at least the normal executable `cpu` RTDL path
4. the generated output is specific to RTDL rather than mostly boilerplate
5. the generated output includes a verification path tied to the requested
   dataset/output contract
6. the MVP stays constrained to one accepted family
7. the final package includes one concrete user scenario where generation is
   more useful than:
   - pointing the user to an existing example
   - giving them a template file
   - a short cookbook recipe
8. the final package states clearly whether the MVP is promising enough to keep
   or weak enough to pause

## Kill criteria

Goal 111 should be cut back or paused if:

- the generated output is mostly template boilerplate
- the generated output is not runnable from a normal repo checkout
- the generated artifact is less useful than simply pointing the user at an
  example file
- the generator input contract is so narrow that it is effectively a hardcoded
  example selector
- the MVP cannot justify why generation helps more than examples/templates
- the verification story is too weak to tell whether generation succeeded

## Important sequencing note

Goal 111 is a secondary v0.2 bet.

It should not be allowed to rewrite the v0.2 identity established by Goal 110:

- workload-first
- disciplined scope
- explicit honesty boundaries

## Final accepted result

Goal 111 closed as a **narrow generate-only MVP**.

The accepted package now includes:

- one structured request contract
- one generator module
- one CLI entry point
- one tracked generated example artifact
- one verification-backed runnable output shape

The MVP survives because it does something more specific than pointing the user
at an example file:

- it accepts one explicit workload/dataset/backend/output request
- it emits one runnable RTDL Python program for that exact request
- it carries its own verification path against `cpu_python_reference`
- it owns the accepted dataset-construction logic directly instead of
  deferring to `baseline_runner`

But the accepted final position is still intentionally narrow:

- one family only: `segment_polygon_hitcount`
- one generated-file shape only: runnable Python RTDL program
- no claim yet that this should expand into arbitrary multi-file project
  generation
- still pause-worthy if future expansion collapses into thin template filling
