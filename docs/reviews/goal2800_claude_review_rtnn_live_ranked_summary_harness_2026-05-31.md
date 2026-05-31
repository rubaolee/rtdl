# Goal2800 Claude Review: RTNN Live Ranked-Summary Harness

Date: 2026-05-31

Reviewer: Claude (Sonnet 4.6) — independent external review, distinct from Codex.

Verdict: **accept-with-boundary**

---

## Verdict Summary

Goal2800 is correctly scoped, honestly executed, and appropriately bounded. The harness exercises the live RTDL/OptiX ranked-summary route and the same-contract CuPy grid opponent. All evidence is internally consistent across the stdout artifact, JSON artifact, and markdown report. The CuPy grid is faster on all three distributions and this is not hidden — it is recorded directly and the `rtdl_beats_cupy_grid_claim_authorized: false` flag propagates through every layer. No overclaims are present for Triton, public speedup, paper reproduction, or native app customization.

The `accept-with-boundary` verdict matches the self-assessed status. The remaining open condition before final evidence closure is a clean-from-Git pod rerun after the Goal2800 commit is pushed. The test suite also requires a consensus file (`goal2800_rtnn_v2_5_live_ranked_summary_harness_consensus_2026-05-31.md`) that does not yet exist.

---

## Review Questions

### Q1 — Does the harness correctly exercise the current RTDL/OptiX ranked-summary route and the CuPy grid opponent?

**Yes.**

- `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py:72-84`: calls `rtnn_runner.run_rtdl_batched_3d_neighbors()` with `backend="optix"` and `result_mode="ranked-summary-raw"` — this is the live OptiX ranked-summary route, not a stub or historical artifact.
- Lines 86-98: calls `rtnn_runner.run_cupy_grid_3d_ranked_summary()` with `dtype="float32"` — this is the same-contract CuPy CUDA-core opponent.
- Three deterministic distributions are exercised (seeds 2800/2801/2802) with fixed radius=0.02, k_max=50, point_count=65536, repeat=3.
- The stdout artifact confirms all six (RTDL + CuPy) × three distribution runs completed with `ok=True`.
- The harness runs under the `goal2348_rtnn_v2_2_external_runner` module, which provides the canonical 3D neighbor entry points used across prior goals — there is no custom RTNN-specific engine path.

### Q2 — Is the tiny candidate-count tolerance for float32 boundary differences honest and sufficiently bounded?

**Yes, with one observation worth recording.**

The tolerance formula at `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py:171-175`:

```python
candidate_count_tolerance = (
    max(2, int(max(cupy_bounded_count, rtdl_candidate_count) * 1.0e-6))
    ...
)
```

At the 65K-point scale used, the 1e-6 proportional arm never exceeds the floor:
- Uniform 206,446: `int(206446 * 1e-6)` = 0 → `max(2, 0)` = **2**
- Clustered 2,914,109: `int(2914109 * 1e-6)` = 2 → `max(2, 2)` = **2**
- Shell 1,158,440: `int(1158440 * 1e-6)` = 1 → `max(2, 1)` = **2**

The effective tolerance is a fixed floor of 2 for all distributions at this scale. The proportional arm would only activate above ~2M candidates. This is appropriate and conservative: the observed deltas of 0, 1, 2 correspond to float32 boundary ambiguity on cells at exactly radius=0.02. The harness records `candidate_count_delta` and sets `candidate_count_matches_cupy_grid: false` for clustered and shell — it does not hide the disagreement. The shell case (delta=2, tolerance=2) is at the exact boundary, which is correct and does not indicate a problem; the harness would correctly fail if this grows to 3.

**Observation:** The tolerance description in the report reads "explicit float32 boundary tolerance" — this is accurate. Future reviewers should note that the tolerance bottoms out at 2 regardless of scale at these point counts, so a rerun with substantially larger counts could encounter a tolerance increase.

### Q3 — Does the report accurately reflect that CuPy grid is faster on the first artifact?

**Yes, and the numbers are internally consistent.**

Report table vs. JSON artifact cross-check:

| Distribution | RTDL (s) report | RTDL (s) JSON | CuPy (s) report | CuPy (s) JSON | Ratio report | Ratio JSON | Delta report | Delta JSON |
|---|---|---|---|---|---|---|---|---|
| uniform | 0.001880 | 0.001879893... | 0.000140 | 0.000140232... | 0.0746x | 0.07459... | 0 | 0 |
| clustered | 0.096477 | 0.096476841... | 0.046966 | 0.046966100... | 0.4868x | 0.48681... | 1 | 1 |
| shell | 0.005670 | 0.005669653... | 0.002724 | 0.002723739... | 0.4804x | 0.48040... | 2 | 2 |

All report values match the JSON artifact (within 4-decimal display rounding). The stdout timing values also match the JSON `elapsed_sec` for the last (best) repeat of each run.

The report's interpretation — "The CuPy grid CUDA-core opponent is faster on these 65K fixtures" — is accurate. CuPy is ~13.4× faster on uniform and ~2.1× faster on clustered and shell.

The "CuPy/RTDL ratio" column heading in the report correctly labels these as sub-1.0 values (CuPy faster). This is not obscured or inverted.

### Q4 — Does the manifest update avoid overclaiming Triton, public speedup, RTNN paper reproduction, or native app customization?

**Yes. All claims are explicitly blocked at every layer.**

