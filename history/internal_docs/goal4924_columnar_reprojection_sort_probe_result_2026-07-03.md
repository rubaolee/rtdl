# Goal4924 Columnar Reprojection/Sort Probe Result

Date: 2026-07-03

## Verdict

`goal4924_correct_but_not_fast_stop_path`

The probe produced byte-equal output and reduced the reprojection/sort region,
but it missed the hard performance bars. This line should not continue as a
Python/Numba micro-optimization path.

## Files

Implementation:

- `history/internal_docs/goal4924_columnar_reprojection_sort_probe.py`
- `history/internal_docs/goal4924_workspace_api_smoke.py`
- `history/internal_docs/goal4924_order_diff_probe.py`

Plan / checklist:

- `history/internal_docs/goal4924_columnar_reprojection_sort_probe_2026-07-03.md`
- `history/internal_docs/rayjoin_hot_path_numba_reachability_checklist_2026-07-03.md`

Evidence:

- `history/internal_docs/goal4924_order_diff_after_gcd_summary_2026-07-03.json`
- `history/internal_docs/goal4924_scaled_int_gcd_summary_2026-07-03.json`
- `history/internal_docs/goal4924_workspace_scaled_int_hooked_summary_2026-07-03.json`
- `history/internal_docs/goal4924_workspace_scaled_int_hooked_rerun_summary_2026-07-03.json`

## Scope

Goal4924 stayed inside the internal RayJoin reproduction experiment harness. It
did not edit:

- `src/rtdsl/**`
- `src/native/**`
- public docs/tutorials/examples
- release surface

The route remains:

- public RTDL planar-map LSI primitive;
- public RTDL planar-map point-location/PIP primitive;
- app-layer RayJoin output assembly;
- Numba app continuation from Goal4886;
- no `rtdsl.rayjoin_overlay` import.

## What Was Implemented

The probe replaced two app-layer functions:

1. `intersection_rows_from_pairs`
2. `sort_xsects_for_map`

The original implementation used `fractions.Fraction` objects in reprojection
and rational sort keys. Goal4924 tried to avoid `Fraction` object materialization
by storing reduced integer numerator/denominator parts on each intersection row,
then using scaled integer sort keys.

The first attempt was wrong in two ways:

1. I foolishly pre-scaled the full dataset's edge arrays during sort. On the
   Australia representative left dataset this touched about 14.4 million edges
   even though only 13,452 intersections existed, making sort map0 take about
   39 seconds. This was an implementation error and was fixed by scaling only
   the edge ids that actually have intersections.
2. I initially skipped `Fraction` reduction. That changed scaled coordinates by
   plus/minus one in many rows because the original `Fraction` route reduces
   huge numerator/denominator pairs before float conversion. This was fixed by
   applying `math.gcd` reduction before internal-coordinate conversion.

After those fixes, the diff probe showed:

- 13,452 rows compared.
- no reprojection row mismatches.
- no map0/map1 order mismatches for `scaled_int`.
- no map0/map1 order mismatches for `exact_cmp`.

## POD Runs

POD:

`root@157.157.221.29 -p 23132`

Worktree:

`/workspace/goal4894_productize_20260703b`

Dataset:

- left: `/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb`
- right: `/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb`
- AuthorOfficial output: `/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt`

### Correctness

All corrected full overlay runs were byte-equal to AuthorOfficial:

- SHA256: `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`
- bytes: `6,189,260`
- lines: `276,320`

The earlier no-reduction and unbounded-scale attempts were rejected and are not
counted as successful evidence.

## Performance Result

Baseline from Goal4915 repeat 1:

| Metric | Goal4915 repeat 1 |
|---|---:|
| hot body elapsed | `3.831950969994068s` |
| intersection reprojection | `0.4678172171115875s` |
| sort map0 | `0.21089166402816772s` |
| sort map1 | `0.20555810630321503s` |
| reprojection + sort total | `0.884267s` |
| output writer | `1.7631013467907906s` |
| byte-equal | true |

