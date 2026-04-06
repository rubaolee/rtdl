# Goal 111 v0.2 Generate-Only MVP Plan

Date: 2026-04-05
Author: Codex
Status: in_progress

## Planning question

What is the smallest generate-only MVP that is still genuinely useful?

## Revised proposal after adversarial review

Keep `segment_polygon_hitcount` as the seed family because:

- Goal 110 just closed it
- its I/O contract is compact:
  - input: segments, polygons
  - output: `segment_id`, `hit_count`
- it already has:
  - deterministic authored case
  - fixture-backed case
  - derived case
  - example file
  - closure tests

But strengthen the MVP so it tests a real product mode rather than a dressed-up
example exporter.

## Proposed MVP shape

Input to generator:

- one small structured request, for example:
  - workload: `segment_polygon_hitcount`
  - dataset: `authored_segment_polygon_minimal`
  - backend: `cpu`
  - verify: `true`
  - output_mode: `rows`

Generated output:

- one Python file containing:
  - RTDL kernel
  - case builder
  - requested backend runner
  - one verification check against expected rows
  - concise usage comments

## Product-value test

The MVP should only survive if it beats curated examples/templates for one real
user scenario:

- user knows the workload family and dataset choice they want
- user wants a runnable starting program immediately
- user benefits from getting the exact requested backend + verification shape
  instead of manually editing an example

If the result is basically "here is the same example with light substitutions,"
the MVP should be paused.

## What must be challenged in review

- Is this actually more useful than a curated example?
- Is one generated Python file enough to count as a product mode if the input
  contract is real and the backend/verification are parameterized?
- Is `cpu` the minimum acceptable backend target, or is that still too weak?
- Should the MVP emit only RTDL-level code, or also a run command contract?
- Is `segment_polygon_hitcount` the right seed family for code generation, or
  is it too tied to the just-closed Goal 110 story?
