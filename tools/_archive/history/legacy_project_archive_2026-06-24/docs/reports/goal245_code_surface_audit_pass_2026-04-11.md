# Goal 245 Report: Code Surface Audit Pass

Date: 2026-04-11
Status: implemented

## Summary

This goal records the public code-facing tier into the system audit database.

The pass covers the RTDL package entrypoint, DSL authoring API, core runtime
surface, oracle/native runtime, baseline runner, reference path, and the three
main accelerated backend runtimes.

## Key Outcome

The audited code surface is technically sound, but this pass intentionally does
not flatten all files to simple pass/no-pass language.

The most important follow-up item preserved in the database is:

- the CPU/oracle path is correct in structure, but still depends on a working
  local GEOS/native-toolchain setup on this macOS host before `run_cpu(...)`
  can succeed

That is a quality and environment-hardening issue, not a hidden correctness
claim failure in the released package surface.

## Direct Checks Used In This Pass

- package import:
  - `python3` import of `rtdsl` succeeded
- import cost:
  - clean import completed in about `0.14s` on this host
- truth path:
  - `run_cpu_python_reference(...)` on the fixed-radius authored case returned
    `4` rows
- package symbol surface:
  - `prepare_embree`, `prepare_optix`, and `prepare_vulkan` all import cleanly

## Outcome

After this pass, the audit database covers:

- front page
- tutorials
- public docs
- release-facing examples
- public code-facing surface

The next major tier is:

- tests, reports, and archive/history layers
