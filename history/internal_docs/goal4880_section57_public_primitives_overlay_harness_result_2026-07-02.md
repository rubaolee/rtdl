# Goal4880: Parameterized Section 5.7 Public RTDL Overlay Harness

Date: 2026-07-02

Status: `completed_pending_external_review`

## Purpose

Goal4880 turns the successful Goal4875 Australia-specific public RTDL overlay
route into a parameterized harness that can be reused by the next
representative Section 5.7 pairs.

The harness must preserve the important boundary from Goal4875:

- public RTDL planar-map LSI primitive;
- public RTDL point-location/PIP primitive;
- Python application-layer overlay assembly;
- no `rtdsl.rayjoin_overlay` import;
- exact-old versus representative-current-source label passed explicitly;
- no fake Numba or performance claim.

## Harness

New file:

```text
history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py
```

It is derived from the byte-equal Goal4875 route, but now takes:

```text
--left
--right
--author-output
--output
--summary
--pair-name
--dataset-label
--swap-query-map-ids
```

The algorithmic route was not changed. The change is harness generalization and
claim metadata cleanup.

## Smoke Test

POD input:

```text
/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb
/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb
```

AuthorOfficial output:

```text
/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt
```

POD command shape:

```text
python3 goal4880_section57_public_primitives_overlay_harness.py \
  --left lakes_Australia_current_osm_Point.cdb \
  --right parks_Australia_current_osm_Point.cdb \
  --author-output author_contract_au_overlay.txt \
  --output rtdl_public_overlay.txt \
  --summary summary.json \
  --pair-name LKAU_x_PKAU_current_osm_smoke \
  --dataset-label representative_current_source
```

Artifacts copied back:

```text
history/internal_docs/goal4880_section57_harness_smoke/summary.json
history/internal_docs/goal4880_section57_harness_smoke/stdout.json
history/internal_docs/goal4880_section57_harness_smoke/stderr.log
```

## Result

The parameterized harness reproduced the Goal4875 Australia representative
output byte-for-byte:

| Field | Generated | AuthorOfficial |
|---|---:|---:|
| Lines | 276,320 | 276,320 |
| Bytes | 6,189,260 | 6,189,260 |
| SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |

Summary flag:

```json
"byte_equal_to_author": true
```

## Route Evidence

Summary fields:

```json
"schema": "rtdl.goal4880.section57_public_primitives_overlay_harness.v1",
"pair_name": "LKAU_x_PKAU_current_osm_smoke",
"dataset_label": "representative_current_source",
"bundled_rayjoin_overlay_imported": false,
"public_lsi_used": true,
"public_point_location_used": true,
"numba_on_correctness_critical_path": false,
"exact_old_paper_input_claim": false
```

Important phase values:

| Phase | Seconds |
|---|---:|
| load/pack left | 71.937 |
| load/pack right | 5.727 |
| public LSI rows | 5.694 |
| vertex PIP map0 in map1 | 10.737 |
| vertex PIP map1 in map0 | 1.556 |
| output-chain write | 17.259 |
| total elapsed | 118.497 |

These are smoke timings only. They do not authorize performance claims.

## What This Proves

Goal4880 proves that the Goal4875 route was not just a hard-coded Australia
script. The same public RTDL overlay route is now parameterized and can be used
by Goal4881 for South America.

## What This Does Not Prove

This does not prove:

- South America correctness;
- full eight-pair Section 5.7 reproduction;
- exact old hidden-input reproduction for regenerated data;
- a performance claim;
- a Numba-critical-path claim;
- an Embree result.

## Decision Audit

1. **Was there a stupid failure mode here?**
   Yes: downloading a new large continent before proving the harness can
   reproduce the already-passed Australia route would be premature.

2. **What action would make that decision stupid?**
   Treating Goal4875 as already generalized without running it through a
   parameterized command and byte-equality smoke.

3. **Is there another path that avoids being stuck?**
   Yes: parameterize first, smoke on known inputs, only then acquire/run South
   America.

4. **Can we start a better path now?**
   Yes. Goal4881 can use this harness on South America representative data.

## Exit Label

`completed_section57_parameterized_public_overlay_harness__australia_smoke_byte_equal`
