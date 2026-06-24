# Goal3560 Claude Review: Goals3556–3559 v2.9 Performance Cleanup

Date: 2026-06-06
Reviewer: Claude Sonnet 4.6 (external read-only review)
Verdict: **accept-with-boundary**

---

## Findings by Severity

### MEDIUM — RTNN Row Run-to-Run Variance Is Unresolved

**Files:** `docs/reports/goal3557_rtnn_same_scalar_median_metric_a5000/summary.json`,
`docs/reports/goal3558_v2_9_full_packet_after_rtnn_same_scalar_a5000_cap250k/summary.json`

The RTNN targeted run in Goal3557 and the same row in the Goal3558 full packet give materially different results despite using the same protocol:

| Run | v2.3 primary_metric_sec | v2.8 primary_metric_sec | Speedup |
|---|---:|---:|---:|
| Goal3557 targeted | 0.001328629 | 0.001356328 | 0.979578x |
| Goal3558 full packet | 0.001532887 | 0.001444501 | 1.061225x |

The v2.3 value differs by ~15% (1.329 ms vs 1.533 ms) between the two runs. Both use `elapsed_median_sec` with ~9500 internal repeats, planned to the same 12.5 s target. This is a single-run-to-single-run variance of the full outer row, not an internal-repeat outlier.

The practical effect is that RTNN sits near the parity boundary (0.98x–1.06x range across these two runs). The report's claim that RTNN "is no longer a weak row" (`docs/reports/goal3558_v2_9_full_packet_after_rtnn_same_scalar_2026-06-06.md`) is premature without an alternating probe equivalent to Goal3559's RayDB treatment. The reported `1.061x` improvement from this single full-packet run is within the noise band established by the two-run comparison, and should not be cited as evidence of a genuine positive result for RTNN.

**Required before stable closeout:** an alternating multi-trial RTNN probe (≥3 trials per lane) using the same `elapsed_median_sec` scalar and the corrected v2.3 overlay, analogous to Goal3559's RayDB probe protocol.

---

### LOW — RT-DBSCAN Uses a Two-Sample Median While RTNN Uses Thousands of Internal Repeats

**Files:** `docs/reports/goal3558_v2_9_full_packet_after_rtnn_same_scalar_a5000_cap250k/summary.json` rows `rt_dbscan_optix_grouped_stream` v2.3 and v2.8 (lines showing `"primary_metric_source": "elapsed_sec"`), `docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch` (rt_dbscan section)

The overlay patch and current code both apply `--warmup 1 --repeat 3` to rt_dbscan. With `warmup=1, repeat=3`, the measured run count is 2. A median of 2 values is their arithmetic mean — it provides no protection against a single bad measurement. The full-packet rt_dbscan result (0.997x) is plausible and near-parity, but its measurement is less robustly sampled than RTNN's or RayDB's.

This is not a correctness defect — both v2.3 and v2.8 sides use the same protocol — but it creates a heterogeneous noise floor across rows in the packet. The summary geomean and interpretation do not account for the different effective repeat robustness per row.

**Advisory only.** Increasing rt_dbscan's measured run count to 3+ (e.g., `--warmup 1 --repeat 4`) would align it closer to the other rows' robustness.

---

### LOW — v2.3 Overlay Semantics Change Is Not Explicitly Documented Per App

**File:** `docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch`

The overlay modifies measurement behavior across six benchmark apps (hausdorff, librts, rt_dbscan, spatial_rayjoin, barnes_hut, and the RTNN external runner). For several apps the semantic of `elapsed_sec` changes: what was formerly the last-repeat wall time becomes the median of repeat-measured runs. This is a correct and beneficial change, but:

- The `primary_metric_source` fields in the full-packet summary still show `"elapsed_sec"` for apps like rt_dbscan rather than distinguishing between the old last-repeat and new median semantics.
- If older reports referencing `elapsed_sec` values for these apps are compared to current reports, the semantics differ silently.

