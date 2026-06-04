# Goal3305 Claude Review: Goal3303–3304 RayJoin Current-Best and Negative Probe Chain

Date: 2026-06-04
Commit reviewed: `ed62ddc7`
Reviewer: Claude Sonnet 4.6
Verdict: **accept**

---

## Summary

The three-goal chain (Goal3300 boundary-event probe, Goal3303 negative tuning probes, Goal3304 current-best refresh) is well-evidenced, honestly scoped, and safe to carry into the next pod run. All claim-boundary flags remain blocked. The negative conclusions are each supported by a matching artifact or a documented fail-closed outcome. Goal3304 correctly identifies the current-best route without overclaiming a win. The next engineering target (generic scalar-count launch/packing/residency overhead) follows from the ruling-out logic. Two minor issues are noted below but neither is blocking.

---

## Findings by Severity

### Low — Wording Ambiguity in Goal3303 Report

**File:** `docs/reports/goal3303_rayjoin_scalar_count_negative_tuning_probes_2026-06-04.md`

The sentence:

> The native PIP scalar-count launch median was about 0.325 ms. This is slower than the prior tuned Goal3294 PIP route, which reported about 0.361 ms end-to-end prepared query median without prepared-edge layout.

The pronoun "This" is ambiguous. Read literally it claims "0.325 ms is slower than 0.361 ms," which is numerically false. The intended reading is that the probe's full end-to-end prepared-query median (0.421 ms) is slower than Goal3294's 0.361 ms end-to-end. The underlying facts are correct and verifiable from the artifact:

- Goal3303 JSON: `rtdl.pip.prepared_query_ms.median` = 0.421 ms
- Goal3303 JSON: `native_phase_samples[*].candidate_count_pass` median ≈ 0.325 ms (confirmed by manual sort of 20 values)

The 0.325 ms native-kernel median is correct. The 0.421 ms end-to-end comparison is correct. Only the prose is misleading. Not blocking for the next pod run, but worth clarifying before this record is cited in a paper or presentation.

**Suggested fix:** Replace the sentence with:

> The native PIP scalar-count launch median was about 0.325 ms; the full prepared-query end-to-end rose to about 0.421 ms. That end-to-end is slower than the prior Goal3294 tuned route, which ran about 0.361 ms end-to-end without prepared-edge layout.

---

### Informational — Outlier Spikes Undocumented in Goal3300 Boundary-Event Artifact

**File:** `docs/reports/goal3300_boundary_event_same_slice_pod_2026-06-04.json`

The `rtdl.pip.boundary_event_device_columns_ms.samples` array contains 5 values outside the stable 3.72–3.80 ms band: 21.02, 12.25, 168.36, 10.33, 14.01 ms. The median is correctly reported as 3.763 ms and the conclusions (boundary-event route is slow) are unaffected. However, these spikes represent roughly one-third of samples and indicate wall-clock instability for this route, likely from the large emitted-row stream (3961 rows) interacting with device memory pressure or OS scheduling.

The Goal3300 report does not mention this variance. Adding a brief note would improve the record and explain why the median is a better summary than the mean (3.894 ms end-to-end median includes grouped-count time; the raw device-columns spikes alone reach 168 ms).

Not blocking; no change required before the next pod run.

---

## Question-by-Question Analysis

### Q1. Are the negative conclusions supported by artifacts/tests?

**Boundary-event materialization (Goal3300):** Supported.
- Artifact median: 3.894 ms PIP end-to-end vs 0.222 ms RayJoin, ratio 17.52x. All 15 count samples return 3961 (consistent). The split timing (device-columns 3.763 ms, grouped-count 0.133 ms) correctly isolates the bottleneck.
- Test `test_pod_artifact_records_split_timings_and_claim_boundaries` verifies `boundary_event_device_columns_ms.median > 3.0` and `boundary_event_grouped_count_ms.median < 0.5`, consistent with the artifact.
- Report correctly notes the grouped-count continuation is not the bottleneck.

**Prepared-edge layout (Goal3303):** Supported.
- Artifact: `rtdl.pip.prepared_query_ms.median` = 0.421 ms with `pip_scalar_count_pipeline: true` and `device_filtered_boundary_mode: inclusive`. Count = 1430 across all 20 samples. This is worse than Goal3304's 0.336 ms median.
- The `RTDL_OPTIX_POINT_PRIMITIVE_USE_PREPARED_EDGE_LAYOUT=1` environment variable is disclosed in the report. The test verifies `prepared_query_ms.median > 0.40` and `counts.last == 1430`.

**Crossing-only boundary mode (Goal3303):** Supported via fail-closed.
- No artifact was written because the runner failed closed on the first PIP warmup: `129 != 1430`.
- The test verifies the report text contains `"129 != 1430"`. The outcome is honest and complete.

**Verdict:** All three negative conclusions are artifact-backed or documented as fail-closed outcomes.

---

### Q2. Does Goal3304 honestly identify the current-best route without overclaiming?

Yes. The report uses precise language throughout:

- "This is the current recommended RayJoin same-slice RTDL route" — not "RTDL beats RayJoin."
- "optimization gap remains" — the 1.53x PIP ratio and 1.22x LSI ratio are both above 1.0.
- "not a release or speedup claim" — stated explicitly.
- Claim-boundary JSON: all six flags are `false`.
- The PIP count contract is correctly labeled `rayjoin_pip_count_not_visible` and the LSI count is `matching_visible_lsi_count` — no false equivalence between the two sides.
- The test `assertLess(pip_comparison["rtdl_over_rayjoin_query_ratio"], 1.6)` bounds the claim range rather than allowing an accidental speedup assertion.