Goal4924 corrected non-workspace run:

| Metric | Goal4924 non-workspace corrected |
|---|---:|
| intersection reprojection | `0.43782900273799896s` |
| sort map0 | `0.05924870818853378s` |
| sort map1 | `0.05474625527858734s` |
| reprojection + sort total | `0.551824s` |
| byte-equal | true |

Goal4924 workspace-hot hooked rerun:

| Metric | Repeat 1 | Repeat 2 |
|---|---:|---:|
| hot body elapsed | `3.7896701246500015s` | `4.637891918420792s` |
| intersection reprojection | `0.44229086488485336s` | `0.43201877921819687s` |
| sort map0 | `0.06003698706626892s` | `0.09940779209136963s` |
| sort map1 | `0.05627947300672531s` | `0.05594277381896973s` |
| reprojection + sort total | `0.558607s` | `0.587369s` |
| output writer | `2.0499158799648285s` | `2.841079458594322s` |
| byte-equal | true | true |

## Hard-Bar Evaluation

Original bar:

- `reprojection + sort <= 0.45s`
- hot body `<= 3.45s`
- byte-equal required

Result:

- byte-equal: pass
- reprojection + sort: fail (`~0.55-0.59s`, not `<=0.45s`)
- hot body: fail (`best stable workspace-hot repeat: 3.7897s`, not `<=3.45s`)

Therefore Goal4924 is a correct but insufficient optimization.

## Technical Interpretation

The sort improvement is real:

- map0/map1 sort fell from about `0.416s` total to about `0.11-0.16s`.

The reprojection phase did not improve enough:

- it remained about `0.43-0.44s`.
- exact author-compatible scaled coordinates require arbitrary-precision integer
  arithmetic and `gcd` reduction to preserve byte equality.
- this shape is not a good Numba target, because Numba cannot cheaply compile
  Python arbitrary-precision integer semantics.

That is the key result: the remaining reprojection correctness contract is not
just ordinary numeric vector math. It contains exact rational/integer behavior.
The fast path can remove `Fraction` object allocation, but it cannot turn the
phase into a simple Numba array loop without losing correctness.

## What This Means

This goal confirms the earlier checklist:

- Numba already helped where the app continuation was simple numeric logic.
- The remaining writer is not Numba-friendly.
- Reprojection/sort had one small win, but not enough to justify a new product
  path.
- Further Python/Numba micro-optimization is likely a looks-busy trap.

The right next decision is not "try another small Python tweak." The remaining
choices are:

1. stop RayJoin performance work at the current honest state;
2. pursue a separately reviewed compiled output writer, while admitting the
   app-output-specific risk;
3. pursue the broader dataflow-to-kernel pushdown research line on a non-RayJoin
   workload where the remaining cost is traversal/reduce rather than text output.

## Non-Authorization

This result does not authorize:

- a broad RTDL performance claim;
- a claim that Numba can close the RayJoin performance gap;
- productizing the Goal4924 wrapper;
- changing RTDL core for RayJoin output formatting;
- raw OptiX callback exposure;
- full eight-pair Section 5.7 paper claim.

## Decision Audit

Was this decision foolish? No. The goal was a bounded measurement/implementation
probe against a named phase, with byte equality and hard stop bars.

What was foolish during execution? The first sort implementation pre-scaled the
entire dataset instead of only intersection-bearing edge ids. That was caught by
timing immediately, fixed, and not used as final evidence. The first no-Fraction
implementation also failed to reduce numerator/denominator pairs before float
conversion; the diff probe exposed the plus/minus-one coordinate drift, and the
fix made the probe byte-equal.

Could another path avoid that foolishness? Yes: the order-diff probe should have
been written before the first full overlay run. Future optimization probes should
begin with a local semantic-equivalence diff before full output generation.

Should we try a different path now? Yes. Stop this micro-optimization line and
return to the owner-level architecture decision from Goal4917.
