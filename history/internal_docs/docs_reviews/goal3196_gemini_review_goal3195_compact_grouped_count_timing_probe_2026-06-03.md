# Gemini Review for Goal3195 Compact Grouped-Count Timing Probe (2026-06-03)

## Context

Goal3195 is an internal timing probe for the Goal3193 compact resident grouped-count columns. It compares exact host-row materialization (`prepared.run(left_segments)` plus Python `Counter(left_id)`) with the compact resident primitive path (`candidate_device_columns(...)` plus `grouped_count_by_left_id_compact_device_columns(...)`). The workload is authored all-crossing segment pairs at scales of `512 x 512`, `1024 x 1024`, and `2048 x 2048`. The compact path uses CuPy copies only for validation. This is not a public speedup claim, not a RayJoin paper reproduction claim, and not release evidence.

## Review Questions

### 1. Is Goal3195 correctly framed as an internal primitive-path timing probe, not a public speedup claim, release gate, or RayJoin paper reproduction?

**Answer:** Yes, the report (`docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.md`) explicitly states its purpose as "an internal timing probe" and disclaims it as "not a public speedup claim, not a RayJoin paper reproduction claim, and not a release gate." The `claim_boundary` flags in the JSON artifact also confirm this framing.

### 2. Do the artifact rows support the report table exactly, including the 2048 x 2048 row with exact host rows `5.909632220864296` seconds and compact resident columns plus validation copy `0.01623670384287834` seconds?

**Answer:** Yes, the JSON artifact (`docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.json`) contains a row for `n_left: 2048, n_right: 2048` where `exact_rows_host_materialized_seconds` is `5.909632220864296` and `compact_device_columns_seconds_including_validation_copy` is `0.01623670384287834`. These values exactly match the report table.

### 3. Are all rows validated against exact-row oracle counts with `all_match_exact_rows: true`?

**Answer:** Yes, the JSON artifact (`docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.json`) shows that for all entries in the `rows` array, the field `all_match_exact_rows` is set to `true`. This is also asserted in the test file (`tests/goal3195_compact_grouped_count_timing_probe_test.py`).

### 4. Does the report correctly explain that the compact path avoids large host-row materialization but still performs a validation copy in this probe?

**Answer:** Yes, the report explicitly states under "Interpretation": "compact resident grouped-count columns avoid the large host-row surface," and under "Setup" it clarifies that "CuPy validation copy of compact `group_key[]` and `count[]` only" is performed. The timing column name "Compact Resident Columns + Validation Copy (s)" also reflects this.

### 5. Are claim boundaries false for release, public speedup, RT-core speedup, true zero-copy, whole-app speedup, and RayJoin paper reproduction?

**Answer:** Yes, both the report (`docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.md`) and the JSON artifact (`docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.json`) explicitly list all these claim boundaries as `False`. The test file also asserts these conditions.

### 6. What should be the next engineering step after this evidence: app-facing integration, larger stress tests, downstream device-to-device continuation, or something else?

**Answer:** Based on the evidence, the compact path is significantly faster and validated. The report concludes with "the new primitive path gets more valuable as the pair stream grows". The claim boundaries explicitly rule out release and public speedup claims, and mention it's "still a primitive-path timing probe". Goal3193's purpose was to add these compact grouped-count device columns, keeping them resident on CUDA. Therefore, the logical next step would be **downstream device-to-device continuation**, as the value of keeping data on the device is demonstrated, and the next steps would be to leverage this without host materialization if possible. App-facing integration would typically come after further integration work and possibly broader stress tests.

## Verdict

accept-with-boundary