The reports and boundary blocks correctly state this is internal evidence only, so there is no external claim risk. But if this overlay is ever used as the basis for a v2.3 comparison claim in a later packet, the changed meaning of `elapsed_sec` should be explicitly documented in the overlay header.

---

### LOW — RayDB De-escalation Probe Uses Three-Trial Minimum

**File:** `docs/reports/goal3559_raydb_sum_count_probe_a5000/summary.json`

The probe runs 3 alternating trials per mode/lane. A median of 3 trials is the minimum useful median; it cannot distinguish a stable 3-way distribution from a one-sided outlier. For count, the v2.8 trial-2 value (0.000556s) is ~6% below the other two v2.8 count measurements (0.000591, 0.000592), pulling the median down slightly. Using 5 trials would give more confidence in the de-escalation conclusion.

This is advisory: the de-escalation from 0.944x to 0.997x is directionally sound because the variance in the probe is observed on both sides, not systematically favoring v2.8.

---

## Question-by-Question Assessment

### Q1: Did Goal3556 correctly preserve RTNN compatibility while adding median/min/max repeat scalars?

**Yes.** The implementation in `scripts/goal2348_rtnn_v2_2_external_runner.py` is correct:

- `import statistics` added (line 9).
- `elapsed_median_sec = statistics.median(elapsed_runs) if elapsed_runs else 0.0` computed at line 1079.
- `elapsed_min_sec` and `elapsed_max_sec` added at lines 1089–1090.
- `"elapsed_sec": elapsed_sec` (last-repeat scalar) preserved at line 1086, maintaining backward compatibility.
- The same three new fields are added to `run_rtdl_adaptive_partitioned_3d_neighbors` (lines 1379–1381).

In `scripts/goal2626_benchmark_embree_optix_baseline.py`, both RTNN cases (`rtnn_embree_prepared_3d_ranked_summary` line 487, `rtnn_optix_prepared_3d_ranked_summary` line 530) now carry `primary_metric_path=("elapsed_median_sec",)`. The tests in `tests/goal3556_rtnn_median_repeat_metric_hardening_test.py` (lines 17–24) verify all three new fields exist, that `elapsed_sec` is preserved, and that both Goal2626 registry rows select `elapsed_median_sec`.

Compatibility is preserved. No regression risk to older reports that read `elapsed_sec`.

### Q2: Did Goal3557 correctly fix the v2.3 overlay mismatch?

**Yes.** The fix is clearly documented and the JSON artifact confirms it. In `docs/reports/goal3557_rtnn_same_scalar_median_metric_a5000/summary.json`:

- v2.3 row: `"primary_metric_source": "elapsed_median_sec"` (line 72), `"primary_metric_sec": 0.001328629`.
- v2.8 row: `"primary_metric_source": "elapsed_median_sec"` (line 151), `"primary_metric_sec": 0.001356328`.

Both sides use the same scalar. The report explicitly rejects the earlier Goal3556 targeted run that compared v2.3 `elapsed_sec` to v2.8 `elapsed_median_sec`. The test at `tests/goal3557_rtnn_same_scalar_median_metric_a5000_test.py` lines 43–44 directly verifies the JSON scalar source matches the artifact.

The overlay patch in `docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch` contains `primary_metric_path=("elapsed_median_sec",)` at least twice for the RTNN Embree and OptiX cases (verified by test line 68).

### Q3: Is Goal3558's full packet interpretation honest?

**Mostly yes**, with the qualification noted under the medium-severity finding above.

The packet is accurately described:
- 11/11 rows target-plan-met and target-observed-met (verified in summary.json lines 2111–2120).
- Geomean 1.0165x and median 0.9938x are correctly reported.
- Claim boundaries are uniformly false across all 11 rows.
- The report names the weakest rows (RayDB sum 0.944x, RayDB count 0.973x) and lists near-parity negatives honestly.
- The report explicitly states it is "not a release or public speedup packet."

The honesty concern is the RTNN row treatment: the report states RTNN "is no longer a weak row" and attributes this to the same-scalar fix. While the scalar fix is correct, the 15% v2.3 variance between the Goal3557 and Goal3558 runs means the 1.061x figure is not yet established as stable. The report should note that the RTNN improvement in the full packet is within the one-run noise band.

