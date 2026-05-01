# Goal1168 Claude Review: Goal1166 Live Pod Intake Audit

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-04-30
Subject: Goal1168 machine-checkable audit of Goal1166 live RTX pod artifacts

## Verdict

**ACCEPT**

The Goal1168 audit correctly concludes `engineering_verdict=accept` and
`claim_grade_verdict=blocked` for the copied Goal1166 live RTX pod artifacts.
All 13 checks evaluate their target JSON fields correctly, all numbers in the
intake report match the raw JSON values, boundary language is conservative, and
no public RTX speedup wording is authorized anywhere in the artifact chain.

## Verification Detail

### 1. Six expected JSON artifacts are checked

The `audit()` function loads exactly six JSON packet files:

| Key | File |
| --- | --- |
| `ann_validation` | `ann_candidate_8192_validation.json` |
| `ann_timing` | `ann_candidate_65536_timing.json` |
| `robot_validation` | `robot_pose_flags_32768_validation.json` |
| `robot_timing` | `robot_pose_flags_262144_timing.json` |
| `jaccard_validation` | `polygon_jaccard_8192_chunk512_validation.json` |
| `jaccard_diagnostic` | `polygon_jaccard_8192_chunk256_diagnostic.json` |

`all_expected_files_present` additionally confirms the three non-JSON files
(intake_report, source_context, runner_log). `missing=[]` in the output JSON.
**Pass.**

### 2. ANN and robot validation rows prove correctness only at smaller scales

- `ann_candidate_8192_validation.json`: `scenario.result.matches_oracle = true`,
  `skip_validation = false`. Audit check `ann_validation_matches_oracle` tests
  `is True`. **Pass.**
- `robot_pose_flags_32768_validation.json`: `matches_oracle = true`,
  `validated = true`. Audit check `robot_validation_matches_oracle` tests
  `is True`. **Pass.**

Neither validation result is overread as large-scale proof; the intake report
explicitly labels them "correctness validation row" only.

### 3. ANN and robot larger rows remain timing-only

- `ann_candidate_65536_timing.json`: `parameters.skip_validation = true`,
  `scenario.result.matches_oracle = null`. Audit checks
  `ann_large_timing_validation_skipped` via `is None`. **Pass.**
- `robot_pose_flags_262144_timing.json`: `validated = false`,
  `matches_oracle = null`. Audit checks `robot_timing_validation_skipped` via
  both `validated is False` and `matches_oracle is None`. **Pass.**

