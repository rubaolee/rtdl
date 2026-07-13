# X-HD Paper App Completion Goals Plan

Date: 2026-07-08

## Completion Definition

This plan treats "complete" as a bounded, honest paper-reproduction app, not a
full paper figure reproduction unless exact paper inputs become available.

Completion requires:

1. author `hd_exec` provenance/build/run is documented;
2. bounded same-input gates exist for 2D and 3D;
3. at least one real RTDL route is used inside the paper app, not only an
   app-owned exact comparator;
4. generic RTDL/system capabilities created during the work are separated from
   X-HD app-owned code;
5. correctness and performance claims are regime-labeled and reviewable;
6. final docs expose what is reproduced, what is not reproduced, and why.

Already implemented / status:

- Goal5110: X-HD provenance scaffold; externally reviewed and approved.
- Goal5111: tiny same-input author JSON gate packet; implemented, external
  review pending.
- Goal5112: author `hd_exec` built and run on POD as `Author+BuildPatch`;
  implemented, external review pending.
- Goal5113: bounded2d author JSON gate matched exact reference; implemented,
  external review pending.
- Goal5114: bounded3d author JSON gate matched exact reference; implemented,
  external review pending.
- Goal5115: bounded2d RTDL 2D columnar route matched author JSON and exact
  reference; implemented, external review pending.

The completion plan cannot treat Goals5111-5115 as approved evidence until the
external review packet for those goals is closed. They are implementation
evidence, not reviewed-and-approved completion evidence.

## Remaining Goals

### Goal5116 - X-HD Completion Criteria And Phase Boundary

Purpose: freeze the target before more implementation.

Deliverables:

- define final allowed claims for X-HD;
- define three evidence levels:
  - bounded same-input correctness;
  - representative same-source correctness;
  - exact paper dataset reproduction;
- define performance regimes:
  - author `Running.AvgTime`;
  - author wall time;
  - RTDL route wall time;
  - RTDL setup/prepare/query/comparator phases;
- decide what counts as "done" for v2.14.5.
- reconcile the fact that Goal5115 already produced one bounded 2D route result
  before this boundary freeze; Goal5116 must classify that result under the
  final evidence model rather than silently treating it as a pre-approved
  headline.

Exit label:

```text
xhd_completion_boundary_frozen
```

Blocker: no new performance or route headline may be introduced before this
boundary exists.

### Goal5117 - Generic 3D Hausdorff Column Route Contract

Purpose: prevent bounded3d from remaining only an app-owned exact comparator.

Deliverables:

- design a public/generic 3D Hausdorff route contract;
- decide API shape:
  - either `directed_hausdorff_3d_*_columns`;
  - or a generic ND column route with explicit dimensionality;
- clarify whether the already-used 2D columnar Hausdorff route is fully public
  and generically proven, or provisional until a non-X-HD consumer/test is
  recorded in this line;
- include a non-X-HD synthetic test proving this is system capability, not
  app-specific code;
- keep route exact/reference first, performance second.

Exit label:

```text
generic_3d_hausdorff_column_route_contract_ready
```

Red line: no `xhd`, `paper`, or author-specific naming in RTDL core APIs.

### Goal5118 - Bounded3D RTDL Route Gate

Purpose: close the current asymmetry: bounded3d has author-vs-exact evidence
but no RTDL route evidence.

Deliverables:

- implement/apply the Goal5117 route to bounded3d;
- compare:
  - author `HDResult`;
  - RTDL 3D route result;
  - deterministic exact reference;
- update manifest/results/register.

Exit label:

```text
bounded3d_rtdl_route_matched_author_json
```

Not authorized:

- performance claim;
- X-HD RT-core algorithm equivalence;
- full paper reproduction.

### Goal5119 - X-HD Author Phase Semantics Audit

Purpose: understand what the author `rt` variant actually computes and reports,
so later performance comparison is not apples-to-oranges.

Deliverables:

- inspect `src/main.cpp`, `src/run_hausdorff_distance.cu`,
  `src/hd_impl/hausdorff_distance_rt.h`, and JSON phase fields;
- document what `HDResult`, `Running.AvgTime`, `Repeats`, `RTTime`,
  `CUDATime`, and `OffloadingSize` include/exclude;
- document whether author timing excludes parsing/loading/preprocessing;
- identify which RTDL phase is comparable to which author phase.
- define whether author `HDResult` is directed or symmetric Hausdorff distance,
  and if directed, which direction is reported. Confirm that RTDL comparisons
  use the same definition rather than merely matching current bounded fixtures
  by numerical coincidence.

Exit label:

```text
author_phase_boundary_understood
```

This goal is required before any fair performance matrix.

### Goal5120 - RTDL X-HD-Style Decision Route Feasibility

Purpose: decide whether RTDL can reproduce the X-HD-style fixed-radius/decision
logic using generic primitives, or whether current RTDL route remains exact
columnar/reference only.

Deliverables:

