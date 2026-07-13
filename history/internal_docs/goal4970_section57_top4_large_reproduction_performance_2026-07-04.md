# Goal4970 Section 5.7 Large Representative Reproduction And Performance

## Scope

This run is the large Section 5.7 reproduction/performance pass requested after the public sample work.

It is **not** a claim that the hidden/exact original eight Section 5.7 CDB pairs are present on the current POD. They are not. The run uses a regenerated **same-source representative** `County x Zipcode` input from the public ArcGIS sources:

- states: `TX`, `CA`, `NY`, `PA`
- label: `top4_county_zipcode_arcgis_same_source`
- dataset type: `representative_current_source`, not `exact_old_paper_input`
- route boundary: public RTDL planar-map primitives plus RayJoin paper app code; no `rtdsl.rayjoin_overlay` bundled-helper route

## Input

Artifact: `history/internal_docs/goal4970_section57_top4_large_reproduction_artifacts_2026-07-04/goal4970_top4_cdb_summary.json`

| Side | Features | Chains | Points | Edges | CDB bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| County top4 | 441 | 1,612 | 1,706,639 | 1,705,027 | 59,780,073 |
| Zipcode top4 | 7,035 | 10,144 | 9,993,104 | 9,982,960 | 350,084,995 |

## Correctness

AuthorOfficial output:

- remote path: `/root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_runs/goal4970_top4_matrix/author_official_section57_overlay.txt`
- bytes: `139,098,488`
- SHA256: `076227b072340e754b7f2cb54de3c37d8054e2a393e87fdb8a4f7368a297b690`

RTDL text route:

- byte-equal to AuthorOfficial: `true`
- bytes: `139,098,488`
- SHA256: `076227b072340e754b7f2cb54de3c37d8054e2a393e87fdb8a4f7368a297b690`

RTDL Numba/text route:

- byte-equal to AuthorOfficial: `true`
- bytes: `139,098,488`
- SHA256: `076227b072340e754b7f2cb54de3c37d8054e2a393e87fdb8a4f7368a297b690`

RTDL binary/device-columnar route:

- does not emit the paper text sink, so it does not make a byte-equality claim
- `lsi_row_count`: `428,322`
- `xsect_sorted_counts`: side0 `428,322`, side1 `428,322`
- vertex positive counts: side0-in-side1 `812,721`, side1-in-side0 `4,527,305`
- device sort order validation against CPU longdouble reference: `true` for both sides

## Performance Table

All numbers are from the POD run at `root@213.173.108.15`, artifacts copied into:
`history/internal_docs/goal4970_section57_top4_large_reproduction_artifacts_2026-07-04/`

| Route | Correctness gate | Main wall / hot number | Meaning |
| --- | --- | ---: | --- |
| AuthorOfficial text dump | reference output | `116.209s` wall | Includes reading maps, building RT pipeline, overlay compute, text output. |
| RTDL public text route | byte-equal | `77.368s` route elapsed | Uses public LSI/PIP primitives plus Python app writer. Faster total wall here mainly because RTDL uses packed CDB cache while Author rereads large CDBs. |
| RTDL public Numba/text route | byte-equal | `70.171s` route elapsed | Same text output, with Numba app-layer helpers. Improves writer/continuation part but does not fix Python reprojection/sort. |
| RTDL binary/device-columnar fresh | numeric/order gates | `7.757s` writer-free hot | No paper text writer. Includes fresh LSI rows plus device-columnar reprojection/sort/group and PIP phases. |
| RTDL binary/device-columnar prepared replay | numeric/order gates | `3.204s` writer-free hot | Diagnostic prepared replay: excludes LSI session/workspace preparation as reusable state. Not a fresh overlay claim. |

## Author Phase Breakdown

From `author_official.stderr.txt`:

| Author phase | Seconds |
| --- | ---: |
| Read map 0 | `15.288` |
| Read map 1 | `88.429` |
| Load Data | `2.737` |
| Init + Build Index | `0.167` |
| Intersection edges | `0.007` |
| Map 0 locate vertices | `0.015` |
| Map 1 locate vertices | `0.058` |
| Compute output polygons | `0.104` |
| Write to file | `9.082` |

The author overlay compute core excluding map read and text file write is roughly:

`0.007 + 0.015 + 0.058 + 0.104 = 0.184s`

So the honest compute comparison is:

- RTDL binary fresh writer-free hot: `7.757s` vs Author compute `~0.184s` -> about `42x` slower.
- RTDL prepared replay writer-free hot: `3.204s` vs Author compute `~0.184s` -> about `17x` slower, but this excludes LSI preparation/reuse costs and is not a fresh overlay claim.

## RTDL Phase Detail

RTDL text route highlights:

- LSI public rows: `4.506s`
- intersection reprojection: `15.597s`
- sort map0 + map1: `13.894s`
- vertex PIP total: `0.878s`
- output-chain writer: `35.427s`
- total route elapsed: `77.368s`

RTDL Numba/text route highlights:

- LSI public rows: `4.448s`
- intersection reprojection: `15.694s`
- sort map0 + map1: `13.905s`
- vertex PIP total: `0.883s`
- output-chain writer: `27.529s`
- total route elapsed: `70.171s`

RTDL binary/device-columnar fresh highlights:

- LSI public rows: `4.067s`
- device-columnar reprojection: `0.255s`
- device-columnar sort map0 + map1: `0.130s`
- vertex PIP total: `1.991s`
- midpoint point materialization: `1.172s`
- compiled grouped carrier construction: `0.110s`
- writer-free hot total: `7.757s`

This is the important result: device-columnar numeric work collapses the reprojection/sort region from roughly `29.5s` in the text routes to roughly `0.385s` in the binary route. That is a real Layer 1/2 gain. It still does not close the author compute gap because the remaining fresh cost is dominated by LSI rows and other app-level materialization.

RTDL prepared replay highlights:

- LSI session prepare: `1.620s`
- LSI workspace prepare: `2.251s`
- prepared LSI replay rows: `0.008s`
- writer-free hot total: `3.204s`

This is useful for amortized pipeline scenarios, but it must not be compared as a fresh overlay number.

## Interpretation

1. The large representative 5.7 correctness gate passed for text output:
   RTDL public text and RTDL Numba/text are byte-equal to AuthorOfficial on a 139MB top4 output.

2. RTDL total text wall looks better than Author total wall in this run, but that is not a clean compute win:
   Author spends about `103.7s` just reading the two large CDB maps. RTDL uses a packed CDB cache and reads in about `0.06s` on the repeated routes.

3. The useful compute comparison is writer-free binary vs Author overlay compute:
   RTDL fresh binary is about `42x` slower than Author compute on this top4 representative input.

4. The Layer 1/2 device-columnar work is real:
   it turns the Python reprojection/sort bottleneck from about `29.5s` into about `0.385s`.

5. The remaining performance gap is not the text writer anymore in the binary route.
   The next hard bottleneck is exact LSI row production and other intermediate materialization. Closing that requires the planned exact LSI device-column route / stronger resident pipeline, not more text-writer tuning.

## Bottom Line

For Section 5.7 large representative reproduction:

- Correctness: **passed** for text routes against AuthorOfficial.
- Numba/text: **small useful improvement** over RTDL text, mostly in writer/continuation, not in reprojection/sort.
- Binary/device-columnar: **large real numeric-pipeline improvement**, but still far from Author compute on fresh overlay.
- Prepared replay: **fast diagnostic/amortized route**, not a fresh overlay claim.

The next optimization target is clear: keep the binary operator framing, then attack exact LSI/device-column production and remaining resident materialization. Do not spend more time pretending text-writer performance is the core RTDL value.