Both larger rows appear as claim-grade blockers ("ANN large row skipped
validation and is timing-only", "robot large row skipped validation and is
timing-only").

### 4. Polygon Jaccard chunk512 pass and chunk256 diagnostic failure

- `polygon_jaccard_8192_chunk512_validation.json`: `status = "pass"`,
  `parity_vs_cpu = true`. CPU and OptiX digests match exactly
  (`jaccard_similarity = 0.263157894737`). Audit checks
  `jaccard_chunk512_passed` via `status == "pass"`. **Pass.**
- `polygon_jaccard_8192_chunk256_diagnostic.json`: `status = "fail"`,
  `parity_vs_cpu = false`. OptiX digest diverges
  (`jaccard_similarity = 0.252854812398` vs CPU `0.263157894737`). Audit checks
  `jaccard_chunk256_diagnostic_failed` via `status == "fail"`. **Pass.**

The chunk256 failure is correctly listed as a claim-grade blocker ("Jaccard
chunk256 remains an expected diagnostic failure"). The intake report labels it
"expected non-fatal failure | diagnostic boundary; not a runner failure."

### 5. Dirty-source marker blocks public speedup wording and claim-grade release

All six JSON artifacts carry:

```
"source_commit": "d0ebf9d69041cf013b7af4dcb20a570d25d92c3f-local-dirty-goal1166"
```

Audit checks:
- `single_source_marker = True` (exactly one distinct marker across all loaded
  artifacts). **Pass.**
- `source_marked_local_dirty = True` ("local-dirty" in marker). **Pass.**
- `source_context_records_dirty_tree = True` (source_context.md contains
  "not cloned from a clean git checkout", "Local dirty-path count at copy time:",
  "not claim-grade public speedup artifacts"). **Pass.**
- `intake_records_engineering_accept_claim_block = True`
  ("ENGINEERING ACCEPT, CLAIM-GRADE BLOCKED" verbatim in intake_report). **Pass.**

The dirty-source marker is the first claim-grade blocker. `claim_grade_verdict =
"blocked"`.

### 6. No public RTX speedup wording is authorized

Every artifact JSON carries a `boundary` field explicitly disclaiming speedup
claims. The audit output `boundary` field states: "does not authorize public
speedup wording or claim-grade release evidence." The intake report Source
Boundary section repeats the same restriction. No path through the audit logic
produces an authorized speedup statement.

### Raw number cross-check (intake report vs. JSON)

| Row | Metric | JSON value | Intake report |
| --- | --- | --- | --- |
| ANN 8192 | OptiX query median | 0.000622868… s | 0.000623 s ✓ |
| ANN 8192 | validation median | 0.004669177… s | 0.004669 s ✓ |
| ANN 65536 | OptiX query median | 0.000963101… s | 0.000963 s ✓ |
| Robot 32768 | OptiX warm median | 0.051494075… s | 0.051494 s ✓ |
| Robot 32768 | oracle_validate | 112.779002… s | 112.779003 s ✓ |
| Robot 262144 | OptiX warm median | 0.000442744… s | 0.000443 s ✓ |
| Robot 262144 | total | 1.352842117… s | 1.352842 s ✓ |
| Jaccard chunk512 | candidate discovery | 1.823073… s | 1.823074 s ✓ |
| Jaccard chunk512 | native exact | 2.347038… s | 2.347039 s ✓ |
| Jaccard chunk256 | candidate discovery | 1.671872… s | 1.671872 s ✓ |
| Jaccard chunk256 | native exact | 2.517094… s | 2.517094 s ✓ |

All values match within rounding. No discrepancies found.

### Check table (all 13 checks)

| Check | Correct | Notes |
| --- | --- | --- |
| `all_expected_files_present` | ✓ | `missing=[]` confirmed |
| `single_source_marker` | ✓ | One distinct commit token |
| `source_marked_local_dirty` | ✓ | "local-dirty" in token |
| `intake_records_engineering_accept_claim_block` | ✓ | Verbatim substring found |
| `source_context_records_dirty_tree` | ✓ | Three required substrings present |
| `ann_validation_matches_oracle` | ✓ | `true` in JSON |
| `ann_large_timing_validation_skipped` | ✓ | `null` in JSON |
| `ann_large_timing_query_under_prior_timeout` | ✓ | 0.000963 s < 1.0 s |
| `robot_validation_matches_oracle` | ✓ | `true` in JSON |
| `robot_timing_validation_skipped` | ✓ | `validated=false`, `matches_oracle=null` |
| `robot_timing_query_under_prior_timeout` | ✓ | 0.000443 s < 1.0 s |
| `jaccard_chunk512_passed` | ✓ | `status="pass"` in JSON |
| `jaccard_chunk256_diagnostic_failed` | ✓ | `status="fail"` in JSON |

## Summary

The Goal1168 audit is technically correct and conservative. All six JSON
artifacts are present and checked. Validation is claimed only at the smaller
scales where `matches_oracle=true` was confirmed. The larger timing-only rows
carry no correctness claim. The Jaccard chunk512/chunk256 split is represented
honestly. The dirty-source marker is properly propagated into `claim_grade_verdict
= blocked` and no public speedup wording is authorized at any layer.

**engineering_verdict: ACCEPT**
**claim_grade_verdict: BLOCKED** (confirmed correct)
