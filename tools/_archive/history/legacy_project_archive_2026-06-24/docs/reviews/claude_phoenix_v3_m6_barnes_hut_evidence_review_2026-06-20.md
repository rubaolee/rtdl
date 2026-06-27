Now I have a complete picture. Let me write the formal review.

---

## Phoenix V3 M6 Barnes-Hut Evidence Review

**Reviewer:** Claude (Sonnet 4.6)
**Date:** 2026-06-20
**Scope:** Accept/reject as internal route-parity evidence under Goal4392 V3 plan only — not V3 release authorization.

---

### Fact Verification

All five facts stated in the call for review check out against the artifacts:

| Fact | Verdict | Notes |
|---|---|---|
| OOM failure preserved, not hidden | **Confirmed** | `m6_barnes_hut_rerank.log` contains the full traceback; evidence test asserts `"out of memory" in log.lower()` |
| Successful run partitions by body count then merges JSON | **Confirmed** | Partitioned log shows sequential `BODY_START/BODY_END` blocks; ends with `"merged_rows": 12` (3 body counts × 4 routes = 12) |
| `status: pass`, `overall_status: internal_m6_route_parity_evidence`, all claim flags false, M7-qualified rows = 0 | **Confirmed** | Summary JSON fields verified against the status doc and intake script logic |
| `numba_cuda_fused` fastest at all three scales | **Confirmed** | `fastest_by_scale` = `{"32768": "numba_cuda_fused", "65536": "numba_cuda_fused", "131072": "numba_cuda_fused"}`, `optix_fastest_scales: []` |
| OptiX+Numba slowdown ratios 7.328x / 5.120x / 13.912x | **Confirmed** | JSON values are 7.3282…, 5.1200…, 13.9116… (13.912 after 3-dp rounding is correct) |
| No claims of RT-core speedup, whole-app speedup, paper reproduction, auto partner selection, release authorization | **Confirmed** | Boundary section enumerates each non-claim explicitly |

---

### P0 Findings

**None found.**

The evidence is correctly scoped, structurally honest, and its key outcome (fused Numba CUDA beats prepared OptiX at 32k–131k bodies) is robust to the issues raised below.

---

### P1 Findings

**P1-1: Mixed timing basis is not labeled on the ratio numbers in the route matrix**

The intake script explicitly enforces that `numba_cuda_fused` uses `hot_time_kind == "cuda_event_kernel"` (kernel-only, CUDA-event scoped). CPU/Numba and both prepared OptiX routes use the runner's `hot_median` wall clock, which includes Python dispatch, memory setup, and host-device transfer overhead.

The methodology note acknowledges the difference, but the route matrix table — `7.328x / 5.120x / 13.912x` — presents these as direct route-vs-route ratios with no indication that they compare kernel time to wall time. A reader of the table alone would assume like-for-like.

This does **not** corrupt the internal classification (all claim flags are false, OptiX would likely still lose under a wall-clock-to-wall-clock comparison given the scale of the gaps). But if these ratios are ever cited forward — in an M7 packet, a performance table, or a planning doc — the heterogeneous basis makes them misleading.

**Required fix:** Add a note under the route matrix table (in `intake_summary.md` and the pod evidence doc) that explicitly says: "Ratios compare CUDA-event kernel time for fused Numba CUDA against wall-clock hot median for all other routes. These are not kernel-to-kernel comparisons." The intake script should also output a `timing_basis_mixed: true` field in the summary JSON so downstream tools can gate on this.

---

**P1-2: No test runs the intake script against the current partitioned rerank JSON**

`v3_phoenix_m6_barnes_hut_intake_test.py` runs the intake script against the **historical M87** artifact (`goal4483_v3_0_m87_barnes_hut_large_scale_rerank_2026-06-16.json`).

`v3_phoenix_m6_barnes_hut_evidence_test.py` reads the **pre-computed summary JSON** (`m6_barnes_hut_intake_summary.json`), not the raw rerank JSON.

No test runs:
```
python scripts/v3_phoenix_m6_barnes_hut_intake.py \
  --rerank-json docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json
```
and verifies the output matches the stored summary. The stored summary JSON could be manually edited without any test failing.

**Required fix:** Add a test case to `v3_phoenix_m6_barnes_hut_intake_test.py` (or the evidence test) that runs the intake script against `m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json` and asserts `status == "pass"`, `overall_status == "internal_m6_route_parity_evidence"`, and all claim flags false. This closes the chain from raw artifact to stored summary.

---

### P2 Suggestions

