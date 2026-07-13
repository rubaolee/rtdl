# Goal4855 - RayJoin Section 5.3 PIP Three-Dataset Reproduction

Date: 2026-07-01

## Verdict

Goal4855 completed a bounded Section 5.3 PIP reproduction run on the three
available datasets:

1. County x Zipcode
2. Block x Water
3. Australia Lakes x Parks representative

The result is a correctness/coverage reproduction of the Section 5.3 workload
shape using RTDL's directed point-location primitive, not a performance-win
claim.  RTDL did not beat the patched author implementation on hot-query time
in this run.

## Scope

This goal reproduces Section 5.3 PIP Performance only:

```text
query_exec -query=pip -mode=rt -grid_size=15000 -xsect_factor 0.1 -enlarge=3.5
```

The direction follows the author program contract: when `-poly2` is supplied,
the query probes poly2/map1 vertices against poly1/map0.  This is not Section
5.7 polygon overlay, not output-chain reproduction, and not an all-eight-pair
paper claim.

## Implementation Boundary

The runner uses:

- RTDL public primitive: `prepare_directed_segment_point_location_2d_optix`
- A user-side streaming CDB adapter for large inputs
- AuthorPatch baseline: author source with the accepted compatibility/intended
  behavior patch line

The runner does not import `rtdsl.rayjoin_overlay` and does not use the bundled
RayJoin overlay helper.  It does use RTDL's internal packed segment ABI in the
streaming adapter to avoid building huge Python object graphs; this is recorded
as product debt because the public API should expose a vectorized CDB/planar-map
packing path.

Runner:

`history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py`

Artifacts:

`history/internal_docs/goal4855_section53_pip_final_stream/`

## Results

| Pair | Base Segments | Query Points | RTDL Positive Faces | RTDL Chunks | RTDL Count Wall | RTDL Native Traversal | RTDL Prepare | RTDL Base Pack | RTDL CDB Scan | AuthorPatch Query | AuthorPatch Elapsed | Author RC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| County x Zipcode | 8,662,896 | 47,862,092 | 41,352,916 | 96 | 0.798661 s | 0.194739 s | 2.115380 s | 54.347 s | 162.915 s | 110.238 ms | 17.883 s | 0 |
| Block x Water | 28,473,338 | 44,863,618 | 40,523,581 | 90 | 0.802338 s | 0.202930 s | 3.430140 s | 179.658 s | 264.046 s | 116.413 ms | 1641.662 s | 0 |
| Australia Lakes x Parks representative | 14,430,155 | 992,505 | 29,719 | 2 | 1.624150 s | 1.593072 s | 2.413695 s | 40.932 s | 23.619 s | 6.73485 ms | 1.739 s | 0 |

## Interpretation

What this proves:

- RTDL can express and execute the Section 5.3 PIP workload shape using the
  directed point-location primitive and a user-side app runner.
- The three available datasets run to completion on the NVIDIA POD.
- The earlier full-load Python object path was the wrong approach for large CDB
  inputs; the streaming adapter avoids that failure mode.
- County x Zipcode and Block x Water are serious-scale tests, not toy tests.

What this does not prove:

- It does not prove RTDL is faster than AuthorPatch for Section 5.3.
- It does not prove full Section 5.7 polygon-overlay reproduction.
- It does not prove all eight Section 5.3 paper pairs.
- It does not prove byte-level PIP output equivalence, because `query_exec
  -query=pip` does not emit per-point classification output in the captured
  baseline path.  The result is a workload reproduction plus timing comparison,
  not a per-row answer-file comparison.

## Engineering Findings

1. The RTDL hot primitive path works on serious input sizes, but the current
   public/user path is dominated by CDB text scanning and packing.

2. The user-side streaming adapter still reaches into RTDL's packed segment ABI.
   That is acceptable for this internal reproduction goal, but it exposes a
   product gap: RTDL should provide a public vectorized CDB/planar-map packing
   API.

3. AuthorPatch cold input handling can dominate elapsed wall time.  Block x
   Water spent most of its 1641.662 seconds loading/serializing large text CDBs,
   while its hot Query line was 116.413 ms.  Reporting must keep cold input
   elapsed time separate from hot query time.

4. Australia representative is the clearest negative performance signal:
   AuthorPatch hot Query was 6.73485 ms, while RTDL native traversal totaled
   1.593072 s.  This must not be hidden.

## Exit Label

`completed_section53_three_dataset_workload_reproduction__no_performance_win_claim`

Recommended next action: external review.  If approved, close Section 5.3 and
move to the next paper-section reproduction target with the same discipline:
contract first, author source first, exact claim boundaries, and no broad
speedup wording unless the measured evidence supports it.
