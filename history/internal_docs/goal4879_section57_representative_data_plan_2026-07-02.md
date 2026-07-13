# Goal4879: Section 5.7 Representative Data Plan

Date: 2026-07-02

Status: `completed_pending_external_review`

## Purpose

Goal4879 defines how to continue RayJoin Section 5.7 after the exact old
paper-preprocessed CDBs for the six Lakes/Parks continent pairs were not found
on the current POD.

The user/author has allowed a representative route:

```text
Use public/current-source data processed with the author-compatible workflow,
label it honestly, and do not pretend it is the hidden old paper input.
```

This goal does not run a new pair. It chooses the next pair(s), records the
source and preprocessing plan, and prevents claim confusion.

## Current Proven State

Completed bounded/full-stream Section 5.7 pairs:

| Pair | Current status | Label |
|---|---|---|
| County x Zipcode | full-stream exact match | available pair, bounded |
| Block x Water | full-stream exact match under AuthorOfficial | available pair, bounded |
| Australia Lakes x Parks | byte-equal representative current-OSM public-primitive route | representative, not exact old paper CDB |

The completed Australia representative route is the template:

- public RTDL LSI primitive;
- public RTDL point-location/PIP primitive;
- Python application-layer overlay assembly;
- no `rtdsl.rayjoin_overlay` import;
- AuthorOfficial comparator;
- no Numba critical-path claim.

## Exact vs Representative Rule

Two labels must remain separate:

| Label | Meaning |
|---|---|
| `exact_old_paper_input` | The exact old paper-preprocessed CDB and answer/comparator output are present. |
| `representative_current_source` | A current/regenerated public-source dataset was processed with author-compatible rules. Useful for engineering and reproduction, but not the old hidden input. |

All remaining Lakes/Parks continent work in this plan is
`representative_current_source` unless the exact old CDBs are later provided.

## Pair Plan

Manifest:

```text
history/internal_docs/goal4879_section57_representative_data_manifest_2026-07-02.json
```

| Pair | Status | Planned action |
|---|---|---|
| LKAU x PKAU | completed representative | Keep as the first accepted current-OSM Lakes/Parks representative. |
| LKSA x PKSA | selected next | Regenerate South America Lakes/Parks from current public OSM and run the Goal4880 harness. |
| LKAF x PKAF | backup after South America | Use if South America acquisition/preprocessing fails or a second additional pair is needed. |
| LKAS x PKAS | deferred | Possible but high resource cost. |
| LKEU x PKEU | deferred | Very high resource cost. |
| LKNA x PKNA | deferred | High resource cost. |

## Why South America Next

South America is selected as the next representative pair because prior audit
estimated its current Geofabrik PBF around `3.8 GB`, making it the smallest
practical remaining continent after already-completed Australia/Oceania.

It is large enough to test a second non-US Lakes/Parks representative shape, but
not so large that we burn the next day on Europe or North America before the
generalized harness is proven again.

Africa is the backup: larger, but still more practical than Asia, Europe, or
North America.

## Planned Preprocessing Contract

For South America and later representatives:

1. Download or reuse the current Geofabrik continent PBF.
2. Extract lake/water polygons:

   ```text
   osmium tags-filter <continent>.osm.pbf natural=water water=lake
   ```

3. Extract park/national-park polygons:

   ```text
   osmium tags-filter <continent>.osm.pbf leisure=park boundary=national_park
   ```

4. Export polygon GeoJSONSeq.
5. Convert to CDB using the existing `goal4848_geojsonseq_to_cdb.py` route.
6. Run AuthorOfficial overlay and public RTDL overlay harness.
7. Require byte equality before any performance/phase timing.

The exact tag expression may need a small preprocessing smoke check against the
Australia route so that South America does not silently use a different
feature-selection rule.

## Next Goal

Goal4880 should not immediately download a huge continent. It should first
generalize the already successful Goal4875 Australia public route into a
parameterized harness and smoke it on the existing Australia inputs.

Only after Goal4880 passes should Goal4881 acquire/run South America.

## What This Does Not Authorize

This plan does not authorize:

- calling current OSM regenerated data exact old paper input;
- claiming full eight-pair old-paper Section 5.7 reproduction;
- running performance before byte equality;
- using V3/V4 language;
- using Embree;
- claiming Numba is used when it is not on the critical path.

## Decision Audit

1. **Was there a stupid failure mode here?**
   Yes: trying to chase all six missing old CDBs again before exploiting the
   representative route the user already authorized.

2. **What action would make that decision stupid?**
   Downloading the largest continent first, or pretending regenerated current
   data is exact old paper data.

3. **Is there another path that avoids being stuck?**
   Yes: keep exact-old and representative labels separate, choose the smallest
   useful next representative, and prove the generalized harness before
   increasing scale.

4. **Can we start a better path now?**
   Yes. Goal4880 should parameterize the public RTDL overlay harness on the
   existing Australia pair; Goal4881 should then run South America.

## Exit Label

`completed_section57_representative_data_plan__south_america_next__africa_backup`
