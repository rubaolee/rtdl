# RTDL Capability Boundaries

This page states the current v2.0-facing capability boundary for learners and
users. Older release history is kept separately in
[Legacy Learner Doc Version Notes](history/legacy_learner_doc_version_notes.md).

## Current Status

RTDL v2.0 is a pre-release candidate, not a final release. The engineering
packet is strong, but final release waits for the strict 3-AI consensus redline
and a fresh Claude-family review.

## Short Version

| Category | Meaning |
| --- | --- |
| RTDL is for | RT-shaped query kernels inside Python applications |
| RTDL owns | typed inputs, traversal, refinement, emitted rows/device columns, backend dispatch |
| Python owns | app semantics, labels, policies, files, presentation, final decisions |
| Partners own | NumPy/PyTorch/CuPy arrays and normal framework continuations |
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

The v2.0-facing partner path lets Python programs pass partner-owned columns to
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
- a general PyTorch/CuPy optimizer;
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

## v2.0 Candidate Boundaries

Allowed:

- Python+partner+RTDL pre-release candidate;
- documented partner-owned input/output columns;
- current OptiX/RT evidence under documented contracts;
- streaming exact witness-column output where reviewed.

Not allowed:

- final v2.0 release before 3-AI consensus;
- arbitrary PyTorch/CuPy acceleration;
- broad RT-core acceleration;
- arbitrary polygon overlay;
- package-install support;
- every user program is faster.

