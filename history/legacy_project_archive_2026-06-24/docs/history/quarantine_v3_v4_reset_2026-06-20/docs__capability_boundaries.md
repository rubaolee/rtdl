# RTDL Capability Boundaries

This page states the current v3.0 capability boundary for learners and users.
Older release history is kept separately in
[Learner Doc Version Notes](history/learner_doc_version_notes.md).
For the short learner-facing summary, read
[Current Claim Boundaries](learn/current_claim_boundaries.md).

## Current Status

RTDL v3.0 is the current source-tree Python+partner+RTDL surface. It closes the
ten-app benchmark route matrix, provides the cleaned benchmark-vs-learner app
portfolio, preserves Embree and OptiX as evidence-bearing native routes where
configured, and publishes primitive-first plus partner-explicit app-author
guidance with conservative public wording.

## Short Version

| Category | Meaning |
| --- | --- |
| RTDL is for | RT-shaped query kernels inside Python applications |
| RTDL owns | typed inputs, traversal, refinement, emitted rows/device columns, backend dispatch |
| Python owns | app semantics, labels, policies, files, presentation, final decisions |
| Partners own | NumPy/CuPy/Numba arrays and normal framework continuations |
| Native engines own | generic primitive execution, not app-specific products |

## Intended Workloads

RTDL is a good fit when the hard part of a workload can be expressed as
candidate discovery plus refinement:

- ray/triangle any-hit and hit-count queries;
- visibility and blocker tests;
- segment/polygon candidate and hit-count queries;
- nearest-neighbor and fixed-radius rows;
- bounded graph traversal-style rows;
- bounded columnar scan or grouped summary rows;
- compact summaries, flags, counts, and bounded witness columns.

The V3 partner path lets Python programs pass partner-owned columns to
supported RTDL primitives and keep results in partner-owned columns when that
contract is documented.

## Not RTDL's Job

RTDL should not become:

- a renderer;
- a DBMS or SQL engine;
- a graph database;
- a GIS overlay engine;
- a robotics planner;
- a physics simulator;
- a general CuPy/Numba optimizer;
- a package-install promise.

Users can combine RTDL with any of those systems in Python. The boundary is
claim ownership: RTDL only claims the RTDL primitive and result contract that it
actually ships, tests, measures, and reviews.

## Performance Boundary

`--backend optix` means the OptiX backend was selected. It does not by itself
mean broad RT-core acceleration or whole-application speedup.

Allowed performance wording names the exact:

- app or primitive;
- backend;
- partner;
- hardware;
- command shape;
- output contract;
- artifact path.

When any of those are missing, use candidate or preview wording.

## v3.0 Release Boundaries

Allowed:

- Python+partner+RTDL source-tree major release;
- documented partner-owned input/output columns;
- current ten-app route closure under documented contracts;
- documented app-author strategy for primitive-first paths, prepared execution,
  explicit partner choice, and app-agnostic primitive requests;
- source-tree C ABI handoff for header/build/stage/prefix/archive/pkg-config/
  CMake/examples;
- streaming exact witness-column output where reviewed.

Not allowed:

- arbitrary CuPy/Numba acceleration;
- broad RT-core acceleration;
- arbitrary polygon overlay;
- package-install support;
- every user program is faster.
- stable SDK or generated binding packages;
- general zero-copy unless the exact measured path proves device-resident
  handoff.
