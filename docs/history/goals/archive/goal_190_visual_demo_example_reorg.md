# Goal 190: Visual Demo Example Reorganization

## Objective

Move the application-style 3D demo programs out of the flat `examples/` root and into a dedicated
`examples/visual_demo/` package, then update the codebase and docs to use the new paths consistently.

## Why

The visual demo programs are useful proof-of-capability artifacts, but they are not the same kind of
release-facing examples as the smaller workload-focused files in `examples/`. Keeping them in a dedicated
subdirectory makes the repo easier to scan and makes the project story clearer:

- RTDL remains positioned as a geometric-query runtime, not a graphics engine.
- The 3D demos remain present as bounded application proofs built on the same core.

## Scope

- Move the current 3D demo Python files into `examples/visual_demo/`
- Preserve direct script execution for the moved demos
- Update tests to import the moved modules
- Update live docs and preserved reports/handoffs to use the new paths
- Re-run bounded checks for the moved code paths

## Non-goals

- No semantic redesign of the visual demos
- No new rendering features
- No new backend behavior changes

## Success Criteria

- `examples/visual_demo/` contains the current 3D demo programs
- No stale repo references remain to the old flat `examples/*.py` demo paths
- The bounded move-affected test slice passes
- The moved smooth-camera demo still works as a direct CLI script
