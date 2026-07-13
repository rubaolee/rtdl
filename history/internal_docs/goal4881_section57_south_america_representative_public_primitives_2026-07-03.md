# Goal4881: Section 5.7 South America Representative Public-Primitives Reproduction

Date: 2026-07-03

## Goal

Run the Goal4880 public RTDL Section 5.7 overlay harness on one additional lakes/parks representative pair beyond Australia:

- Pair: `LKSA x PKSA`
- Source: current public Geofabrik South America OSM extract
- Baseline: `AuthorOfficial` (`Author+RTDLContractPatch`)
- RTDL route: public planar-map LSI + public planar-map point-location/PIP + application-layer output-chain writer

This is a representative current-source reproduction. It is not an exact old hidden paper-input claim.

## Source And Preprocessing

Downloaded source on POD:

```text
/workspace/goal4881_section57_south_america/source/south-america-latest.osm.pbf
sha256: 8a21e105180c92ac35bed227af08eaee99add50185ab9730a8095b0ccbf39899
```

The source PBF was the Geofabrik South America extract redirected to `south-america-260702.osm.pbf`.

The same representative extraction rules as the Australia route were used:

```bash
osmium tags-filter -O -o lakes.filtered.osm.pbf south-america-latest.osm.pbf \
  w/natural=water r/natural=water

osmium tags-filter -O -o parks.filtered.osm.pbf south-america-latest.osm.pbf \
  w/leisure=park r/leisure=park w/boundary=national_park r/boundary=national_park

osmium export -O --geometry-types=polygon -f geojsonseq -o lakes.geojsonseq lakes.filtered.osm.pbf
osmium export -O --geometry-types=polygon -f geojsonseq -o parks.geojsonseq parks.filtered.osm.pbf
```

The existing converter was reused:

```text
history/internal_docs/goal4848_geojsonseq_to_cdb.py
```

## Full South America Attempt

The full current-source South America CDBs were generated first:

| Input | features | chains | points | size |
| --- | ---: | ---: | ---: | ---: |
| lakes | 762,256 | 881,998 | 46,415,821 | 1.3GB |
| parks | 198,031 | 202,597 | 3,480,312 | 98MB |

The full run was stopped before accepting evidence because the full lakes text CDB was much larger than the old paper LKSA scale and the AuthorOfficial path spent several minutes in text-CDB parsing before reaching the useful overlay stages. Keeping the full intermediate files also hit the POD workspace write quota during the first bounded attempt.

This was not treated as a correctness failure. It was treated as an execution-control problem. The source sha and bounded CDB summaries preserve provenance; the full transient PBF/GeoJSONSeq/full CDB intermediates were deleted after bounded CDB generation to restore write capacity.

## Bounded Representative Slice

To keep the experiment controlled, the South America current-source GeoJSONSeq files were converted to a bounded representative slice:

| Input | max features | chains | points | CDB size |
| --- | ---: | ---: | ---: | ---: |
| lakes | 150,000 | 159,346 | 7,216,938 | 195MB |
| parks | 50,000 | 50,487 | 654,694 | 19MB |

Remote CDB paths:

```text
/workspace/goal4881_section57_south_america/cdb_bounded_150k_50k/lakes_South_America_current_osm_bounded150k_Point.cdb
/workspace/goal4881_section57_south_america/cdb_bounded_150k_50k/parks_South_America_current_osm_bounded50k_Point.cdb
```

Local copied summaries:

```text
history/internal_docs/goal4881_section57_south_america_bounded/lakes_bounded_summary.json
history/internal_docs/goal4881_section57_south_america_bounded/parks_bounded_summary.json
```

## AuthorOfficial Baseline

Command shape:

```bash
/workspace/RayJoin_goal4834_patched_author/release/bin/polyover_exec \
  -poly1 lakes_South_America_current_osm_bounded150k_Point.cdb \
  -poly2 parks_South_America_current_osm_bounded50k_Point.cdb \
  -serialize=/workspace/goal4881_section57_south_america/serialize_author_sa_bounded_clean \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false \
  -output author_official_sa_bounded_overlay.txt
```

Result:

| Metric | Value |
| --- | ---: |
| output lines | 97,893 |
| output bytes | 2,096,449 |
| sha256 | `8b4e80a50fedb77120781e8bf39c9f2db1df3a1f823716f7dab9c1f9eed1862d` |

AuthorOfficial timing excerpt:

