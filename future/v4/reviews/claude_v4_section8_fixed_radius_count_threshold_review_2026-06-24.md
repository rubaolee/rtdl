I have all seven files. Rendering the verdict now.

---

## RTDL V4 Section 8 — External Reviewer Verdict

**Date:** 2026-06-24  
**Verdict:** `accept_strict_fail_revise_architecture`

---

### 0. Reading summary

Three-tier architecture doc defines the gate. Protocol translates it into two numeric thresholds (scalar ≥ 2.0x on ≥2 sizes; summary ≥ 1.5x on ≥2 sizes). Evidence JSON and report agree: scalar passes all three sizes, summary passes only the largest size. Gate fails. The harness's own `authorized_next_step` field correctly reads `stop_v4_performance_release_and_revisit_architecture`.

---

### Q1 — Oracle-boundary fix validity

**The fix is valid. No rerun with a different correctness strategy is required.**

The first attempt timed `output_mode=full` with `brute_force_outlier_rows` as the oracle inside the measured path — O(N²) work artificially inflating the rows-baseline timing. The fix substitutes `expected_tiled_density_rows`, which is the closed-form tiled oracle and O(N). The re-run post-fix numbers are the correct ones.

The regression test `test_outlier_full_mode_uses_tiled_oracle_not_quadratic_bruteforce` patches `brute_force_outlier_rows` to raise `AssertionError("quadratic oracle")` and confirms the full-mode path never calls it. That lock is structurally correct.

One caveat to record: the oracle is an exact hardcoded tiling of 8 base points. It is correct for the defined fixture. Its correctness depends on the fixture remaining `make_outlier_case` — which it is. This is not a weakness but is worth noting for any future fixture change.

---

### Q2 — Measurement validity for a fail verdict

**Yes. The measurement is valid enough to accept the strict gate outcome as fail.**

Credibility checklist:
- Three serious sizes: 65K, 262K, 1M points. ✓
- 7 repeats + 1 warmup per route per size. ✓
- Correctness passes all three sizes on all three routes. ✓
- Median used for gate comparison. ✓
- Gate failure is not borderline noise: summary speedup at 8192 is 1.406x (7% below gate), at 32768 is 1.389x (7% below gate). Not measurement uncertainty.

**Measurement weaknesses that must be recorded:**

1. **High-variance outliers in the scalar route at larger sizes.** At copies=32768, two runs land at ~1.88–1.90s against a pack of ~1.51–1.54s (≈25% above median). At copies=131072, two runs land at ~7.46–7.52s against a pack of ~5.98–6.18s (≈22% above median). Seven repeats with two high outliers is atypical. These outliers do not change the gate outcome (median still clears 2.0x with room), but they suggest transient GPU scheduling or L2/memory-bandwidth competition on the pod. Future experiments should use at least 10 repeats at large sizes to characterize this variance.

2. **`generic_primitive: null` and `summary_primitive: null` on the summary route.** Every summary route entry in the JSON shows these fields as null, while `native_continuation_active: true` and `native_continuation_backend: "optix_threshold_count"` are set. The `_is_fused_fixed_radius_route` check still identifies it correctly (matches `"threshold_count"` in `native_continuation_backend`), but the null primitives indicate the `_run_optix_prepared_density_summary` code path does not plumb `primitive` or `summary_primitive` from the underlying `rt` result back into `run_app`'s return dict. This is a metadata gap, not a correctness or gate-logic error, but it should be closed before the next validation run.

3. **No independent hand-written OptiX reference (Route D not run).** `independent_handwritten_optix_reference_available: false` is hardcoded in the harness's plan. This is the correct record, but it means the gap between the fused primitive and actual hand-written OptiX is entirely unknown. "Near hand-written OptiX" remains an unverifiable assertion, not an evidenced claim.

4. **Single hardware platform (RTX 4000 Ada).** Acceptable for a scoped gate experiment; noted for the record.

---

### Q3 — Should V4.0 stop the broad Tier-2 performance-release path?

**Yes. Under the written protocol, the broad Tier-2 performance-release path must stop.**

The protocol (`performance_gate.status: "fail"`) is unambiguous. The architecture doc (§12) says: "No POD spend beyond the §8 focused validation, no public speedup claim before §8 validates." The gate failed. The harness emits `stop_v4_performance_release_and_revisit_architecture` as the authorized next step.

There is no ambiguity in the reading. The summary route's failure at the two smaller sizes is not close enough to attribute to measurement noise. The path must stop for architecture revision.

---

### Q4 — Is it valid to preserve a narrower scalar fused primitive track while revising the summary-route claim?