All claim boundaries are correctly coded false in the artifact JSON, and the report text contains the required boundary language.

### Q4: Does Goal3559 reasonably de-escalate RayDB sum/count?

**Yes.** The de-escalation is supported by the data and correctly framed.

The Goal3558 full-packet RayDB sum value (0.944x) came from a single run where the v2.8 primary_metric was 0.000793s. The Goal3559 probe at repeat=20000 across 3 alternating trials shows v2.8 sum median = 0.000758s (vs v2.3 = 0.000748s) for a 0.987x result. The variance in the v2.3 side across three trials (0.000787, 0.000748, 0.000746) is larger than the v2.8 gap, consistent with run variance rather than systematic regression.

For count, the probe result is 0.997x (essentially parity). The report's conclusion — "do not change RayDB code solely from Goal3558's single weak sum row" — is well-supported.

The probe uses the same `copies=120000` and `metadata.timings.query_median_sec` path as the full packet, so the comparison is apples-to-apples.

### Q5: Are any claim boundaries over-authorized?

**No.** All reviewed artifacts carry consistent boundary enforcement:

Every comparison row in all four goal summaries has:
- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_rt_core_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`
- `paper_reproduction_claim_authorized: false`
- `package_install_claim_authorized: false`
- `internal_results_only: true`

The tests for Goals 3556–3559 all include dedicated `test_claim_boundary*` methods that assert all seven flags false. The report text in each goal also contains explicit "does not authorize" lists.

The RayDB backend is labeled `optix_partner_resident_experimental` in the command arguments (summary.json lines 686, 763). No row attempts to claim RT-core traversal for the RayDB grouped-aggregate path.

### Q6: What is required before treating the v2.9 packet as a stable internal closeout?

The following are required, in priority order:

**Required:**
1. **RTNN alternating probe.** The 15% v2.3 single-run variance between Goal3557 and Goal3558 is unresolved. Run ≥3 alternating trials for the `rtnn_optix_prepared_3d_ranked_summary` row (same protocol as Goal3559) before classifying the row as positive or stable.

2. **Documentation of the RTNN single-run uncertainty.** Until the alternating probe is done, the Goal3558 report and any downstream summary should note that the 1.061x RTNN result is a single-packet observation within the established 0.98x–1.06x noise band for this row.

**Advisory (improves robustness, not blocking):**

3. **RT-DBSCAN repeat count.** Increase `--repeat` from 3 to 4 (keeping `--warmup 1`) so the median is over 3 measured runs rather than 2.

4. **Consider an alternating probe for the cluster of near-parity negatives** (robot collision 0.988x, spatial RayJoin 0.989x, LibRTS 0.992x, Barnes-Hut 0.994x). None individually is a concern, but all four being below 1.0 in the same packet run warrants at least one verification that this cluster is variance, not a systematic small regression.

5. **Add an explicit note in the v2.3 overlay header** that `elapsed_sec` in the overlay-patched apps now carries median-of-measured-repeats semantics, not last-repeat semantics, to prevent silent comparison errors with pre-overlay measurements.

---

## Summary

The Goals3556–3559 chain is procedurally sound and claim-boundaries are consistently enforced. Goal3556 correctly adds median/min/max scalars while preserving backward compatibility. Goal3557 correctly repairs the scalar-mismatch bug that produced the earlier spurious 0.956x RTNN result. Goal3558 provides an honest 11-row internal triage picture with positive geomean and correctly bounded language. Goal3559 correctly de-escalates RayDB sum/count from a code-change mandate to a one-run variance observation.

The one unresolved issue is that the RTNN row in the full packet (1.061x) is not corroborated by an alternating probe, and differs from the targeted run (0.980x) by a 15% v2.3 variance. The packet should not be used to claim RTNN is a positive row until that variance is resolved.

Verdict: **accept-with-boundary**
Required before stable closeout: alternating RTNN probe and documentation of the one-run uncertainty.