- audit existing fixed-radius/count-threshold assets;
- run or design a bounded 2D decision route for `HD <= r`;
- compare decision results against exact reference on tiny/bounded2d;
- state whether this is:
  - ready as a generic route;
  - needs generic API work;
  - or out of scope for this release.

Exit labels:

```text
xhd_style_decision_route_feasible_with_existing_generic_primitives
xhd_style_decision_route_requires_new_generic_api
xhd_style_decision_route_deferred_reference_route_only
```

Red line: do not write an X-HD-specific primitive.

### Goal5121 - Representative Same-Source Fixture Decision

Purpose: decide whether the project can go beyond tiny/bounded synthetic
fixtures.

Deliverables:

- search author repo/`expr` for accessible input datasets;
- classify inputs:
  - exact paper datasets available;
  - same-source representative datasets available;
  - no usable datasets available;
- if available, add one small representative gate;
- if unavailable, document why bounded fixtures are the honest stopping point.

Exit labels:

```text
exact_paper_inputs_available_next
representative_same_source_inputs_available_next
paper_inputs_unavailable_bounded_fixtures_only
```

### Goal5122 - Representative Correctness Gate

Purpose: if Goal5121 finds usable inputs, run a larger correctness gate.

Deliverables:

- run author `hd_exec` and RTDL route on the same representative input;
- compare `HDResult` under explicit tolerance;
- preserve raw author JSON and RTDL summary;
- classify as representative, not exact paper reproduction, unless the input is
  proven to be exact paper data.

Exit label:

```text
xhd_representative_same_source_correctness_gate_matched
```

This goal is skipped if Goal5121 exits `paper_inputs_unavailable...`.

### Goal5123 - Fair Performance Matrix

Purpose: produce one honest performance table, only after phase semantics are
known.

Deliverables:

- measure author and RTDL on the same input(s);
- separate:
  - author `Running.AvgTime`;
  - author wall time;
  - RTDL setup/prepare;
  - RTDL route query;
  - comparator/output;
  - cold process vs warm process;
- report no ratio when denominators do not align.

Exit label:

```text
xhd_fair_performance_matrix_published_with_boundaries
```

Not authorized:

- author parity unless same denominator proves it;
- speedup headline from different regimes;
- hiding build/setup/loading costs.

### Goal5124 - System API Extraction Review

Purpose: harvest reusable RTDL language/system value from the X-HD app.

Deliverables:

- list what stayed app-owned:
  - author wrapper;
  - WKT/POD fixture policy;
  - author JSON comparator;
  - tolerance policy;
- list what became or should become system API:
  - 2D columnar Hausdorff route already used;
  - possible 3D/ND Hausdorff route;
  - possible fixed-radius decision route;
- add at least one non-X-HD test for any new system API.

Exit label:

```text
xhd_system_api_extraction_complete
```

### Goal5125 - X-HD Closeout Packet

Purpose: close the X-HD paper app line with reviewable evidence.

Deliverables:

- final README update;
- manifest status update;
- results inventory;
- review-opinion register update;
- public-surface leak scan;
- local test matrix;
- call-for-review covering Goals5110-5125.

Allowed final statuses:

```text
xhd_bounded_same_input_reproduction_complete
xhd_representative_same_source_reproduction_complete
xhd_exact_paper_reproduction_complete
```

The status must be chosen based on evidence, not aspiration.

## Recommended Execution Order

1. Goal5116 - freeze completion boundary.
2. Goal5117 - generic 3D route contract.
3. Goal5118 - bounded3d RTDL route.
4. Goal5119 - author phase semantics.
5. Goal5120 - X-HD-style decision feasibility.
6. Goal5121 - input/dataset decision.
7. Goal5122 - representative gate if available.
8. Goal5123 - fair performance matrix.
9. Goal5124 - system API extraction.
10. Goal5125 - closeout packet.

## Review Batch Points

Batch review 1:

```text
Goals5116-5118
```

Reason: locks claim boundary and closes 2D/3D RTDL route symmetry.

Batch review 2:

```text
Goals5119-5123
```

Reason: phase semantics, possible representative input, and performance matrix
must be reviewed together.

Batch review 3:

```text
Goals5124-5125
```

Reason: system extraction and final closeout.

## Main Risks

1. Existing RTDL Hausdorff route may remain reference/columnar, not X-HD RT-core
   algorithmic reproduction.
2. Exact paper inputs may not be available in the author repository.
3. Author timing fields may not align with RTDL route timing.
4. 3D generic route may require system API work rather than app-only wiring.

## Success Criteria

Minimum acceptable completion:

```text
xhd_bounded_same_input_reproduction_complete
```

with 2D and 3D bounded author gates, at least bounded2d RTDL route, clear
performance non-claim, and system API extraction.

Preferred completion:

```text
xhd_representative_same_source_reproduction_complete
```

with at least one larger same-source input and a fair performance matrix.

Full completion:

```text
xhd_exact_paper_reproduction_complete
```

only if exact paper datasets and matching author regime can be pinned.