**Yes, with strict conditions.**

The scalar fused primitive (`density_count` / `FIXED_RADIUS_COUNT_THRESHOLD_2D`) is materially validated: 2.10x, 2.13x, 2.45x across all three sizes. This result is consistent, passes the gate on all three sizes (gate only required two), and the route correctly records `native_continuation_active: true`, the named generic primitive, and `summary_primitive: REDUCE_INT(COUNT)`. This is a real, narrow, evidenced result that should not be discarded.

**Conditions for a narrower scalar track:**

- Authorized claim wording may not exceed: "On the measured fixed-radius threshold-count query, the scalar fused native primitive beats the separated row-materialization route by 2.1x–2.4x median on 65K–1M points on RTX 4000 Ada." No generalizations.
- "Near hand-written OptiX" wording remains forbidden until Route D is run.
- The summary route claim must be explicitly revised. The scalar pass does not carry the summary route.
- The gap between the scalar and summary routes must be explained before a revised summary claim is made (see Q5).

---

### Q5 — What next experiment is required before adding more Tier-2 primitives?

Before any new primitive is added, the following must be completed in order:

**Step 1 — Diagnose the summary route underperformance (cheap, required).**  
The summary route at copies=8192 writes 65,536 compact rows, and the separated route writes 163,840 neighbor rows (2.5 neighbor rows per query point on average for this fixture). The theoretical memory reduction ratio is ~2.5x, but the achieved speedup is only 1.41x. Either: (a) the summary route kernel has higher per-point overhead than expected; (b) N=65K compact row writes still dominate the kernel time; or (c) the route has preparation overhead (BVH reuse, context switching) that eats the savings at smaller N. Profile the summary route (kernel time vs buffer allocation vs host-to-device transfer) at copies=8192 and report where time is spent. Do not add primitives until this is answered.

**Step 2 — Run Route D (independent hand-written OptiX reference) for the scalar primitive.**  
Write or locate a minimal hand-written OptiX kernel that performs the same fixed-radius threshold-count query on the same point set. Measure it with the same methodology. This is the only way to locate where the fused primitive sits relative to the theoretical ceiling, and to evaluate whether the architecture's "near hand-written OptiX" thesis is true for even this one primitive.

**Step 3 — App-catalog coverage audit.**  
Before claiming the scalar primitive generalizes to "80% of workloads," enumerate the existing app catalog and count how many apps' continuation logic maps to count-threshold scalar. Report the real number.

**Step 4 — Only after Steps 1–3:** run a second primitive (e.g., `event_ordered_grouped_ray_id_reduction`) through a full Section 8-style experiment. Do not promote the primitive library until a second primitive clears the gate.

---

### Q6 — Authorization audit for forbidden claim categories

Confirmed against the evidence:

| Claim category | Status |
|---|---|
| V4 release claim | Not authorized. `release_claim_authorized: false` in JSON. |
| Broad V4 speedup wording | Not authorized. `performance_gate.v4_tier2_thesis_locally_validated: false`. |
| Near hand-written OptiX wording | Not authorized. `near_handwritten_optix_claim_authorized: false` in JSON and hardcoded in harness. Route D not run. |
| Tier-3 PTX/callback claim | Not authorized. No Tier-3 experiment exists. Architecture doc (§6) explicitly requires a separate falsifiable spike, gated after Tier-2. |
| App-specific native engine claim | Not authorized. The `boundary` field on every route result explicitly forbids it: "not an outlier-specific native engine ABI." |
| Broad V3-over-V2 wording | Not authorized. Protocol (Claim Boundary section) explicitly forbids it. |
| Automatic partner choice claim | Not authorized. `automatic_partner_selection_authorized: false` in device-density metadata. |
| True zero-copy claim | Not authorized. `true_zero_copy_claim_authorized: false` in device-density metadata. |

Nothing in this packet authorizes any of these claims. The packet's own language correctly precludes them at every boundary annotation.

---

### Verdict summary

**`accept_strict_fail_revise_architecture`**

The oracle-boundary fix is valid and the measurement is credible enough to read the gate outcome as fail. The strict gate correctly fails: the summary route does not achieve 1.5x on two serious sizes. The scalar fused primitive is a real, narrow, evidenced result (2.1x–2.4x) that can be preserved under strict claim wording. The broad Tier-2 performance-release path must stop. Before any further primitive is added, the summary route underperformance must be diagnosed, Route D must be run for the scalar primitive, and the app-catalog coverage claim must be audited. No V4 release, no broad speedup wording, no near-OptiX wording, no Tier-3 claim, and no app-specific engine claim is authorized by this packet.
