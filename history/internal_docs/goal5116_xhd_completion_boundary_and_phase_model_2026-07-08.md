# Goal5116 - X-HD Completion Boundary And Phase Model

Date: 2026-07-08

## Verdict

```text
xhd_completion_boundary_frozen
```

## Purpose

Freeze the X-HD paper-app completion boundary before more route or performance
work. This goal explicitly separates implementation evidence from externally
reviewed completion evidence.

## Evidence Levels

### Level 1 - Bounded Same-Input Correctness

Same small fixture, same author binary, same input files, explicit tolerance.

Allowed claims:

- bounded same-input author `HDResult` matched;
- bounded same-input RTDL route matched author JSON;
- no paper dataset or performance claim.

### Level 2 - Representative Same-Source Correctness

Input is larger and derived from an accessible author/source repository dataset,
but not proven to be the exact paper input.

Allowed claims:

- representative same-source correctness;
- no exact paper dataset claim unless provenance proves exact identity.

### Level 3 - Exact Paper Dataset Reproduction

Only allowed if exact paper input files and the corresponding author regime are
pinned.

Allowed claims:

- exact paper dataset result for the pinned dataset only.

## Final Status Labels

```text
xhd_bounded_same_input_reproduction_complete
xhd_representative_same_source_reproduction_complete
xhd_exact_paper_reproduction_complete
```

The final status must be evidence-driven.

## Performance Regimes

Any future matrix must separate:

- author wall time;
- author `Running.AvgTime`;
- author JSON phase fields such as `RTTime`, `CUDATime`, and `OffloadingSize`;
- RTDL setup/prepare time;
- RTDL route time;
- comparator/output time;
- cold process;
- warm long-lived process.

No ratio is allowed unless denominators match.

## Current Evidence Classification

Goal5110 is externally reviewed and approved.

Goals5111-5115 are implementation evidence and review pending:

- Goal5111: tiny same-input gate packet;
- Goal5112: author `hd_exec` build and tiny POD run;
- Goal5113: bounded2d author JSON gate;
- Goal5114: bounded3d author JSON gate;
- Goal5115: bounded2d RTDL public column route gate.

Goal5115 produced a route result before this boundary freeze. It is now
classified as Level 1 bounded same-input implementation evidence, pending
external review in the final packet.

## Done For v2.14.5

Minimum acceptable v2.14.5 X-HD closeout:

```text
xhd_bounded_same_input_reproduction_complete
```

Required evidence:

- author build/run provenance;
- bounded 2D and 3D author gates;
- bounded 2D and 3D RTDL route gates;
- claim boundary docs;
- system API extraction review;
- consolidated external review packet.

## Not Authorized

- full X-HD paper reproduction without exact paper inputs;
- exact paper dataset reproduction without pinned paper inputs;
- performance or speedup headline before Goal5119 and Goal5123;
- author parity unless same-denominator evidence proves it;
- reclassifying historical `hausdorff_xhd` benchmark results as paper
  reproduction.

## Next

Goal5117 and Goal5118 should close route symmetry by adding a generic 3D
Hausdorff public route and applying it to the bounded3d fixture.
