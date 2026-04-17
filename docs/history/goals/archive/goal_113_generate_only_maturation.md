# Goal 113: Generate-Only Maturation

Date: 2026-04-05
Status: accepted

## Goal

Strengthen the Goal 111 generate-only MVP into a more useful but still tightly
bounded product surface.

Goal 113 is not a mandate to broaden code generation arbitrarily. Its job is to
improve the existing narrow generate-only mode while preserving the workload-
first discipline of v0.2.

## Why this goal now

Goal 111 proved that a small generate-only mode is worth keeping:

- one structured request in
- one runnable RTDL file out
- verification included

But Goal 111 also closed with an explicit narrowness boundary:

- one workload family
- one generated file shape
- one renderer

So the next step is not “declare victory.” The next step is to determine
whether the feature can become materially stronger without collapsing into thin
template filling.

## Scope

Goal 113 should improve the current generate-only path in ways that increase
real user value while staying controlled.

In scope:

- stronger request-contract quality
- stronger generated-program usefulness
- stronger verification and generated-code quality checks
- one additional layer of controlled flexibility if it clearly helps users

Out of scope:

- arbitrary project scaffolding for all RTDL workloads
- native C++ or CUDA code generation as the main target
- broad multi-workload expansion before one stronger generate-only story exists
- turning code generation into the main v0.2 identity

## Candidate improvement directions

Goal 113 may choose from the following, but should not try to do all of them
at once:

1. request-contract refinement
   - clearer typed request shape
   - optional explanation/comment level
   - better output-shape control without fake flexibility

2. generated-program quality improvements
   - cleaner structure
   - clearer usage comments
   - better self-contained handoff quality

3. verification maturity
   - stronger checks on generated output
   - better proof that generated code stays runnable and correct

4. one carefully chosen expansion
   - either one more accepted backend surface
   - or one more generate-only output shape
   - or one more controlled user scenario

## Acceptance boundary

Goal 113 is accepted only if all of the following become true:

1. the feature becomes more useful than the Goal 111 MVP in a concrete user
   scenario
2. the final package explains exactly what improved and why it matters
3. the final package does not overclaim generality
4. the generated output remains verification-backed
5. the work does not collapse into a collection of shallow templates

## Kill criteria

Goal 113 should be cut back or paused if:

- “improvement” mostly means more constants or more boilerplate branches
- the new flexibility is mostly decorative
- the request contract expands faster than real user value
- the package cannot explain why the strengthened mode is better than:
  - Goal 111
  - a curated example
  - a template file

## Required outputs

- one explicit Goal 113 improvement target
- one implementation package
- one validation package
- one critique/rebuttal pass focused on whether the improvement is real
- one final keep/pause judgment for the strengthened feature

## Final accepted result

Goal 113 closes with one concrete improvement target:

- `handoff_bundle` artifact shape

The accepted strengthened feature now supports two artifact shapes for the same
seed family:

- `single_file`
- `handoff_bundle`

The accepted bundle shape includes:

- one runnable generated RTDL Python program
- one request manifest
- one README with handoff-oriented run instructions

This is accepted as a real improvement over Goal 111 because it serves one
clearer user scenario:

- generating a reviewable handoff package for a collaborator or downstream user

The package remains deliberately narrow:

- still one workload family
- still Python RTDL only
- still no broad project scaffolding claim
- still pause-worthy if later expansion degenerates into low-signal template
  multiplication
