I have now read all nine required files. Here is the full external review.

---

## RTDL V4 Section 8 External Review
**Date:** 2026-06-24
**Branch:** codex/v4-tier2-section8

---

## Verdict

**`accept_protocol_revision_to_prepared_hot_path_required`**

The final rerun is valid. The strict whole-call gate fails as written. The scalar fused primitive track survives with narrow claim wording. The summary route requires a protocol revision to measure prepared-session hot-path timing before it can be credited. No architecture revision is required by this result, and no V4 release is authorized.

---

## Question-by-Question Findings

---

### 1. Is the final rerun valid, and does the strict written whole-call gate fail?

**Measurement validity: yes, with one prior defect now corrected.**

The first 8192 attempt exposed a real bug: `run_app()` in `output_mode="full"` was calling `brute_force_outlier_rows()` as the oracle inside the timed path, adding O(N²) work to the baseline. This was fixed: `run_app()` now uses `expected_tiled_density_rows()` (O(N) tiled pre-computation) across all output modes. A regression test (`test_outlier_full_mode_uses_tiled_oracle_not_quadratic_bruteforce`) pins this fix. The correction is correct and the test is adequate.

The final rerun uses:
- 7 measured repeats, 1 warmup per route per size — protocol-compliant
- Whole-call timing of `run_app()` for all three routes — consistent methodology
- All three correctness gates pass (`matches_oracle: true`, `outlier_count` and `point_count` matching across routes)
- `native_continuation_active: true` and `native_continuation_backend: optix_threshold_count` confirmed for both fused routes
- `generic_primitive: FIXED_RADIUS_COUNT_THRESHOLD_2D` confirmed — no app-identity kernel

One secondary issue worth noting: `make_outlier_case()`, `expected_tiled_density_rows()`, and the oracle comparison are all inside the timed `run_app()` call for all three routes. This is consistent — the extra overhead appears in all baselines equally — and the fixture costs are O(N), not O(N²). This does not invalidate the measurement.

**Gate outcome:**

| copies | points | scalar speedup | scalar gate (≥2.0x) | summary speedup | summary gate (≥1.5x) |
|---:|---:|---:|:---:|---:|:---:|
| 8192 | 65,536 | 2.100x | pass | 1.415x | **fail** |
| 32768 | 262,144 | 2.157x | pass | 1.394x | **fail** |
| 131072 | 1,048,576 | 2.434x | pass | 1.497x | **fail** (raw: 1.4973x) |

- Scalar gate: pass on all 3 sizes (≥2 required)
- Summary gate: fail on all 3 sizes (≥2 required); the 131072 case misses by 0.003x — close, but the raw JSON value is unambiguous at 1.4972605752246604

`performance_gate.status: "fail"`, `v4_tier2_thesis_locally_validated: false`, `authorized_next_step: "stop_v4_performance_release_and_revisit_architecture"`.

**The strict written whole-call gate fails. This is confirmed.**

---

### 2. Does the phase profile validly show that prepared-session hot-path summary beats rows by >2x at all sizes?

**The phase profile's >2x claim is internally valid. It measures a different thing than the main harness.**

From the phase profile medians:

| copies | rows_total (s) | summary_without_prepare (s) | ratio |
|---:|---:|---:|---:|
| 8192 | 0.602 | 0.293 | 2.06x |
| 32768 | 2.540 | 1.243 | 2.04x |
| 131072 | 12.316 | 5.261 | 2.34x |

The `summary_total_without_prepare_sec` = `summary_native_run_sec` + `summary_python_convert_sec`. This is valid as a hot-path measurement: the profiler opens the context manager once, runs both queries within the prepared session, and measures query time separate from scene setup. `scene_prepare_sec_this_batch: 0.0` confirms no per-query re-prepare happens inside the context.

**Concerns about the phase profile as evidence:**
1. Only 3 repeats, versus 7 in the main harness. Less statistical confidence.
2. The "rows" baseline in the phase profile (0.602s at 8192) is lower than the main harness baseline (0.764s at 8192) because it excludes `make_outlier_case()` and oracle comparison. The phase profile is comparing hot-path summary against a stripped-down rows path. This is appropriate for the isolated comparison, but the two baselines are not the same number.
3. The `_profile_once()` function creates a fresh prepared scene on every call (via `with rt.prepare_generic_...`). The "without prepare" timing is only the query within that session — but each outer repeat is a full re-prepare. This correctly isolates the hot path, but the phase profiler is not a batch-session test: it measures query time assuming prepare is already done, by timing only the inner call.

The phase profile result is valid as exploratory evidence that the hot-path summary query (with amortized prepare) is competitive. It does not retroactively pass the main harness gate, and the report correctly declines to claim it does.

---

### 3. Should the protocol be revised to measure prepared-session hot-path timing, or should the whole-call fail remain controlling?

**The whole-call fail is controlling for this experiment. A protocol revision is the required next step before any summary route credit.**

**Why the whole-call fail stands:**
- The written protocol was agreed to before the experiment. Revising the metric after observing results is not permitted without external review approval.
- The whole-call timing reflects what users experience with the current `run_app()` API: the `_run_optix_prepared_density_summary()` function opens and closes the prepared context on every call, paying the prepare cost each time.
- The closest size (131072) misses by 0.003x — this is not a rounding error or noise; the raw JSON is unambiguous.

