All evidence read. Now I'll verify the raw speedup arithmetic before rendering verdicts.

**embree_32768_stress spot-check (sample 1):**  
`v2=0.78442s / current=0.90061s = 0.8710x` — matches `0.8709860165492801` ✓

**optix_cold_single_shot spot-check (sample 4):**  
`v2=0.23964s / current=0.19801s = 1.210x` — matches `1.2102412039933332` ✓

**embree geomean spot-check:**  
Product ≈ 1.271, raised to 1/8 ≈ 1.0304 — matches `1.0305008610719026` ✓

**optix geomean spot-check:**  
Product ≈ 0.847, raised to 1/8 ≈ 0.9794 — matches `0.9794850577580364` ✓

---

## Verdict

```
accept_m58_valid_yellow_watch_rows_open_no_closure
```

---

## Question-by-Question

### 1. Was M58 within the exact M57 one-run authorization?

**Yes.** All eleven required preconditions from the M57 3-AI consensus are satisfied:

| Precondition | Result |
|---|---|
| Dry-run executed first with `--run-preflight` without `--execute` | `execute: false, run_preflight: true` ✓ |
| Real current/V2.14 roots used | `/root/rtdl_v3_rebuild_20260620/{current,v2_14}` ✓ |
| Explicit Linux Python paths | `/usr/bin/python3` throughout ✓ |
| Dry-run `failed_checks=[]` | Confirmed ✓ |
| `current_librts_set_b_source_signature` row exists, `returncode=0`, stdout `"failed": []` | All confirmed ✓ |
| Execution proceeded only after conditions 1–5 passed | Dry-run dir timestamp `0054`, execution dir `0055` ✓ |
| Exactly one run with `--execute` | One execution directory; no evidence of second run ✓ |
| Unchanged M47 scenario set (`optix_cold_single_shot`, `embree_32768_stress`) | Both present, all parameters identical to M47 spec ✓ |
| Exactly 8 paired samples per scenario | `sample_count_per_scenario: 8` ✓ |
| Full evidence copied back | 32 stdout JSON + 39 stderr/preflight files + `summary.json` + driver log ✓ |
| Watch rows not closed from raw output | Neither scenario labeled green ✓ |

The `current_git_revision` check returned `returncode: 128` (no git repo at the sync target), but this row is `required: false` and is expected for a deployed non-repo directory. It is not a breach.

The authorization token itself is not echoed into `summary.json` (the harness enforces it as a gate condition; it does not archive it). This is a minor traceability gap but not a scope breach — the harness would have refused to execute without the token, and no second run exists.

---

### 2. Is the target dry-run/source-signature gate evidence sufficient?

**Yes.** The source-signature preflight (`preflight_current_librts_set_b_source_signature.stdout.txt`) records all eight checks as `true` with `"failed": []`:

- `prepared_embree_count_helper_present` ✓  
- `prepared_optix_query_set_helper_present` ✓  
- `prepared_helpers_mark_set_b_control` ✓  
- `prepared_helpers_mark_not_set_a_probe` ✓  
- `prepared_optix_helper_marks_prepared_query_mode` ✓  
- `librts_app_exposes_payload_set_b` ✓  
- `librts_app_exposes_metadata_set_b_twice` ✓  
- `librts_app_exposes_optix_prepared_query_mode` ✓  

The preflight unit tests (`v3_phoenix_librts_aabb_count_runner_test`, `v3_phoenix_prepared_execution_session_runner_test`, `v3_phoenix_aabb_prepared_query_cache_test`) also passed with `returncode: 0`. The dry-run status is correctly `m47_librts_stability_protocol_preflight_only_no_pod_not_release`.

---

### 3. Is the execution copy-back complete enough for review?

**Yes.** The copy-back satisfies all requirements:

- 32 measured stdout JSON files (= 8 samples × 2 scenarios × 2 trees) — confirmed by the intake gate test `glob("*stdout.json")` assertion ✓  
- ≥32 stderr/preflight text files (39 present) ✓  
- `summary.json` present with full `scenario_results`, `schedule`, and `preflight` blocks ✓  
- `m58_execution_driver.log` present ✓  