**P2-1: The 131,072-body timing shows anomalous scaling that is not called out**

`numba_cuda_fused` goes 11.249 → 34.738 → 44.445 ms (roughly linear 32k→65k, then barely increases 65k→131k despite doubling the body count). This is unexpectedly favorable for an O(N log N) algorithm and is almost certainly an artifact of CUDA-event timing capturing only the inner kernel, not data setup. The document's wording "Large rows are route-parity evidence, not full exact-force oracle rows" gestures at this but doesn't call out the scaling anomaly. A brief note would improve credibility for future reviewers.

**P2-2: The widened checksum tolerance for 131,072 bodies is not highlighted**

The 131,072-body run uses `tolerance_x = 3.43e-4` and `tolerance_y = 4.19e-4` (derived from relative tolerance against the accumulated force magnitude), versus the default `1e-4` for smaller body counts. The deltas are well within tolerance (1.0e-8 and 2.2e-7 respectively), so this is not a correctness concern. But the automatic widening is not mentioned in any doc or test. A passing note in the methodology section would help reviewers trust the check rather than wonder if the tolerance was tuned to pass.

**P2-3: The `optix_cupy_prepared_frontier` route timing is not exposed in the summary**

The summary only tracks `optix_numba_prepared_frontier` in the ratio. `optix_cupy_prepared_frontier` exists in the run but its timing is not surfaced in the summary JSON or the route matrix. For completeness as route-parity evidence, it would be useful to know whether CuPy and Numba OptiX routes perform similarly or diverge at scale.

**P2-4: `"merged_rows": 12` in the partitioned log is correct but not self-documenting**

The log line `{"body_counts": [32768, 65536, 131072], "merged_rows": 12}` is correct (3 × 4 = 12), but readers must infer the multiplication. A comment or structured log line `merged_rows_per_body_count: 4` would be clearer for future runs with a different route set.

---

### Answers to the Five Questions

1. **Is this evidence honestly classified as internal M6 route-parity evidence?**  
   Yes. The classification is conservative and accurate. All claim flags are false. The boundary section enumerates every non-claim explicitly. The docs do not conflate "four routes ran with checksum parity" with "RT cores accelerate Barnes-Hut."

2. **Are the claim boundaries strong enough, especially around prepared OptiX losing?**  
   Yes, with P1-1 caveat. The boundary language is complete and the non-claim list is exhaustive. The only weakness is the route matrix table's ratio numbers appear to be apples-to-apples when they are not (kernel time vs. wall clock). Fixing P1-1 closes this.

3. **Is the failed single-process OOM handled correctly?**  
   Yes. The log is preserved, explained, and tested. The partitioned corrective run is documented with its rationale. The Goal-Level Decision Audit is present and honest about what caused the failure.

4. **Does the intake script enforce the right checks without overfitting to a desired result?**  
   Mostly yes. The script enforces structural completeness (4 routes, contribution count agreement, checksum parity, dry_run=false, repeat≥11, warmup≥2, all claim flags false, OptiX-route metadata, and CUDA event timing for the fused Numba route). It does not enforce a specific winner — the `headline` text changes if OptiX wins; the `overall_status` remains `internal_m6_route_parity_evidence` regardless. The only overfitting concern in the evidence test (`assertGreater(optix_numba_over_fastest, 5.0)`) is appropriate for an evidence-archival test verifying a frozen artifact, not a run-time gate.

5. **What P0/P1 changes are required before Codex can close this bounded M6 goal?**  
   No P0 changes. Two P1 changes:  
   - Add explicit mixed-timing-basis labeling to the ratio table and a `timing_basis_mixed` field to the summary JSON (P1-1).  
   - Add an end-to-end test that runs the intake script against the stored raw rerank JSON (P1-2).

---

### Final Recommendation

**verdict: approve-with-required-fixes**

The evidence is structurally honest and correctly classified. It closes the M6 evidence gap as stated: four routes across 32k/65k/131k bodies, checksum parity, all claim flags false, no release authorization. The OOM failure is preserved. The docs do not overclaim.

The two P1 fixes are required before Codex closes this goal — they do not require a re-run, only a documentation annotation and an additional test case. Once P1-1 (timing basis label) and P1-2 (end-to-end intake test) are added, this evidence can be accepted as closed internal M6 route-parity evidence under the Goal4392 V3 plan, with the M6 compliance table entry updated to "internal-route-parity: closed" and the release blocker updated accordingly. M6 should stay internal until M7 row review, consistent with what the docs already say.
