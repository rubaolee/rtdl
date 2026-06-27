## Audit Findings

### Severity: Low — URL helper naming mismatch

`build_arcgis_geojson_query_url` in `datasets.py:246` accepts `response_format="json"` and the actual Linux run used `--response-format json`. The function name implies GeoJSON only, but it handles both formats. The script (`goal28b_stage_uscounty_zipcode.py:75`) calls it with the `response_format` arg correctly. No bug, but the name is a mild lie that could confuse future callers.

### Severity: Low — Test coverage gap on Zipcode count

`tests/goal28b_staging_test.py:16` asserts `uscounty_feature_layer.feature_count == 3144` (hardcoded, verified against registry). There is no parallel assertion for `zipcode_feature_layer.feature_count == 32294`. The zipcode test only checks `layer_id == 0`. The 32294 figure appears in both the registry and the doc report but has no test guard.

### Severity: Low — Redundant `sys.path` mutation in script

`goal28b_stage_uscounty_zipcode.py:16-17` inserts `"src"` and `"."` into `sys.path` unconditionally, but the documented invocation already passes `PYTHONPATH=src:.`. Harmless but noisy.

### Severity: Informational — Zipcode service URL inherits upstream typo

`datasets.py:198` has `USA_ZIP_Code_Areas_anaylsis` ("anaylsis" is misspelled). This is the actual upstream Esri service URL typo. The live query confirmed 32294 features, so the URL resolves correctly. This is noted for future navigability — anyone copy-pasting the URL will carry the typo.

### Severity: Informational — `OBJECTID` ordering assumed stable across restarts

Paging uses `orderByFields=OBJECTID` (the default). If the run is interrupted and resumed from a checkpoint, there is no resume/skip logic in the script — it would re-download from offset 0. The report correctly describes the Zipcode run as "intentionally stopped," not resumed. No claim is made about incremental resume capability, so this is not an overstatement — it just means restart = full re-pull.

---

## Verdict

**Closure boundary check:**
- Reproducible staging path in repo: yes — script + documented invocation + manifest
- USCounty fully staged on Linux: yes — offset 3000 with page_size 250 covers 3144 features, directory size plausible
- Zipcode demonstrated and partially completed with real host evidence: yes — offset 7000 with specific file paths named
- CDB conversion and exact-input execution explicitly deferred: yes — stated clearly in both the Iteration_1 report and the docs report boundary section

**Overstatement check:** None found. The reports distinguish between "raw-source acquisition" and "exact-input execution" consistently. The payload probe numbers (115MB/1000-feature geojson page, ~10MB/100-feature page, 92M county directory, 48M zipcode checkpoint) are internally consistent and plausible for US polygon datasets at this scale. No claims exceed what the code and evidence support.

**Technical soundness:** The paging loop, manifest generation, gzip writing, and per-page logging are all correct. The `status: partial` vs `status: complete` logic in `stage_asset` (`downloaded == total`) is accurate.

---

**Approved with minor notes**
