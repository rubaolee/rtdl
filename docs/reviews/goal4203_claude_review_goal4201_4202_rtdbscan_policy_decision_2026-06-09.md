# Goal4203: Claude Review — Goal4201/4202 RT-DBSCAN Boundary Policy Decision

Date: 2026-06-09
Reviewer: Claude Sonnet 4.6 (independent read-only review)
Verdict: **accept-with-boundary**

---

## Scope

This review covers Goals4201 and 4202 as a chain. Goal4201 measures whether
`lowest_component_root_two_pass` is fast enough to promote as the default route.
Goal4202 tests whether the existing default `lowest_candidate_then_root` route
already satisfies the Goal4194 deterministic reference contract. Both goals feed
into the decision to keep two-pass as an explicit reference/debug policy while
continuing to use one-pass as the performance route.

---

## Q1 — Timing Methodology (Goal4201)

**Finding: fair, sufficient for the stated conclusion, minor metadata gap noted.**

The methodology is sound:

- Both policies use the same pre-built `PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D`
  handles throughout measurement. This isolates execution cost from prepare cost —
  the right comparison for an already-prepared-scene performance question.
- `cuda.synchronize()` brackets each timed iteration before the wall-clock start
  and after the wall-clock stop.
- Two warmup iterations run before the five measured repetitions; alternating
  measurement order (even index: default first, odd index: two-pass first) guards
  against monotonic thermal drift.
- `same_counts_only_signature: true` confirms both policies produce the same
  component structure in every case, so the timer is comparing equivalent work.

