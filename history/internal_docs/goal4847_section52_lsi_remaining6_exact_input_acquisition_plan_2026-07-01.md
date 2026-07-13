# Goal4847 - RayJoin Section 5.2 Remaining Six LSI Pairs

Date: 2026-07-01

## Objective

Acquire or prove unavailable the six missing RayJoin Section 5.2 lakes/parks exact CDB input pairs, then run AuthorPatch-vs-RTDL LSI correctness for every acquired pair.

This goal continues Goal4846. Goal4846 completed the two currently available pairs:

| Pair | AuthorPatch LSI | RTDL LSI | Delta |
|---|---:|---:|---:|
| County x Zipcode | 961165 | 961165 | 0 |
| Block x Water | 649605 | 649605 | 0 |

## Remaining Six Pairs

| # | Pair | Required left CDB | Required right CDB |
|---:|---|---|---|
| 1 | LKAF x PKAF | `point_cdb/lakes/Africa/lakes_Africa_Point.cdb` | `point_cdb/parks/Africa/parks_Africa_Point.cdb` |
| 2 | LKAS x PKAS | `point_cdb/lakes/Asia/lakes_Asia_Point.cdb` | `point_cdb/parks/Asia/parks_Asia_Point.cdb` |
| 3 | LKAU x PKAU | `point_cdb/lakes/Australia/lakes_Australia_Point.cdb` | `point_cdb/parks/Australia/parks_Australia_Point.cdb` |
| 4 | LKEU x PKEU | `point_cdb/lakes/Europe/lakes_Europe_Point.cdb` | `point_cdb/parks/Europe/parks_Europe_Point.cdb` |
| 5 | LKNA x PKNA | `point_cdb/lakes/North_America/lakes_North_America_Point.cdb` | `point_cdb/parks/North_America/parks_North_America_Point.cdb` |
| 6 | LKSA x PKSA | `point_cdb/lakes/South_America/lakes_South_America_Point.cdb` | `point_cdb/parks/South_America/parks_South_America_Point.cdb` |

## Hard Rules

- Do not call regenerated/same-source CDBs exact paper inputs.
- Do not use V3/V4 artifacts or claims.
- Do not use Embree.
- Do not change RTDL runtime unless an acquired pair exposes a reviewed generic core correctness defect.
- Correctness before performance: every timing row must include the count-match status.
- If exact inputs cannot be acquired from the authoritative source, close the pair as `missing_exact_input_after_source_audit`.

## Execution Plan

### A. Authoritative Source Audit

Check:

1. current POD filesystem;
2. archived local/POD artifact trees;
3. RayJoin paper-reproduction data source recorded in Goal4380:
   `https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA`

Exit gate:

- each required CDB path is either found with byte size and source path, or recorded as missing after source audit.

### B. Acquisition

For every found/downloadable exact CDB:

- place it under a dedicated Goal4847 dataset root preserving the `point_cdb/...` relative path;
- record source URL/path, file size, checksum if practical;
- do not mix with regenerated CDBs.

Exit gate:

- pair status becomes `exact_input_ready` only when both left and right CDBs exist.

### C. Correctness Runs

For each `exact_input_ready` pair:

1. run AuthorPatch `query_exec -query=lsi -mode=rt -warmup=0 -repeat=1`;
2. run RTDL OptiX `run-rtdl --case-id lsi_* --backend optix --warmup 0 --repeat 1`;
3. compare counts.

If counts mismatch:

- dump pair sets;
- compute missing/extra pairs;
- reduce the first discriminating pair to a synthetic reproduction;
- only fix generic candidate/predicate defects after review.

### D. Bounded Performance

Only for correctness-passed pairs:

- report AuthorPatch query timing and RTDL native timing separately;
- do not report broad speedup unless denominator and wrapper overhead are explicit.

## Expected Problems

1. The six exact CDB files may not be in the public Dryad share or may require a different archive file than currently present.
2. Downloads may be large; acquisition should inspect manifests before pulling multi-GB archives.
3. Dataset-root/cache-key matters for AuthorPatch. Use stable relative paths from the dataset root to hit serialized caches.
4. Some pairs may expose new numeric edge cases; use pair-diff immediately, not repeated full runs.

## Completion Labels

- `complete_remaining6_all_acquired_and_correctness_passed`
- `partial_acquired_pairs_pass_missing_inputs_recorded`
- `blocked_missing_exact_inputs_after_source_audit`
- `blocked_by_count_mismatch_with_pair_diff`
