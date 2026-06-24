I have everything I need. Here is the formal review.

---

## Review: Phoenix V3 Barnes-Hut Fused Partner M7 Candidate

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-06-21  
**Verdict: `approve-with-amendments`**

---

### Evidence audit

#### Timing basis (critical check)

The intake summary at line 77 of `m6_barnes_hut_intake_summary.json` explicitly states: *"Fused Numba CUDA uses CUDA-event kernel timing when available; CPU/Numba and prepared OptiX routes use the runner's hot median. The route ratios therefore compare CUDA-event kernel time against wall-clock hot median; they are not kernel-to-kernel comparisons."*

The same-basis no-go packet (`checks.timing_basis_mixed_removed_for_ratios: true`, `same_basis_timing_kind: wall_repeat_median_seconds`) correctly resolved this by extracting `call_wall_median_seconds` (wall call path) for the Numba CUDA route rather than `original_hot_median_seconds` (kernel event path). The candidate packet inherits this corrected basis via `repeat_seconds_median`.

Verification: at 131K, wall-call path = 45.493 ms vs kernel-event path = 44.445 ms. The candidate packet uses 45.493 ms. This is correct. The intake summary's `comparisons` block used kernel-event time (producing 13.912x over OptiX); the candidate packet's wall-call basis produces 13.591x. The same-basis correction slightly reduces the apparent GPU speedup, which is the honest direction.

**Math spot-check (all pass):**
- 185.684 / 45.493 = 4.082x ✓
- 618.302 / 45.493 = 13.591x ✓
- 110.559 / 35.643 = 3.102x ✓ (floor min, barely above 3.0)
- 87.943 / 11.739 = 7.492x ✓

---

### Q1 — Legitimate V3 language/engine capability or Barnes-Hut app tuning?

**Finding: Legitimate, with one condition that must be stated in the row.**

The contract name `generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1` is app-agnostic. The script verifies the source class block contains no "Barnes-Hut" or "barnes_hut" strings. The smoke metadata shows `native_engine_app_specific: false`. The API names (`prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda`, `sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda`) carry no application reference.

The capability being promoted is: **fused Numba CUDA JIT kernel for weighted vector accumulation over a pre-built aggregate tree with no frontier or contribution row materialization on the hot path.** This is a genuine engine/language capability. Barnes-Hut is the test harness.

**Condition:** The row must note that the evidence was obtained on a Barnes-Hut (theta=0.5, 2D, bucketized) tree structure. The contract is agnostic; the evidence base is not. This distinction belongs in the row metadata, not in the claim wording.

---

### Q2 — Is evidence sufficient for exactly one row-scoped M7 promotion?

**Finding: Yes, for M7 milestone scope (not release scope).**

The validation tier is tiered and appropriate:

| Layer | Detail | Status |
|---|---|---|
| Small-scale exact | 64 bodies, CPU oracle, max diff 5.68e-14 (x) / 1.14e-13 (y) | Pass |
| Large-scale correctness | Route parity at 32K/64K/128K, checkcsum delta << tolerance | Pass |
| Large-scale oracle | Independent exact-force CPU oracle at large scale | **Not claimed** |

The large-scale gap is the acknowledged blocker. For M7 milestone promotion of a single row-scoped partner claim, route parity at r=11 warmup=3 is sufficient given:
- The small-scale exact test establishes the contract is numerically sound
- The performance gap is large enough (>3x minimum on all scales) that noise is not a confound
- The claim is explicitly scoped to one row, not a release

For a future public release row, an independent oracle at 131K scale would be required.

---

### Q3 — Are the blockers honest enough?

**Finding: Yes. All four blockers are real and correctly stated.**

The key claim-suppression flags are all false: `release_authorized`, `public_speedup_claim_authorized`, `row_scoped_public_speedup_claim_authorized`, `broad_v3_faster_than_v2_claim_authorized`, `rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `m7_promotion_authorized`. The packet self-guards well.

One small addition I would require (see amendment below): the draft claim wording does not currently surface the validation tier. The row metadata should carry it explicitly.

---

### Q4 — Does the large-row validation basis need a fresh POD rerun before promotion?

**Finding: No, for M7 milestone. Yes, for any future public release row.**

The evidence artifact is one day old (June 20). The run is r=11 warmup=3 (the intake summary confirms warmup=3, slightly exceeding the check floor of 2). The performance gap at the claimed scale (131K, 4.082x CPU, 13.591x OptiX) is large enough that re-running would not change the conclusion. A borderline result would require a fresh rerun; this is not borderline.

The OptiX frontier-emission route degrading from ~7x slower at 32K to ~13.6x slower at 131K (scaling worse with problem size) and the Numba CUDA fused route scaling well across all three sizes are both credible patterns for this class of computation.

---

### Q5 — If approved, what exact wording and row ID?

**Row ID (retain as-is):**
```
aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped
```

**Draft claim wording (amended):**

> Generic aggregate-tree fused weighted-vector sum, Numba CUDA partner (`generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1`): at 131,072 bodies on a Barnes-Hut tree (theta=0.5, 2D), 45.493 ms wall-repeat median (r=11, warmup=3), 4.082x faster than CPU/Numba fused baseline. Not an RT-core claim. Large-scale validation: route parity plus checksum across three scales; independent exact-force CPU oracle not claimed at this scale.

Changes from the draft: (1) added "on a Barnes-Hut tree (theta=0.5, 2D)" to anchor the evidence basis; (2) added the warmup count; (3) appended the validation tier sentence. The 13.591x-over-OptiX figure is informational (the OptiX route was already declared no-go) and should appear only in supplementary metadata, not the canonical row wording.

---

### Amendments required before the M7 row is written

1. **Add evidence-basis note to row metadata** — `evidence_tree_structure: barnes_hut_theta_0.5_2d_bucketized`. The contract is generic; the evidence was not. A future user of this row needs to know the domain.

2. **Add validation tier to row metadata** — `large_scale_validation_tier: route_parity_plus_checksum_no_independent_oracle`. The packet already lists this as a blocker, but it must be promoted into the row record, not left in the candidate packet.

3. **Suppress the "13.591x over OptiX" figure from the row claim wording.** It belongs in supporting metadata. Headlining a comparison against a route that is already no-go is misleading in isolation. The CPU/Numba comparison (4.082x) is the defensible primary figure.

4. **Pin the row to the artifact.** Row metadata should reference `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json` as the evidence source, so the row is not later detached from the run that generated it.

---

### What this review does not approve

- Any whole-application Barnes-Hut claim
- Any RT-core claim
- Any broad V3-over-V2 claim
- Any paper reproduction claim against Nagarajan et al. PPoPP 2025
- Public release authorization (that requires an independent oracle at scale and a separate release review)
- The 13.591x figure as primary claim wording

---

### Summary

The candidate packet is structurally honest: it does not promote before external review, it correctly flags all over-claim guards as false, it disclosed the validation tier as a blocker, and the same-basis timing correction is handled properly. The performance evidence is clear and the floor checks are met. The four required amendments are housekeeping — none of them reverse the capability finding.

**Verdict: `approve-with-amendments`**  
Exactly one row-scoped `aggregate_frontier` / `vector_accumulation` M7 row may be added after the four amendments above are incorporated into the row record. No public claim, no release flag, no RT-core language.