The phrase "RayJoin PIP positive count not exposed" correctly flags that the comparison is asymmetric: RTDL self-validates 1430 but RayJoin's PIP output count remains unavailable from the unpatched upstream binary.

---

### Q3. Do all claim-boundary flags remain blocked?

Yes. All three artifacts carry the same six-key `claim_boundary` object with every value `false`:

- `public_speedup_claim_authorized: false`
- `rayjoin_paper_reproduction_claim_authorized: false`
- `release_authorized: false`
- `rt_core_speedup_claim_authorized: false`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`

All three test suites include `self.assertFalse(any(artifact["claim_boundary"].values()))`. The runner emits this object unconditionally from a hardcoded constant (`CLAIM_BOUNDARY` dict at module level); it cannot be accidentally toggled by command-line flags.

---

### Q4. Is the next engineering target sound?

Yes. The reasoning is tight:

1. Boundary-event materialization is ruled out: 3.763 ms for 3961 emitted rows is structurally worse than any count-only path.
2. Prepared-edge layout is ruled out: 0.421 ms end-to-end vs 0.336 ms without it.
3. Crossing-only boundary semantics are ruled out: semantically incorrect for this slice (129 vs 1430).
4. The native scalar-count kernel time (0.260 ms in Goal3304 native_phase_samples) is close to the full prepared-query median (0.336 ms). The ~0.076 ms gap is in Python-side packing, upload, and launch overhead — none of which requires a semantic change.

The report correctly concludes: "The next useful work is not another semantic shortcut. It should target generic scalar-count launch/packing/residency overhead while preserving inclusive boundary semantics and keeping the native engine app-agnostic."

The framing as app-agnostic overhead reduction (not RayJoin-specific) is consistent with the engine boundary maintained throughout this chain.

---

### Q5. Inconsistencies in counts, timing units, route names, or visible contracts

**Counts:** Fully consistent across reports, artifacts, and tests.
- LSI: 269 in all artifacts and all sample arrays (15 or 20 samples each).
- Goal3303/3304 PIP: 1430 in all 20 samples, exact match across both artifacts.
- Goal3300 PIP: 3961 in all 15 samples.

**Timing numbers (report vs JSON):**
- Goal3300 table: 3.894 ms / 0.222 ms / 17.52x → JSON: 3.8935 ms / 0.22227 ms / 17.517x ✓
- Goal3300 split: 3.763 ms / 0.133 ms → JSON: 3.7635 ms / 0.1327 ms ✓
- Goal3303 table: 0.221 ms / 0.421 ms / 1.90x → JSON: 0.221411 ms / 0.4208 ms / 1.9007x ✓
- Goal3304 LSI: 0.226 ms / 0.275 ms / 1.22x → JSON: 0.226068 ms / 0.27538 ms / 1.2181x ✓
- Goal3304 PIP: 0.219 ms / 0.336 ms / 1.53x → JSON: 0.219409 ms / 0.33647 ms / 1.5335x ✓
- Goal3304 phase notes: 0.260 ms native scalar count, 0.020 ms point upload, 12.456 ms static shape pack → JSON native_phase_samples median candidate_count_pass ≈ 0.2596 ms, point_upload ~0.019-0.020 ms, static_shape_pack_ms.median = 12.456 ms ✓

**Timing units:** All tables in milliseconds, all JSON fields suffixed `_ms`, all native_phase_samples in seconds (as expected by the phase schema). No unit confusion detected.

**Route names:** `device_filtered_validated + inclusive + z_point + scalar count pipeline` appears consistently in the Goal3303 conclusion, Goal3304 title/table/test assertions, and the runner's `--rtdl-pip-count-mode` / `--rtdl-pip-boundary-mode` / `--rtdl-pip-query-axis` / `--rtdl-pip-scalar-count-pipeline` argument tuple.

**Commit hashes:**
- Goal3300 and Goal3303 artifacts: `56a91c8955985acd2ef98964c776444797b7bce9` (pod ran before Goal3303 was committed to main)
- Goal3304 artifact: `c312903ac30ec166432288ada88b145a05cd8eab` (current HEAD after negative probe records were committed)
- Tests pin each artifact to the correct commit. The progression is chronologically coherent.

**Visible contracts:** The `count_contract_status` field is correctly differentiated:
- `matching_visible_lsi_count`: LSI in all three artifacts, counts verified equal.
- `rtdl_boundary_event_count_not_pip_membership`: Goal3300 PIP only, correctly signals non-membership semantics.
- `rayjoin_pip_count_not_visible`: Goal3303 and Goal3304 PIP, correctly signals the unpatched binary limitation.

No inconsistencies found that require fixing before the next pod run.

---

## Verdict

**accept**

The three-goal chain is complete, internally consistent, and correctly scoped. The boundary-event route is ruled out with solid timing evidence and a fail-closed correctness guard. The prepared-edge and crossing-only probes are ruled out cleanly. Goal3304 is an honest current-best packet. The next target (app-agnostic scalar-count overhead) is well-motivated by the 0.076 ms gap between native kernel time and end-to-end prepared-query median. No fixes are required before the next pod run. The one wording ambiguity in Goal3303 is recommended for cleanup before external citation.