In `src/rtdsl/v2_5_triton_app_migration.py`, the `rtnn` manifest row (lines 296-306):
- `canonical_harness_status: "ready_with_goal2800_live_ranked_summary_harness"` — scoped to this harness only.
- `next_action`: explicitly keeps "dense exact top-k Triton auto-selection blocked until a tiled top-k route beats the same-contract CuPy grid opponent" — no premature Triton promotion.

In the harness `CLAIM_BOUNDARY` dict (lines 22-33), all nine overclaim flags are `False`:
- `public_speedup_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `rtdl_beats_rtnn_claim_authorized: False`
- `rtdl_beats_cupy_grid_claim_authorized: False`
- `broad_rt_core_speedup_claim_authorized: False`
- `triton_speedup_claim_authorized: False`
- `paper_reproduction_claim_authorized: False`
- `native_engine_customization: False`

This `CLAIM_BOUNDARY` dict is copied into both the top-level JSON artifact and each per-row result — there is no path where a consumer can receive a row without the boundary flags.

The report's "Not claimed" section (report lines 96-106) recites all the same boundaries in prose, consistent with the JSON. No discrepancy found.

### Q5 — Are app-specific RTNN policies kept outside the native engine contract?

**Yes.**

The harness calls the engine with generic parameters:
- `result_mode="ranked-summary-raw"` — a generic contract mode, not RTNN-specific.
- `k_max=50` — a numeric bound, not app-specific semantics.
- The engine is asked to do fixed-radius neighbor search in 3D; no RTNN-specific indexing policy, approximate-neighbor policy, or paper-defined behavior is embedded in the engine call.

The `V25TritonBenchmarkAppPlan` for `rtnn` (migration file lines 187-189) explicitly records: "Approximate-neighbor policy remains app code; primitive behavior is grouped candidate ranking."

The JSON `contract` per row correctly labels: `"family": "fixed_radius_neighbors_3d"`, `"mode": "ranked-summary"`, `"exact": true` — these are generic contract descriptors. `"same_contract_opponent": "cupy_grid_exact_ranked_summary_3d"` names the opponent at the contract level, not the app level.

`"native_engine_customization": false` is set correctly throughout.

### Q6 — Is a clean-from-Git rerun still correctly identified as pending before final evidence closure?

**Yes.**

The report is explicit at three points:
- Line 6-7: `Status: implemented locally with first OptiX/CuPy pod evidence.` and `Verdict: accept-with-boundary pending external review and clean-from-Git rerun.`
- Lines 62-63: "The new Goal2800 script was copied into that checkout for the first artifact run. A clean-from-Git rerun must follow after the Goal2800 commit is pushed."
- Lines 123-124: "Focused tests, external review, consensus, and clean-from-Git pod validation are still pending at the time this report was first written."

The first evidence run was executed at commit `6da008bc` by copying the script manually. The Goal2800 commit has since been pushed (the current branch `main` is at `6da008bc` or later per the git log), but the clean-from-Git pod rerun is not yet recorded — the current JSON artifact does not contain a `clean_rerun_commit` or equivalent field.

**Additional note:** The test file (`tests/goal2800_rtnn_v25_live_ranked_summary_harness_test.py:12`) references `CONSENSUS = .../goal2800_rtnn_v2_5_live_ranked_summary_harness_consensus_2026-05-31.md`. The `test_report_and_consensus_keep_boundary` test (line 58) reads this file and will fail until consensus is written. This is expected behavior given the "pending external review" status, and this review document can serve as input to that consensus file.

---

## File-Grounded Findings

| Severity | Location | Finding |
|---|---|---|
| Note | `harness.py:171-175` | Tolerance formula bottoms out at floor=2 for all distributions at 65K scale. Proportional arm is dormant at this size. Correct behavior but worth documenting for scale changes. |
| Note | `harness.py:56-58` | `tempfile.TemporaryDirectory` is created but then overridden by `work_dir` if provided. The `temp_name` directory is created and then abandoned if `work_dir` is given. Minor resource waste but functionally correct. |
| Note | `test:12,58` | `CONSENSUS` file does not yet exist; `test_report_and_consensus_keep_boundary` will fail until consensus is written. Expected pending state, not a defect. |
| Pass | `json artifact` | All claim boundary flags consistent across top-level and all three row-level objects. |
| Pass | `json vs. report` | All timing, count, delta, tolerance, and ratio values in report table exactly match JSON artifact values (within display rounding). |
| Pass | `stdout vs. json` | All final-repeat elapsed_sec values in stdout match JSON `elapsed_sec` fields for both RTDL and CuPy runs. |

---

## Boundary Notes for Public Claims

- CuPy grid is faster on all three 65K fixtures. This must not be inverted into an RTDL speedup claim in any downstream summary or public communication.
- The `cupy_grid_over_rtdl_elapsed_ratio < 1.0` values (0.0746, 0.4868, 0.4804) indicate CuPy is faster, not RTDL. Any consumer reading `cupy_grid_over_rtdl_elapsed_ratio` must interpret it as "CuPy elapsed / RTDL elapsed" — a ratio below 1 means CuPy is faster.
- The Tier B designation is appropriate. This is live parity evidence, not a benchmark win claim.
- Dense exact top-k Triton auto-selection remains blocked. The next_action in the manifest correctly records this condition.
- The pod was an RTX A5000 with driver 570.211.01 and CuPy 14.1.0. Performance numbers are specific to this pod environment and must not be generalized as architecture-independent claims.

---

## Confirmation

This review is an independent Claude (Sonnet 4.6) review. It was not produced by Codex and does not share context with prior Codex reviews of this goal. All findings are derived solely from reading the six files listed in the handoff document.
