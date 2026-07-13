# Goal5127 - X-HD Generic Nearest Pipeline Extraction

## Verdict

`completed_generic_nearest_pipeline_extraction`

## Why This Goal Exists

The X-HD paper app raised a system-design question: Hausdorff distance is an
application-level composition, not an RTDL core concept. Historical RTDL work
already contained many useful assets for this workload:

- generic `knn_rows(k=1)` traversal/refine rows;
- generic fixed-radius threshold/count scenes;
- partner-column handoff helpers;
- grouped top-k and grouped argmin/global-argmax reductions;
- previous `directed_hausdorff_*` convenience wrappers.

The gap was not absence of assets. The gap was that the reusable building blocks
were not exposed as a clean app-neutral pipeline. Goal5127 makes that boundary
explicit.

## What Changed

In `src/rtdsl/partner_continuations.py`, added three app-neutral NumPy column
helpers:

1. `pairwise_l2_distance_candidate_rows_numpy_columns(...)`
   - Converts source/target point columns into generic pairwise L2 candidate rows.
   - Supports caller-selected coordinate fields, e.g. `("x", "y")` or
     `("x", "y", "z")`.
   - Emits `PartnerCandidateRows`, not a Hausdorff object.

2. `nearest_witness_numpy_columns(...)`
   - Reduces generic candidate rows to one nearest witness per source row.
   - Uses the existing deterministic grouped top-k helper.

3. `max_nearest_distance_witness_numpy_columns(...)`
   - Reduces nearest-witness columns to the row with maximum nearest distance.
   - This is a generic max-over-nearest operation; applications may interpret it.

The existing `directed_hausdorff_2d_numpy_columns(...)` and
`directed_hausdorff_3d_numpy_columns(...)` functions remain public compatibility
wrappers, but now compose the generic pipeline:

```text
pairwise_l2_distance_candidate_rows
  -> nearest_witness_columns
  -> max_nearest_distance_witness
```

The new helpers are exported from `rtdsl.__init__`.

## What This Proves

- RTDL does not need a Hausdorff-specific core primitive for this bounded X-HD
  route.
- Directed Hausdorff can be expressed as a composition over generic candidate
  rows and grouped reductions.
- The newly exposed generic pipeline carries no X-HD, paper, author, or `hd_exec`
  identity in the core implementation window.

## What This Does Not Prove

- It does not prove an RT-core X-HD algorithm reproduction.
- It does not add a new OptiX/native traversal.
- It does not improve performance.
- It does not claim author parity or paper-level performance.
- It does not replace future work on a true X-HD-style nearest-witness traversal
  or candidate-cell pruning pipeline.

## Validation

Command:

```text
py -m unittest tests.goal5110_xhd_paper_app_scaffold_test tests.goal5111_xhd_author_json_gate_test tests.goal5113_xhd_bounded2d_author_gate_test tests.goal5114_xhd_bounded3d_author_gate_test tests.goal5115_xhd_rtdl_route_gate_test tests.goal5117_generic_3d_hausdorff_column_route_test tests.goal5118_xhd_bounded3d_rtdl_route_gate_test tests.goal5127_xhd_generic_nearest_pipeline_extraction_test
```

Result:

```text
Ran 24 tests in 1.330s
OK
```

The new Goal5127 test checks:

- pairwise L2 candidate rows for a 3D fixture;
- nearest witness columns;
- max-nearest witness;
- equality with the existing `directed_hausdorff_3d_numpy_columns` wrapper;
- source-level app-neutral scan of the generic pipeline window;
- fail-closed dimension contract validation.

## Claim Boundary

Allowed:

- "RTDL now exposes a generic NumPy column pipeline for pairwise L2 candidate
  rows, nearest witnesses, and max-nearest witness reduction."
- "The X-HD bounded route can use Hausdorff as an app-level wrapper over these
  generic primitives."

Not allowed:

- "RTDL core implements X-HD."
- "RTDL core has a Hausdorff primitive as a fundamental language concept."
- "This is a performance improvement."
- "This closes paper-level X-HD reproduction."
