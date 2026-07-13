# RayJoin Hot-Path Numba Reachability Checklist

Date: 2026-07-03

Purpose: record which remaining RayJoin Section 5.7 hot-path phases are
realistic Numba targets, which are not, and what work is justified next.

This note is a supplement to the Goal4917 performance-status line. It is not a
release claim and not an authorization to implement a new optimization. It is a
decision aid for whether more Python/Numba work is worthwhile.

## Executive Answer

Only a small part of the current prepared-hot path is a realistic Numba target:
the numeric reprojection/sort region, currently about 0.88 seconds on the
Australia/South-Australia representative run.

The largest remaining single phase, the exact output-chain writer at about
1.76 seconds, is not a good Numba target. It is dominated by Python object
state, dictionaries, exact text formatting, output-chain sequencing, and bulk
string/file emission. Those are structurally outside Numba's main strength.

Therefore:

- Do not spend more time on Python writer micro-edits.
- Do not expect Numba to close the remaining RayJoin performance gap.
- If we do one more Numba probe, make it a narrow columnar
  reprojection/sort probe with a hard stop condition.
- If that probe does not materially reduce the 0.88 second numeric region,
  stop Python/Numba optimization for this workload.

## Current Hot-Path Evidence

Representative source:
`history/internal_docs/goal4915_intersection_writer_summary_2026-07-03.json`,
repeat 1.

| Phase | Time, seconds | Current shape | Numba reachability | Recommendation |
|---|---:|---|---|---|
| Prepared LSI pair-id replay | 0.006 | Native OptiX workspace; pair-id rows only | No meaningful Numba role | Done. Do not touch. |
| Vertex PIP map0/map1 | 1.109 total | Native point-location call plus row conversion into face arrays | Do not Numba traversal. Avoid/trim row conversion if possible. | Treat as native/runtime phase, not app Numba work. |
| Intersection reprojection | 0.468 | Python loop over pair rows; constructs `OverlayIntersection` objects; uses `Fraction` for exact scaled coordinates | Possible only if refactored to columnar numeric arrays; direct `njit` over current object/Fraction path is not viable | Worth at most one bounded columnar probe. |
| Sort map0/map1 | 0.416 total | Python dict grouping and object sort using rational-distance keys | Possible only if intersections become columnar keys/indices; not useful as a direct `njit` patch | Can be paired with reprojection in the same bounded probe. |
| Midpoint point generation | 0.019 total | Already routed through Goal4886 Numba helper | Already Numba; too small | Done. Do not touch. |
| Midpoint PIP | 0.001 total | Native point-location on small midpoint set | No meaningful Numba role | Done. Do not touch. |
| Assign midpoint faces | 0.001 total | Tiny Python loop | Too small | Ignore. |
| Exact output-chain writer | 1.763 | Python dictionaries, polygon/point id assignment, point dedupe, string formatting, line buffering, file emission | No, not in a useful way. Numeric skip-plan already uses Numba; the remaining work is text/object/output-format bound | Stop Python writer micro-edits. Any major writer speedup is a compiled output subsystem question, not Numba. |
| File summary/hash | 0.040 | File IO and hashing | No | Ignore. |

## Code Shape Audit

Files inspected:

- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`
- `history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py`
- `history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py`
- `history/internal_docs/goal4915_intersection_writer_summary_2026-07-03.json`

Findings:

1. `intersection_rows_from_pairs` is not directly Numba-friendly.
   It is a Python loop that constructs `OverlayIntersection` objects and uses
   `fractions.Fraction` to preserve author-compatible exact scaled coordinates.
   The right improvement is not "add njit"; it is to split the phase into
   numeric column production plus a minimal object materialization boundary.

2. `sort_xsects_for_map` is not directly Numba-friendly.
   It groups Python objects in a dict and sorts each group with a key that uses
   rational fields. Numba becomes useful only after the sort keys are made
   columnar numeric arrays and the sorted order is represented as integer
   indices.

3. `midpoint_points`, consecutive-point dedupe, chain keep, chain-has-xsects,
   and writer skip decisions already have Goal4886 Numba kernels.
   This was the correct Numba use: numeric arrays in, numeric mask/indices out.
   The remaining midpoint phase is now too small to chase.

4. `write_output_chains_streaming_numba_skip` has already moved the numeric
   skip-plan into Numba. The remaining writer work is still dominated by
   Python dictionaries, exact string formatting, point-id bookkeeping, and
   output-chain ordering. This is why Goal4915 improved correctness and a
   little wall time, but missed the hard writer/hot-body bars.

5. `faces_from_rows` already converts native rows to NumPy arrays and assigns
   face ids vectorially. If this phase is still too expensive in a larger case,
   the fix is a narrower native/row-buffer result shape, not Numba over Python
   objects.

## One Justified Optional Probe

If the owner wants one more optimization goal before stopping this line, the
only justified Numba-oriented probe is:

Columnar Reprojection/Sort Probe

Goal:

- Replace object-first reprojection/sort with a columnar numeric intermediate:
  `eid0`, `eid1`, scaled coordinates, display coordinates, sort keys, and owner
  indices.
- Keep the public RTDL LSI/PIP primitives unchanged.
- Preserve byte-for-byte output equality.
- Materialize Python `OverlayIntersection` objects only at the final boundary
  where the existing writer still requires them.

Hard bar:

- `intersection_reprojection_sec + sort_map0_sec + sort_map1_sec` must fall
  from about 0.884 seconds to <= 0.45 seconds on the same representative run.
- Overall hot body should fall from about 3.832 seconds to <= 3.45 seconds.
- Output must remain byte-equal to AuthorOfficial.
- If the bar is missed, stop Python/Numba optimization for this workload.

Expected result:

- Possible bounded win: 0.3 to 0.5 seconds.
- Not a path to beat the author C++/CUDA/OptiX stack by itself.
- Not a substitute for the larger architectural question about compiled output
  writer or dataflow-to-kernel pushdown.

## What Not To Do

- Do not try to Numba the text writer.
- Do not write more variants of `flush_plain_chain` or direct dataset-chain
  shortcuts without a new measured bottleneck.
- Do not call the writer issue a RT traversal issue.
- Do not claim Numba can close the remaining RayJoin gap.
- Do not turn a RayJoin-specific output format into RTDL core under a generic
  name.

## Decision Audit

Was the decision foolish? No. It is based on current phase measurements and
code-shape inspection, not on a belief that "more Numba" is automatically good.

What would have been foolish? Continuing to optimize the writer with Numba-like
edits after the measurements show it is text/object/output-format bound.

Alternative path? Yes: one bounded columnar reprojection/sort probe, or stop
RayJoin micro-optimization and move to either a generic pushdown experiment or
a separately reviewed compiled-output subsystem.

Recommended next path: only run the columnar reprojection/sort probe if the
owner wants a small bounded win. Otherwise stop this optimization line at the
current honest product state.
