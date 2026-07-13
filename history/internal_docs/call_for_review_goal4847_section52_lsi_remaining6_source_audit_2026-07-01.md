# Call For Review - Goal4847 RayJoin Section 5.2 Remaining Six Source Audit

Date: 2026-07-01

## Requested Verdict Labels

- `approve_goal4847_remaining6_missing_exact_input_after_source_audit`
- `approve_with_required_amendments`
- `block_goal4847_due_to_insufficient_source_audit_or_overclaim`

## Files To Review

- `history/internal_docs/goal4847_section52_lsi_remaining6_exact_input_acquisition_plan_2026-07-01.md`
- `history/internal_docs/goal4847_section52_lsi_remaining6_source_audit_2026-07-01.md`
- `history/internal_docs/goal4846_section52_lsi_results_2026-07-01.md`
- `history/internal_docs/antigravity_goal4846_section52_lsi_8pair_status_review_2026-07-01.md`

## Claim Under Review

Goal4847 should close as:

```text
partial_available_pairs_pass__remaining6_missing_exact_input_after_source_audit
```

Meaning:

- County x Zipcode and Block x Water already passed AuthorPatch-vs-RTDL Section 5.2 LSI correctness in Goals 4845 and 4846.
- The remaining six Lakes/Parks exact CDB pairs are unavailable on the current POD and through the currently known authoritative public source path.
- No RTDL correctness runs were attempted for those six because the exact inputs are absent.

This is not a full 8/8 Section 5.2 claim.

Important clarification: this claim is only about the **exact paper-preprocessed CDB files**. It is not a claim that Lakes/Parks raw data is private or nonexistent. A broader web search confirms SpatialHadoop publicly lists OpenStreetMap-derived Lakes and Parks datasets. Those raw public datasets can support a future `same_source_regenerated_cdb` route, but they do not by themselves prove exact paper-input availability.

## Evidence Summary

### POD exact-input search

Search over `/workspace`, `/data`, and `/root` for all 12 required Lakes/Parks CDB file names returned:

```text
FOUND_COUNT 0
```

### POD raw/archive search

Search for plausible Lakes/Parks raw/source/archive artifacts (`.wkt`, `.shp`, `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.7z`, `.geojson`, `.json`, `.csv`) returned:

```text
FOUND_RAW_OR_ARCHIVE 0
```

### `/dev/shm`

No Lakes/Parks serialized maps exist in `/dev/shm`; only the two U.S. same-source serialized maps are present.

### Author repo

The author README says preprocessed datasets are not provided in the repository and users need to download/process them. The scripts assume:

```text
DATASET_ROOT=/local/storage/liang/Downloads/Datasets
```

and then construct the Lakes/Parks CDB paths. The scripts do not download the data.

### Author logs

The author repo contains historical Lakes/Parks LSI logs with author counts:

| Pair | Author log count |
|---|---:|
| LKAF x PKAF | 4765 |
| LKAS x PKAS | 37333 |
| LKAU x PKAU | 12618 |
| LKEU x PKEU | 278461 |
| LKNA x PKNA | 1251343 |
| LKSA x PKSA | 22383 |

These logs are reference evidence only. They are not input CDBs and cannot prove RTDL correctness.

### Dryad

The preprocessed share:

```text
https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA
```

currently resolves to:

```text
effective_url=https://datadryad.org/404
http_code=404
```

Dryad API searches for `RayJoin` and `RayJoin spatial join` return `count=0,total=0`.

## Questions For Reviewer

1. Is the source audit sufficient to classify the six Lakes/Parks exact CDB pairs as currently unavailable?
2. Does the report correctly separate author logs from executable input data?
3. Does the report correctly avoid calling regenerated or same-source data exact paper input?
4. Is it correct that no RTDL correctness runs should be attempted for the six pairs without exact CDB inputs?
5. Does the report correctly preserve the two available-pair results without promoting them to an 8/8 claim?
6. Is the Dryad 404/API-zero evidence sufficient as a current public-source check?
7. Are there any additional likely exact-input locations that must be checked before closing Goal4847?
8. Should Goal4847 close with `partial_available_pairs_pass__remaining6_missing_exact_input_after_source_audit`, or should more acquisition work be required first?

## Non-Authorization

This review must not authorize:

- full 8/8 Section 5.2 reproduction;
- Section 5.7 overlay reproduction;
- regenerated data being called exact paper input;
- V3/V4 claims;
- Embree claims;
- broad RTDL/RayJoin performance claims;
- using author logs as RTDL correctness evidence.
