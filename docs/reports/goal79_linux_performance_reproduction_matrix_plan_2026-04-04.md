# Goal 79 Plan: Linux Performance Reproduction Matrix

Date: 2026-04-04
Status: planned

## Objective

Measure the available RayJoin-style performance surfaces on Linux with the RTDL backends that currently matter for performance:

- PostGIS
- Embree
- OptiX

## Why This Goal Exists

The project now has:

- correctness closure on the accepted bounded surfaces
- backend performance wins on specific prepared-execution county runs
- explicit oracle trust envelopes for correctness and demos

The next missing artifact is a single Linux performance package that tells the truth about the current available experiment surface without mixing incompatible timing boundaries.

## Inclusion Rule

Include a workload family only if:

- the dataset is available
- the run is operationally finishable
- the timing boundary can be named precisely
- PostGIS and at least one RTDL performance backend can be measured honestly

## Exclusion Rule

Skip a workload family if:

- the source dataset is unavailable or unstable
- the run cannot be completed reliably on Linux
- the timing boundary would be ambiguous

Skipped rows must be recorded explicitly, not omitted silently.

## Timing Boundaries

Every measurement row must be labeled as one of:

1. `end_to_end`
2. `prepared_execution`
3. `cached_repeated_call`

No report table may compare those labels as if they were identical.

## Expected Candidate Surfaces

Initial candidate set:

- county/zipcode positive-hit `pip`
- blockgroup/waterbodies positive-hit `pip`
- any additional available RayJoin-style surfaces already validated in the current Linux environment

The final included set depends on actual dataset availability and reliable execution.

## Deliverables

- goal report
- machine-readable summary artifact
- human-readable matrix artifact
- artifact note with provenance and skipped rows
- Codex review
- Gemini review
- consensus note

## Review Rule

This goal should use:

- Codex review
- Gemini review

Claude is optional bonus review, not a dependency.