**Why a protocol revision is warranted (not a rejection of the architecture):**
- The `PreparedOutlierDetectionSession` class already exists in the app and correctly models the reuse scenario. This is a legitimate API, not a post-hoc rationalization.
- The scalar route already passes the strict gate with prepare included (2.1–2.4x). The scalar evidence validates the fusion thesis at the kernel level. The summary route's failure is specifically about Python-side output materialization overhead (`_density_rows_from_count_rows`) plus scene setup, not fusion itself.
- The phase profile confirms the hot-path summary query is real and >2x when prepare is amortized, which motivates the protocol revision.

**What the revision must include (see Q5 below).**

---

### 4. Is preserving the scalar fused primitive track authorized, with narrow claim wording only?

**Yes, authorized — with the following exact scope.**

The scalar fused primitive (`optix_fused_prepared_scalar`) passes the strict gate on all 3 serious sizes. Correctness is verified. `native_continuation_active: true`, `native_continuation_backend: optix_threshold_count`, `generic_primitive: FIXED_RADIUS_COUNT_THRESHOLD_2D` — not an app-identity kernel.

**Authorized narrow claim:**
> On the fixed-radius threshold-count operator with `copies=8192–131072` (65,536–1,048,576 points) on NVIDIA RTX 4000 Ada Generation (Driver 550.127.05, OptiX 8.0.0), the fused native scalar primitive (`FIXED_RADIUS_COUNT_THRESHOLD_2D`, `REDUCE_INT(COUNT)`) beats the separated Tier-1 row-materialization route by 2.1x–2.4x median whole-call wall time. This is not a broad V4 speedup claim, not a V3/V2 claim, not a near-handwritten OptiX claim, and does not generalize beyond the measured operator and fixture.

**Not authorized:**
- Summary route credit (failed its gate)
- Promotion of any additional Tier-2 primitives (requires the revised protocol to pass first)
- Any release or POD spend beyond the revised protocol experiment

---

### 5. What exact next experiment is required before adding more Tier-2 primitives?

**Required: A formally revised Section 8 protocol for prepared-session hot-path timing.**

The revised protocol must specify:

1. **Session boundary:** Use `PreparedOutlierDetectionSession` (or equivalent). Prepare once. Run ≥7 measured calls within the same session without re-preparing. The timed window is the query call only.

2. **Baseline:** The rows route measured the same way (emit + reduce), excluding `make_outlier_case()` and oracle comparison — matching the isolation level. The baseline must be measured in the same script run as the candidate to control for GPU state and thermal variance.

3. **Sizes:** Same serious sizes: 8192, 32768, 131072 copies. No relaxation.

4. **Repeats:** ≥7 measured hot-path calls per route per size, 1 warmup.

5. **Gate:** Summary prepared hot-path ≥1.5x over rows baseline on ≥2 serious sizes. The gate level is unchanged; only the timing boundary changes.

6. **Route D (hand-written OptiX reference):** If a hand-written OptiX reference for this exact contract can be obtained, run it as the ceiling. Without it, "near hand-written OptiX" wording remains unauthorized.

7. **External review:** The revised protocol document and the result JSON must both be externally reviewed before any Tier-2 primitive promotion.

**No additional Tier-2 primitives may be promoted until this revised protocol passes and receives external review approval.** The scalar primitive is already evidenced; it does not need this revised experiment. But the summary route does, and no third primitive begins until the summary route question is resolved.

---

### 6. Unauthorized claim confirmation

The following claims are confirmed as **not authorized** by any evidence in these files:

| Claim | Status | Evidence |
|---|---|---|
| V4 release claim | **Not authorized** | `release_claim_authorized: false` in result JSON; report explicitly states "No V4 release claim is authorized." |
| Broad V4 speedup wording | **Not authorized** | Claim boundary in harness JSON limits authorization to "fused primitive vs separated RTDL route" only |
| Near-handwritten OptiX wording | **Not authorized** | `independent_handwritten_optix_reference_available: false`, `near_handwritten_optix_claim_authorized: false` in result JSON |
| Tier-3 PTX/user-callback claim | **Not authorized** | No Tier-3 measurement performed; architecture design §6 explicitly marks it a "falsifiable spike" not gating V4.0 |
| App-specific native engine claim | **Not authorized** | Boundary string in harness JSON and app code: "not a KNN/Hausdorff/Barnes-Hut claim... not an outlier-specific native engine ABI" |
| Automatic partner selection claim | **Not authorized** | `automatic_partner_selection_authorized: false` in app code metadata |
| True-zero-copy claim | **Not authorized** | `true_zero_copy_claim_authorized: false` in app code metadata |
| Broad V3-over-V2 wording | **Not authorized** | Not measured in this experiment; claim boundary does not extend there |

All prohibitions from the protocol document, architecture design §12 (Non-authorization), and the harness claim boundary are intact in the evidence files and code.

---

## Summary

The rerun is valid. The strict whole-call gate fails as written: the summary route does not reach 1.5x on any serious size (closest: 1.497x at 131072). The scalar fused primitive is real, passes at 2.1–2.4x, and may be preserved with narrow claim wording. The gate failure is not an architecture invalidation — the fusion thesis is validated at the scalar output level. The summary route's failure is a measurement-boundary issue (prepare included in whole-call vs. hot-path reuse), which the phase profile shows is material. The path forward is a formally revised protocol for prepared-session hot-path timing, external-reviewed before any summary route credit or Tier-2 primitive promotion. No V4 release, no near-OptiX wording, no Tier-3 claim, and no additional primitive track is authorized.