The alternating-order design does not protect against non-monotonic GPU scheduling
effects, and five repetitions give limited statistical power. However, the gap in
clustered and road cases (1.5x–1.9x) is large enough to survive measurement noise.
The conclusion ("two-pass is correctness/reference machinery, not a default
performance route") is well-supported.

**Metadata gap — ngsim_dense case:** Both policies record
`native_boundary_assignment_policy: null` and
`native_boundary_assignment_pass_count: null` for the 65k dense-grid fixture.
The JSON data and source confirm this occurs because all 65 536 points are
predicate-true (`flag_true_count == point_count`, `negative_label_count: 0`),
causing both policies to take the all-predicate-true fast path. In that path the
native metadata does not propagate those keys back to the Python layer. This is a
metadata presentation gap, not a correctness concern; the timing ratio ≈1.003
correctly reflects that neither policy performs boundary work in this degenerate
case. The gap should be documented in the metadata schema or filled by the native
path for completeness.

---

## Q2 — Reference Comparison Validity (Goal4202)

**Finding: valid for the tested fixtures, with acknowledged scale limitations.**

The comparison chain is correct:

1. **CPU candidate pairs** — `_candidate_pairs` computes all pairs within `radius`
   using an O(n²) brute-force loop with squared-distance comparison. Correct for
   the small scales used.

2. **Predicate flags** — drawn from the default one-pass run's `is_core` output.
   Core classification depends on `neighbor_counts` relative to `min_neighbors`,
   which is independent of the boundary assignment policy. Using the default
   run's flags for both the reference and the two-pass comparison is correct.

3. **Reference labels** — produced by `predicate_aware_boundary_union_reference`
   (Goal4194 contract, `predicate_aware_boundary_union.py`). The implementation
   uses union-find with path compression and lowest-root boundary assignment.
   The contract is clearly versioned (`rtdl.predicate_aware_boundary_union.reference.v1`)
   and the status field marks it `reference_contract_candidate_not_promoted`. The
   reference semantics are correct.

4. **Label comparison** — zero-based labels from both native policies are compared
   exactly to reference labels. Mismatch count is 0 for every fixture.

5. **Pass-count verification** — Goal4202 evidence test confirms
   `native_boundary_assignment_pass_count == 1` for default and `== 2` for
   two-pass across all four fixtures.

**Scale limitation:** The largest fixture is 1 024 points (road3d_1024), far
below the 65 536 used in Goal4201. The report acknowledges this. CPU O(n²) limits
the reference comparisons to small scales; larger-scale parity requires a
different strategy (component-size signature comparison or incremental reference).

**Degenerate fixture (ngsim_dense_1024):** `predicate_true_count: 0` — no points
are core. All labels are -1 (noise). Both policies trivially agree because no
boundary assignment work is performed. This fixture does not stress-test the
boundary logic; it is a valid degenerate case but should not be counted as
meaningful boundary coverage. The same degenerate observation applies to the
Goal4201 ngsim_dense_64k fixture (all predicate-true, no boundary candidates).

---

## Q3 — Decision Support

**Finding: the evidence supports the stated decision.**

Goal4201 shows two-pass is 1.46x–1.89x slower in cases that exercise boundary
logic. Goal4202 shows the one-pass route already matches the reference contract
for the tested fixtures. Together, these two facts form a coherent basis for:

- retaining two-pass as an explicit policy for reference/debug use;
- continuing one-pass as the performance route;
- deferring promotion until a broader parity gate is cleared.

The decision memo correctly identifies the next technical target: collecting
candidate roots during the primary traversal, then rebasing through the final
parent array on device, without a second RT traversal. This is described as a
runtime/primitive improvement rather than an application-specific trick — the
framing is accurate given the `predicate_aware_boundary_union` abstraction.

---

## Q4 — Claim-Boundary Audit

**Finding: no leaks detected.**

All boundary fields (`release_authorized`, `route_promotion_authorized`,
`public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`,
`whole_app_speedup_claim_authorized`) are `false` in both artifact payloads and
in both Python scripts' output structures. The scripts hard-code `False` in the
return values and at the top-level payload, providing two independent false
assertions per claim per run.

**RT-core acceleration:** `rt_core_accelerated: true` appears in the Goal4202
case metadata. This is a factual hardware observation recorded in metadata, not
a promoted claim. The claim boundary does not authorize broad RT-core acceleration
claims. No leak.

**Speedup language in reports:** The Goal4201 report states "the second RT
traversal is the cost center" and presents ratios. These are directional
observations internal to the timing study, not public speedup claims. No leak.

**Hidden dispatch:** Both policies resolve to the same native symbol
(`rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs`)
in both artifacts. The policy distinction is implemented purely at the Python
layer dispatch (one vs. two calls to `apply_device_grouped_union_self`). No
evidence of hidden dispatch to a different symbol or codepath that would
invalidate the comparison.

**App-specific native engine logic:** The Goal4201 report explicitly states the
next target is "not an RT-DBSCAN app-specific trick." The
`predicate_aware_boundary_union_reference` contract has
`native_engine_app_specific_logic: False` in its policy metadata. No leak.

**Cross-commit concern:** Goal4201 evidence is from commit `0cfdad4a`, Goal4202
from `801acd3b`. These are different commits in the same forward chain (per git
log order). The evidence tests hard-code these commit hashes as assertions, making
the chain traceable. No leak, but downstream consumers should note that parity
evidence at commit `801acd3b` does not automatically extend to later commits.

---

## Q5 — Evidence Still Required for One-Pass Promotion

The following evidence is required before `lowest_candidate_then_root` can be
renamed or promoted as a policy-bound deterministic route:

1. **Adversarial boundary fixtures** — sparse-noise-heavy point sets where a
   significant fraction of points are border nodes with multiple competing
   component roots. The current fixtures are predominantly high-density core
   clusters. The key invariant to stress-test is: "the component root observed
   during a single traversal equals the final parent-array root after union
   convergence." This invariant can fail with deep merge chains or race-prone
   late-merging clusters.

2. **Fragmented and overlapping cluster fixtures** — clusters that partially
   overlap or fragment under the given radius/threshold combination, where many
   points have both core and border neighbors across component boundaries.

3. **Randomized seeds, multiple runs** — the current parity run uses a single
   fixed seed (20260519) for each fixture. A non-determinism audit (multiple runs
   of the same fixture) and a seed sweep are required to rule out lucky alignment
   between union order and traversal order.

4. **Larger-scale parity with component-size signature comparison** — since CPU
   O(n²) reference is impractical above ~2k points, the promotion gate should
   define an alternative: compare component-size signatures or label-count
   histograms across policies at the scales used in Goal4201 (16k–64k). This
   requires a specific criterion (e.g., exact histogram match across N fixtures
   and M seeds at the target scale).

5. **Explicit promotion criteria document** — a written specification of what
   "broader same-contract parity" means quantitatively (fixture count, dataset
   diversity, seed count, pass/fail threshold) should be ratified before running
   the promotion gate, not after.

6. **Native metadata completeness fix for the all-predicate-true path** — the null
   `native_boundary_assignment_policy` and `native_boundary_assignment_pass_count`
   fields in the ngsim_dense case should be resolved before any promoted contract
   relies on those metadata fields for policy audit.

---

## Summary

| Question | Assessment |
| --- | --- |
| Q1: Timing methodology fair? | Yes — adequate for the stated conclusion; ngsim_dense null metadata is a minor gap |
| Q2: Reference comparison valid? | Yes — CPU pairs, native flags, Goal4194 reference, and exact label comparison are all correct; scale is small but acknowledged |
| Q3: Decision supported by evidence? | Yes — two-pass is slower and produces equivalent results; deferring promotion is correct |
| Q4: Claim-boundary leaks? | None detected — all boundary fields are false; rt_core metadata is factual, not a claim |
| Q5: Remaining evidence for promotion? | Adversarial fixtures, fragmented clusters, seed sweep, larger-scale signature parity, written promotion criteria, metadata null fix |

**Verdict: accept-with-boundary**

The Goal4201/4202 chain correctly concludes that two-pass is reference/debug
machinery and one-pass is the performance route. The boundary fields are
consistently false. No premature promotion claims are made. Outstanding work
before promotion is clearly identified. The main residual risk is that the parity
evidence covers only 3 non-degenerate fixture types at small scale; the chain
correctly names this as the next gate rather than asserting broader coverage.