| Phase | Time |
| --- | ---: |
| Read map 0 | 70.917s |
| Read map 1 | 6.832s |
| Load Data | 1.838s |
| Build Index | 15.699ms |
| Intersection edges | 2.516ms |
| Map 0 PIP | 12.453ms |
| Map 1 PIP | 3.761ms |
| Compute output polygons | 36.005ms |
| Write to file | 379.418ms |

Artifact:

```text
history/internal_docs/goal4881_section57_south_america_bounded/author_official_sa_bounded_overlay_summary.json
history/internal_docs/goal4881_section57_south_america_bounded/author_official_sa_bounded_overlay.log
```

## Public RTDL Harness Result

Harness:

```text
history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py
```

Route:

```text
public_planar_map_lsi_and_point_location_plus_python_app_overlay_writer
```

Claim-boundary flags from the harness:

```json
{
  "broad_performance_claim": false,
  "bundled_rayjoin_overlay_imported": false,
  "dataset_label": "representative_current_source",
  "exact_old_paper_input_claim": false,
  "full_eight_pair_paper_claim": false,
  "numba_on_correctness_critical_path": false,
  "public_lsi_used": true,
  "public_point_location_used": true
}
```

Result:

| Metric | AuthorOfficial | Public RTDL |
| --- | ---: | ---: |
| output lines | 97,893 | 97,893 |
| output bytes | 2,096,449 | 2,096,449 |
| sha256 | `8b4e80a50fedb77120781e8bf39c9f2db1df3a1f823716f7dab9c1f9eed1862d` | `8b4e80a50fedb77120781e8bf39c9f2db1df3a1f823716f7dab9c1f9eed1862d` |
| byte-equal | - | true |

Public RTDL phase timings:

| Phase | Seconds |
| --- | ---: |
| load/pack left | 33.973 |
| load/pack right | 3.663 |
| public LSI rows | 3.863 |
| vertex PIP map0 in map1 | 4.909 |
| vertex PIP map1 in map0 | 0.851 |
| midpoint PIP map0 | 0.035 |
| midpoint PIP map1 | 0.048 |
| output-chain write | 8.465 |
| total harness elapsed | 58.385 |

Other correctness-relevant counters:

| Counter | Value |
| --- | ---: |
| LSI rows | 1,856 |
| map0 xsects | 1,856 |
| map1 xsects | 1,856 |
| map0 vertex positives in map1 | 84,944 |
| map1 vertex positives in map0 | 5,574 |
| output chains | 3,909 |
| output faces | 1,880 |
| output points | 93,984 |

Artifact:

```text
history/internal_docs/goal4881_section57_south_america_bounded/rtdl_public_sa_bounded_overlay_summary.json
history/internal_docs/goal4881_section57_south_america_bounded/rtdl_public_sa_bounded_overlay.log
```

## What This Proves

This proves a second lakes/parks representative Section 5.7 route beyond Australia:

- The RTDL public-primitives route can reproduce AuthorOfficial byte-for-byte on a South America current-source bounded slice.
- The route did not import bundled `rtdsl.rayjoin_overlay`.
- The route used public planar-map LSI and public planar-map point-location/PIP primitives.
- The result is a real overlay-output equality result, not a count-only LSI/PIP result.

## What This Does Not Prove

This does not prove:

- Exact old Section 5.7 hidden-paper LKSA x PKSA input reproduction.
- Full eight-pair Section 5.7 reproduction.
- Broad RTDL performance superiority.
- A Numba-critical correctness route. Numba is not on this correctness-critical path.
- That the full current-source South America extract is practical through text-CDB first-load without better dataset staging/cache management.

## Goal-Level Decision Audit

1. Was the decision to stop the full South America run stupid?
   - No. Continuing the full current-source run after seeing 46.4M lake points, slow text-CDB parse, and workspace write quota pressure would have risked a looks-busy-but-low-signal hole.

2. What action prevented stupidity?
   - I preserved provenance, deleted only transient full intermediates after bounded CDBs were produced, and moved to a bounded same-source slice with explicit labeling.

3. Was there another path?
   - Yes: keep forcing the full current-source route. That would be useful later only after durable dataset/cache handling is improved, not as the next proof step.

4. Does the current path solve the real problem?
   - Yes for the bounded representative goal: it tests the same public RTDL LSI/PIP/output-chain route against AuthorOfficial and obtains byte equality on a non-Australia lakes/parks pair.

## Exit Label

Recommended exit label:

```text
completed_section57_south_america_bounded_representative_public_primitives_byte_equal
```