The driver log confirms all 7 preflight rows ran first, then the full 32 schedule rows (16 optix, 16 embree) in alternating order. Execution status is `m47_librts_stability_protocol_run_complete_not_release`. All claim-boundary booleans are `false`. `run_errors: {}`.

---

### 4. Do the M47 yellow labels follow from the summary metrics and metadata?

**Yes, the yellow labels are correctly assigned for both scenarios.**

**embree_32768_stress** (yellow, justified):
- Geomean 1.031x is nominally positive
- But 2 of 8 samples fall below 0.95: sample 1 (0.871x) and sample 4 (0.945x)
- High inter-sample variance (min 0.871, max 1.226) prevents closure
- First-sample-stripped geomean 1.056x is encouraging but insufficient alone
- Cannot be green; cannot be red; yellow is correct

**optix_cold_single_shot** (yellow, but substantively weak — note this):
- Geomean 0.979x is **below 1.0** — V3 is, on average, marginally slower than V2 across these 8 samples
- 5 of 8 samples fall below 0.95 (samples 1, 2, 3, 7, 8)
- Pass count 3/8 is the lowest allowable for yellow; one fewer pass would be clearly red-territory
- First-sample-stripped geomean 1.002x barely clears 1.0 only after removing the worst outlier
- This row remains open not as a mild concern but as a genuine stability problem

The yellow label is technically correct for both, but the optix row is the harder case and should not be soft-pedaled in any future narrative.

---

### 5. Is it correct that `set_b_control_candidate_missing` is cleared?

**Yes.** Every paired sample across both scenarios reports:

```
current_metadata_failures: []
current_metadata_ok: true
fixture_contract_failures: []
fixture_contract_matches: true
```

That is 16 paired samples (8 per scenario) with zero metadata failures. The source-signature preflight verified at the code level that `prepared_helpers_mark_set_b_control` and `librts_app_exposes_metadata_set_b_twice` are both present in the synced source files. The M55 metadata failure that caused prior concern is structurally cleared.

---

### 6. Is it also correct that neither watch row is green/closed?

**Yes, unambiguously correct.**

**embree_32768_stress:** Geomean 1.031x is positive but 2 samples below 0.95 with a 0.871x minimum disqualify green.

**optix_cold_single_shot:** Geomean 0.979x (sub-1.0), 5/8 samples below 0.95. This row does not come close to green. It is yellow/open precisely because it represents a real, unresolved performance concern.

Any claim that either row is closed would be unsupported by the evidence.

---

### 7. What is the next allowed action?

The M57 authorization token is consumed. No second M57 run is authorized. The next allowed actions, in order, are:

1. **Record M58 as accepted evidence intake** with both LibRTS watch rows `yellow_stability_boundary_watch_row_open`. This review constitutes that recording.

2. **Decide whether the open watch rows represent a permanent acknowledged limitation or an actionable gap.** This is a separate scope decision requiring its own review. The options are:
   - Accept yellow/open as a stable disclaimer in the V3 release gate (LibRTS is not a release blocker claim, it is a labeled open row)
   - Authorize new LibRTS implementation work to address the optix cold-shot weakness — but that requires a separate authorization, not derived from M57 or M58

3. **No** public speedup wording, no V3-over-V2 claim, no all-app benchmark run, no broad POD campaign, no watch-row closure, no V4/embedding/C ABI/true-zero-copy work, no second M57 run — all remain prohibited.

---

## Non-Authorization Confirmation

This review does not authorize and explicitly preserves prohibition on:

- V3 release
- All-app benchmark run
- Broad paid POD campaign
- Second M57 run
- Public speedup wording
- Broad V3-over-V2 claim
- V4 work
- Embedding
- C ABI
- True-zero-copy claim
- Watch-row closure for either LibRTS scenario
