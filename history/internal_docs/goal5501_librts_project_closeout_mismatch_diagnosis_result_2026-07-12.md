# Goal5501 LibRTS Project Closeout And Range-Intersects Diagnosis

## Status

```text
librts_project_bounded_closeout_ready__mismatch_diagnosis_completed__full_paper_not_claimed__review_pending
```

Goal5501 is the final implementation goal for the current LibRTS workstream.
It does not pretend to recover unavailable relation rows or turn a partial
operation matrix into a paper reproduction. It closes the engineering loop at
the strongest evidence-backed boundary: exact archive provenance, generic
columnar AABB execution, author/RTDL count evidence, independent diagnostic
oracles, explicit capacity limits, and a final claim boundary.

## Diagnosis Inputs

The diagnosis uses the two Goal5500 disagreement cases and creates same-source
prefix datasets from the official extracted WKT files:

```text
geometry prefix: first 100,000 WKT geometry rows
query prefix:    first 10,000 WKT query rows
author config:   load_factor=1
RTDL route:      Aabb2DColumns + prepare_aabb_index_2d_columns(backend="optix")
oracles:         CPU float64 overlap, CPU float32 overlap,
                 CPU float32 overlap with 1e-6 indexed-box padding
```

All four routes consume the same prefix bytes for each diagnostic case. The
prefix is a diagnostic workload, not a paper dataset replacement and not a
full-input equivalence claim.

## Diagnostic Results

| Case | Author | RTDL | CPU float64 | CPU float32 | RTDL=CPU32 |
|---|---:|---:|---:|---:|---|
| `parks_Europe` prefix | 13,695,048 | 13,695,053 | 13,695,027 | 13,695,053 | yes |
| `lakes.bz2` prefix | 12,596,850 | 12,596,850 | 12,596,844 | 12,596,850 | yes |
| `parks.bz2` capacity prefix | 11,815,394 | 11,815,398 | 11,815,384 | 11,815,398 | yes |

The diagnostic establishes a useful boundary:

- RTDL agrees with the independent CPU float32 AABB-overlap oracle on all
  three feasible prefix probes.
- `lakes.bz2` author and RTDL agree on the 100k prefix even though the full
  8.3M-geometry case disagrees.
- The author differs from RTDL on the `parks_Europe` and `parks.bz2` prefixes
  by 5 and 4 counts respectively.
- The 1e-6 padding variant does not explain the `parks_Europe` prefix result;
  it is not promoted as the root cause of the full-input disagreement.

This narrows the full-input mismatch to a scale-sensitive or execution-contract
difference between the author route and RTDL's generic float32 AABB route. It
does **not** prove that the author is wrong, that RTDL is wrong, or that the
full-input difference is caused by one specific implementation detail. The
author binary emits counts only, so no pair-row adjudication is possible in
this campaign.

## Capacity Result

The full Goal5500 `parks.bz2` case remains an author-side CUDA allocation
failure. Goal5501's 100k-geometry capacity prefix completes and records the
same RTDL/CPU32 relationship, but it does not resolve the full 8.5GB geometry
case. The project therefore closes this capacity question as an explicit
resource boundary, not as a semantic success.

## Final Project Boundary

The current LibRTS project is complete at this bounded closeout boundary:

- official archive provenance is verified;
- exact point-contains and range-contains count lines are recorded;
- exact range-intersects has three full-input count matches;
- six-geometry range-intersects coverage was attempted and honestly records
  three matches, two unresolved full-input count disagreements, and one author
  OOM;
- the disagreements have an independent generic diagnostic result rather than
  being silently ignored;
- the RTDL route remains generic AABB/columnar functionality;
- cache lifecycle remains app-owned;
- no LibRTS-specific RTDL primitive was introduced;
- Embree remains out of scope.

The following are explicitly **not** complete:

```text
all 42 exact range-intersects pairs
pointwise relation equality for the standard author count-only binary
Figure 6 reproduction
full LibRTS paper reproduction
author/RTDL performance ratio or parity
device zero-copy
Embree comparison
```

Further work would be a new project scope, not a hidden continuation of this
closeout: either obtain an author pair-row comparator, obtain an externally
accepted execution-contract mapping, or authorize a new capacity/hardware
campaign.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_gate.json
Paper-reproduction-apps/librts-paper/results/goal5501/mismatch_diagnostic.json
Paper-reproduction-apps/librts-paper/results/goal5501/parks_bz2_capacity.json
Paper-reproduction-apps/librts-paper/run_goal5501_range_intersects_mismatch_diagnostic.py
tests/goal5501_librts_range_intersects_mismatch_diagnostic_test.py
tests/goal5501_librts_mismatch_diagnostic_result_test.py
```
