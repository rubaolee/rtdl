# Goal507 External AI Review

Date: 2026-04-17  
Reviewer: Claude Sonnet 4.6 (external AI review)

## Verdict: PASS — Honest and accurate

The five artifacts (app, benchmark script, test, report, two raw JSON files) are internally consistent and do not overstate RTDL performance or RT-core acceleration.

---

## Data Integrity

All numeric values in the report tables were cross-checked against the raw JSON:

- Every `median_sec` value in the report matches the corresponding `median_sec` field in the JSON to displayed precision.
- Every `Correct vs reference` flag in the report matches `matches_reference_distance` in the JSON.
- The 20k file correctly records a single-sample run (iterations=1); median=min=max for each entry, and the report tables are labeled "Median sec" which is technically accurate for n=1.
- The host metadata (GTX 1070, driver 580.126.09, Embree 4.3.0, OptiX 9.0.0, Vulkan 0.1.0, library versions) is consistent between the two JSON files and the report.

One nuance cross-checked and confirmed correct: FAISS at 5k and 20k reports `True` correctness despite a slightly different distance than the reference. The difference is within the declared `rel_tol=1e-5, abs_tol=1e-5` tolerance (5k delta ~3e-6; 20k delta ~6e-6), so the True flag is not a misrepresentation. FAISS at 10k (`matches_reference_distance: false`, delta ~1.5e-4) is correctly reported as False in the table.

---

## Hardware Disclosure

The GTX 1070 pre-RTX boundary is clearly stated in the report and is confirmed by the `nvidia_smi` field in both JSON files (`"NVIDIA GeForce GTX 1070, 580.126.09"`). The "do not claim: RT-core acceleration" bullet is respected throughout; no RT-core language appears in the report.

---

## Performance Claims

All four explicit claims in the "What This Means For v0.8" section are supported by the data:

| Claim | Data support |
|---|---|
| Multi-backend execution works to 20k on Linux | All three RTDL backends returned status:ok at 20k |
| OptiX/Vulkan strongly outperform RTDL Embree | At 20k: Embree 45.77s vs OptiX 0.65s vs Vulkan 0.42s — ~70–110× |
| RTDL does not beat SciPy/FAISS for exact 2D 1-NN | SciPy faster than RTDL GPU at 20k; FAISS fastest at all sizes |
| No RT-core acceleration claim | Confirmed absent |

---

## Code Review

**`rtdl_hausdorff_distance_app.py`**: The app correctly implements the two-pass Hausdorff reduction (A→B and B→A nearest-neighbor passes, Python max). The `matches_oracle` tolerance of `1e-5` (both `rel_tol` and `abs_tol`) is appropriate for `float_approx` GPU backends and is an honest relaxation from `1e-12`. The oracle (`brute_force_hausdorff`) is a clean double-loop reference. The deterministic tie-break in `_directed_from_rows` (by `query_id` descending then `neighbor_id` descending) is consistent between the oracle and the app, so correctness checks are fair.

**`goal507_hausdorff_linux_perf.py`**: The benchmark `_measure` function uses `gc.collect()` before each timed call and `time.perf_counter()` — appropriate methodology. The `reference_distance` is set to the first successful measurement (rtdl_embree first in iteration order), making the correctness check relative rather than to a separate oracle. This is fine for the stated purpose (cross-library distance consistency check), but reviewers should note that if all backends agreed on a wrong answer, the check would not catch it. In practice the reported numbers are consistent with the float64 reference values from the app correctness smoke tests, so this is not a concern here.

**`goal507_hausdorff_perf_harness_test.py`**: Tests are minimal but appropriate: one subprocess check that GPU backend choices appear in `--help` output, one numpy-guarded functional test of the CPU path at size 8. The skipped test is correctly documented and exercised in the Linux benchmark environment.

---

## Minor Observations (non-blocking)

1. **Symmetric benchmark geometry**: `_make_points` uses `phase=0.0` for both A and B sets (only the seed differs). This produces `directed_a_to_b == directed_b_to_a` for every entry in both JSON files — a coincidence of the data, not a bug. Real use cases will have asymmetric directed distances; the app code handles asymmetry correctly.

2. **OptiX cold-start**: At 1k the OptiX `max_sec` (0.498s) is ~119× larger than its `median_sec` (0.0042s), indicating GPU JIT/init cost on the first call. Using median across 3 iterations is the right choice and is not misrepresented.

3. **FAISS float32 precision**: The benchmark's `_points_to_numpy` returns `float32`; FAISS `IndexFlatL2` operates on `float32`; distances are reconstructed via `sqrt`. The float32 rounding is the correct explanation for FAISS deviating at 10k, as acknowledged in the report.

---

## Summary

The report is accurate, the raw data supports every table entry and correctness flag, the hardware limitation is prominently disclosed, and no overclaiming of RTDL performance or RT-core acceleration is present. Goal507 satisfies the external review criteria.
