# Goal4860: Repair Public Planar-Map LSI Row Materialization

Date: 2026-07-02

## Purpose

Repair the LSI row-surface gap exposed by Goal4859 so Section 5.7 can continue
from correct intersection rows rather than scalar counts only.

This goal belongs to Section 5.2, because it concerns LSI row materialization.
It is not a Section 5.3/PIP goal.

## Starting Evidence

Goal4859 found:

- public planar-map LSI scalar count works;
- raw segment-pair rows are not the same contract;
- hidden-predicate row materialization still misses rows;
- a three-segment minimal witness reproduces `count=2, rows=0`.

Primary files:

- `history/internal_docs/goal4859_section57_lsi_row_surface_gap_report_2026-07-02.md`
- `history/internal_docs/goal4859_minimal_real_witness_probe_summary.json`
- `history/internal_docs/goal4859_au_chunk_mismatch_locator_summary.json`
- `history/internal_docs/goal4859_county_zipcode_correct_input_hidden_predicate_lsi_rows_summary.json`

## Work Items

1. Add a focused failing regression test for the minimal real witness:
   - base segment ids `14110870`, `14387225`;
   - query segment id `640`;
   - expected planar-map LSI row count `2`.

2. Inspect and repair the row materialization route:
   - scalar count path currently emits `2`;
   - row path currently emits `0`;
   - the repaired row path must use the same planar-map LSI contract as the
     scalar path.

3. Keep the repair generic:
   - do not introduce a RayJoin application kernel;
   - do not special-case Australia/County/Zipcode;
   - implement a planar-map LSI row contract.

4. Re-run focused gates:
   - minimal witness: rows `2`;
   - existing small synthetic count-vs-row cases: all pass;
   - Australia representative: rows `13622`;
   - correct County x Zipcode input: rows `961165`.

5. Document remaining limits:
   - whether row coordinates are sufficiently exact for Section 5.7 output-chain
     byte equality;
   - whether additional rational/scaled coordinate fields are needed by the app
     layer.

## Exit Criteria

Goal4860 passes only if:

- minimal witness `count == rows == 2`;
- Australia representative `count == rows == 13622`;
- correct County x Zipcode input `count == rows == 961165`;
- no PIP/5.3 or Section 5.7 performance claim is made.

## Review Requirement

Because this goal may touch RTDL native/runtime code, it requires external
review before closure.
