# Goal4806 Contract: Released RTDL RayJoin Section 5.7 Reproduction

Date: 2026-06-30

## Objective

Goal4806 is to reproduce the RayJoin paper Section 5.7 Polygon Overlay workload
as an installed-user application using:

- released RTDL V4.0.0;
- Python;
- Numba as the partner continuation where useful and measurable.

The reproduction must compare against:

- the RayJoin author C++/CUDA/OptiX implementation;
- the existing RTDL V2.14 exact-suite route;
- the released RTDL V4.0.0 + Python + Numba user application.

## What This Goal Is Not

Goal4806 is not runtime development.

The following actions do not count as progress for this goal:

- modifying `src/rtdsl`;
- modifying native RTDL/OptiX runtime files;
- adding new RTDL primitives;
- changing the released V4.0.0 API and calling the result "released V4";
- hiding RayJoin-specific behavior inside the RTDL language core;
- reporting LSI-only, PIP-only, or count-only results as full Section 5.7
  polygon overlay reproduction.

## Required User-Level Deliverable

The deliverable must be an external paper-reproduction application or script
that a user can run against released RTDL V4.0.0 without modifying RTDL source.

The app may:

- import released RTDL modules;
- call released RTDL RayJoin overlay helpers if they exist in V4.0.0;
- use Numba for user-side continuation/post-processing;
- call the RayJoin author binaries for baseline comparison;
- read the same CDB inputs and author parameters.

The app must not require editing RTDL source.

## Semantic Contract

The reproduction must preserve the RayJoin Section 5.7 workload:

- CDB input convention;
- eight Section 5.7 polygon-overlay dataset pairs where inputs are available;
- LSI;
- vertex PIP in both directions;
- midpoint PIP for output-chain construction;
- output-chain semantics;
- fixed Section 5.7 parameters:
  `grid_size=15000`, `mode=rt`, `-fau`, `xsect_factor=0.1`, `enlarge=3.5`;
- author-compatible precision and tie-break boundary, especially PIP
  equal-height boundary cases.

## Evidence Required For Completion

Goal4806 is complete only when current evidence proves:

1. A clean released V4.0.0 user environment can run the reproduction app.
2. The app runs the full Section 5.7 overlay workload, not just a substage.
3. Correctness is checked against the author output or an author-compatible
   topology/geometry/hash/chain-level oracle.
4. Performance is measured on the same RT hardware and same inputs for:
   author code, RTDL V2.14 route, and released RTDL V4.0.0 + Python + Numba.
5. Any missing dataset, missing author binary, or missing released RTDL feature
   is recorded as a product gap, not patched inside RTDL during this goal.

## Current Clean-Tag Finding

Clean `v4.0.0` tag inspection shows:

- `examples/paper_reproduction/rayjoin.py` is an explanatory wrapper and harness
  forwarder; it does not expose Section 5.7 run/preflight/Numba-auto commands.
- released `rtdsl.v4` has no public RayJoin Section 5.7 symbol.
- released `scripts/rayjoin_paper_reproduction_suite.py run-rtdl` and
  `rtdsl.rayjoin_overlay.run_rayjoin_overlay_rtdl_from_cdb_paths()` do provide
  RTDL overlay execution capability, subject to CDB inputs and native runtime
  availability.

Therefore Goal4806 remains incomplete.  The next valid action is to build the
external user application around released V4.0.0 capabilities, then test it
against exact Section 5.7 inputs on the POD.

