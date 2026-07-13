# Goal4845 Section 5.2 LSI AuthorPatch vs RTDL Reproduction Plan

## Objective

Reproduce the RayJoin paper Section 5.2 LSI workloads by comparing:

- **AuthorPatch RayJoin**: author original code plus the accepted compatibility / intended-behavior patches used as the project baseline.
- **RTDL v2.14 line**: current RTDL LSI route over the same CDB inputs and equivalent Section 5.2 parameters.

This goal does **not** compare against Uniform Grid, LBVH, PSSL, GLIN, cuSpatial, PostGIS, Kinetica, RasterJoin, or any other paper baseline. Those are not RTDL's responsibility for this goal.

## Scope

Run LSI only:

- no polygon-overlay output-chain construction,
- no PIP midpoint debugging,
- no Section 5.7 full overlay claim,
- no broad RayJoin-paper speedup claim.

The only question is:

> On Section 5.2 LSI workloads, does RTDL reproduce AuthorPatch LSI correctness, and what is the measured RTDL-vs-AuthorPatch performance on the same hardware and inputs?

## Required Work

1. Read and preserve the Section 5.2 workload contract from the paper:
   - dataset pairs,
   - query type,
   - parameters,
   - timing categories.
2. Inspect author source/scripts for `query_exec -query=lsi -mode=rt`.
3. Inventory which Section 5.2 CDB inputs are actually available on the current POD.
4. Run AuthorPatch and RTDL on available pairs with matching parameters.
5. Record:
   - input pair,
   - input provenance (`exact_paper_cdb` vs `same_source_regenerated_cdb`),
   - AuthorPatch LSI count,
   - RTDL LSI count,
   - count equality,
   - AuthorPatch preprocessing / processing / total time,
   - RTDL pack / build / traversal / materialization / total time,
   - caveats.
6. If a dataset or author baseline is missing, mark it as `missing_input` or `missing_authorpatch_baseline`; do not silently substitute.

## Acceptance Gates

- Correctness is primary: a timing row is usable only if the LSI count/result contract matches or the mismatch is diagnosed.
- Every timing number must include its denominator and source.
- No comparison to paper baselines unless those baselines are actually run in this goal.
- No claim that this completes full Section 5.2 unless all eight Section 5.2 pairs are covered.

## Expected First Output

A bounded table for the currently available Section 5.2 pairs, likely starting with:

- County x Zipcode
- Block x Water, if present

## Current Risk

The current POD may contain only same-source regenerated CDBs, not all exact paper-preprocessed CDBs. In that case, the result must be labeled as same-source reproduction, not exact full-paper reproduction.
