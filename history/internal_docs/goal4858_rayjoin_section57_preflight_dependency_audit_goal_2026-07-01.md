# Goal4858: RayJoin Section 5.7 Preflight Dependency Audit

Date: 2026-07-01

## Purpose

Prepare for the RayJoin paper Section 5.7 polygon-overlay reproduction without
falling into an unnecessary full reproduction of Sections 5.4, 5.5, or 5.6.

Goal4858 is a bounded, mostly read-only dependency audit.  It must answer:

1. What Section 5.7 needs from Sections 3.2, 5.4, 5.5, and 5.6.
2. Which precision, SoS, adaptive-grouping, and parameter choices must be locked
   before running polygon overlay.
3. Whether any 5.4/5.5/5.6 experiment is a real prerequisite for Section 5.7.
4. Whether RTDL now has the public primitives needed to attempt 5.7 as an
   application-layer implementation rather than a bundled-helper shortcut.

The default expected outcome is: read and extract dependencies from 5.4-5.6,
then proceed directly to Section 5.7.

## Background State

Completed inputs:

- Section 5.2 LSI reproduction is bounded-closed through the public
  `prepare_planar_map_lsi_2d_optix` front door for the available cases.
- Section 5.3 PIP / point-location reproduction is bounded-closed for two
  serious exact cases plus one representative count-only case through the
  public `prepare_planar_map_point_location_2d_optix` front door.
- Goal4857 cleaned the Section 5.3 public front door so user scripts no longer
  set internal RayJoin CDB environment variables directly.

Open risk:

- Section 5.7 is not just LSI plus PIP counts.  It requires overlay-chain
  construction, midpoint/face classification, author-compatible parameters,
  and exact output validation.

## Work Items

### A. Paper dependency extraction

Read and summarize the specific Section 5.7 dependencies from:

- Section 3.2: conservative representation / precision contract.
- Section 5.4: precision validation and whether it imposes any correctness gate
  on 5.7.
- Section 5.5: adaptive grouping and parameter tuning, especially `s`,
  `enlarge`, `grid_size`, `xsect_factor`, and any build/query tradeoff that
  affects the Section 5.7 command line.
- Section 5.6: scalability methodology and whether it is a prerequisite for
  5.7 or a separate later experiment.
- Section 5.7: polygon-overlay workflow, inputs, outputs, timing scope, and
  baseline/comparison scope.

### B. Author source dependency extraction

Read the corresponding author source paths and identify:

- How Section 5.7 calls or composes LSI.
- How Section 5.7 calls or composes PIP / point-location.
- Where adaptive grouping parameters enter.
- Where output chains are built.
- What files or answer artifacts are required for correctness validation.
- What timing region the author reports for Section 5.7.

This is source reading and mapping only.  Do not patch author source in this
goal except to inspect already-recorded AuthorPatch compatibility notes.

### C. RTDL capability map for Section 5.7

Build a stage-by-stage map:

| Section 5.7 stage | Author source contract | RTDL public primitive available? | App-layer code needed? | Missing capability? |
|---|---|---|---|---|

The classification must distinguish:

- public generic RTDL primitive,
- Numba partner continuation,
- app-layer formatting or orchestration,
- bundled RayJoin helper,
- missing RTDL capability.

Bundled helper use must never be described as generic language reproduction.

### D. 5.4-5.6 go/no-go decision

For each of 5.4, 5.5, and 5.6, write one explicit decision:

- `dependency_only`: read and apply to 5.7, but do not reproduce now.
- `must_reproduce_before_5_7`: a true blocking dependency was found.
- `defer_until_after_5_7`: useful for later paper completeness or performance
  scaling, but not needed before overlay.

Any `must_reproduce_before_5_7` decision must name the exact Section 5.7 risk it
blocks.  Vague caution is not enough.

### E. Section 5.7 execution plan

Produce the next concrete Goal4859 proposal for Section 5.7, including:

- exact dataset pair(s) to run first,
- exact author command or command template,
- exact RTDL user-script command or command template,
- correctness check: byte-equal answer, topology hash, or explicit reason why
  answer files are unavailable,
- performance check only after correctness,
- what is allowed to use from public RTDL primitives and Numba,
- what is forbidden.

## Explicit Non-Goals

Goal4858 must not:

- run a full Section 5.4 precision reproduction;
- run a full Section 5.5 adaptive-grouping sweep;
- run a full Section 5.6 scalability experiment;
- run POD performance experiments;
- modify `src/rtdsl/**` or `src/native/**`;
- patch the public release surface;
- use bundled RayJoin helpers as generic RTDL language evidence;
- claim Section 5.7 reproduction.

## Verification Standard

Goal4858 passes only if it produces a report with:

1. paper-section dependency table for 3.2, 5.4, 5.5, 5.6, 5.7;
2. author-source dependency map with file/function names;
3. Section 5.7 stage-by-stage RTDL capability map;
4. explicit do/defer decisions for 5.4, 5.5, 5.6;
5. a concrete Goal4859 Section 5.7 execution plan;
6. no runtime/native edits;
7. no POD spend unless a later goal explicitly authorizes it.

## Exit Labels

Allowed exit labels:

- `completed_section57_preflight__go_directly_to_57`
- `completed_section57_preflight__must_first_reproduce_54`
- `completed_section57_preflight__must_first_reproduce_55`
- `completed_section57_preflight__must_first_reproduce_56`
- `blocked_by_missing_author_source_or_inputs`
- `blocked_by_rtdl_public_capability_gap`

The expected label is:

`completed_section57_preflight__go_directly_to_57`

## Review Gate

Goal4858 completion should be sent to Antigravity for review.  Claude review is
valuable but may be recorded as debt if unavailable, because this is a bounded
read-only planning/audit goal rather than a runtime correctness or release
authorization gate.

## Goal-Level Decision Audit

1. Am I being foolish by skipping full 5.4-5.6 reproduction?
   No, because Section 5.7 is the target application and 5.4-5.6 are precision,
   tuning, and scalability sections.  They should inform 5.7, not automatically
   become separate reproduction projects.

2. What actions would make this decision foolish?
   It would become foolish if I ignored a concrete 5.7 dependency in 5.4/5.5/5.6,
   or if I used this audit as an excuse to avoid the hard Section 5.7 overlay
   integration.

3. Is there another path that avoids getting stuck?
   Yes: extract only the dependencies needed for 5.7, lock them, and then run
   5.7.  Full 5.4-5.6 reproduction can be deferred until after overlay works.

4. Can I switch to a better path that solves the actual problem?
   Yes.  Goal4858 exists to force that switch: stop sequentially reproducing
   every paper section, and move to the decisive Section 5.7 application after
   a short dependency audit.
