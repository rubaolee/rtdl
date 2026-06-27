# Goal4168 Claude Review: Goals 4165–4167 RT-DBSCAN Mixed Policy Status

**Date:** 2026-06-09
**Reviewer:** Claude Sonnet 4.6
**Verdict:** `accept-with-boundary`
**Scope:** Read-only review of reports, JSON artifacts, test files, and benchmark app source. No source files edited, no tests run.

---

## Summary

Goals 4165–4167 close the investigation that Goal4159 opened. Goal4159 established that the `road_sparse_many_noise` mixed-predicate row had a genuine border-assignment policy gap that no simple canonical comparison could dismiss. Goal4165 confirms that switching grouped-stream configuration knobs does not explain that gap: each variant fails for at least one seed. Goal4166 adds the correct response — a pure app-layer semantic helper that separates the two possible contracts. Goal4167 updates the advisor to report both contracts and the performance status honestly. No route is promoted, no claim boundary is violated, and no native code was changed.

---

## Question 1: Does Goal4165 correctly show that no single grouped-stream variant universally explains the mixed-predicate direct-status component-size differences?

**Yes.**

The JSON artifact (`goal4165_mixed_policy_variant_probe_pod.json`) contains 12 rows: four shapes × three seeds. Manually verifying the `candidate_canonical_matches` field across all rows confirms the report's summary table:

| Variant | Canonical matches | Canonical mismatches (seed) |
| --- | ---: | --- |
| `grouped_stream_numba_same_root_true` | 11/12 | `road_sparse_many_noise` seed 123 |
| `grouped_stream_numba_same_root_false` | 11/12 | `road_sparse_many_noise` seed 123 |
| `grouped_stream_numba_direct_side_effect` | 11/12 | `road_sparse_many_noise` seed 17 |

No single variant achieves 12/12. Each variant fails for a different seed. This is the key observation: the predicate direct-status route does not consistently agree with any one grouped-stream configuration. The exact-match counts (7/12 per variant) are also accurate — the remaining 5 misses per variant are label-ID permutations where canonical multisets agree, as expected for label-arbitrary component numbering.

The test `test_only_road_sparse_seed_variants_show_canonical_mismatch` correctly encodes the two specific mismatches. The test `test_artifact_records_no_single_grouped_variant_as_universal_reference` verifies the 7/11 exact/canonical counts per variant. Both tests are tightly tied to the actual JSON data.

**One specific data observation**: For `road_sparse_many_noise` seed 17, the `grouped_stream_numba_direct_side_effect` canonical differs from the predicate direct-status canonical. The sizes differ as `[…, 16, 16, …, 21767, 21979]` (grouped-direct) vs `[…, 16, …, 21783, 21979]` (predicate). The delta is exactly 16 — one size-16 component merged into the large cluster under the predicate route's border policy. This is a genuine border-assignment difference, not a rounding artifact.

---

## Question 2: Is the interpretation sound that mixed-predicate DBSCAN-like outputs require an explicit border-assignment policy, and that component-size distribution is not always a stable semantic contract?

**Yes.**

The artifact data confirms the mechanism: for `road_sparse_many_noise`, `core_count` and `noise_count` are identical across all variants at each seed. Only component sizes differ. This is exactly the case where a border point that touches two or more predicate-true components is legally assignable to either, and different policies produce different size distributions without changing the count of cores or noise.

The report's phrasing — "predicate-false items that touch more than one predicate-true component need an explicit border assignment policy" — is precise. This is a general graph-theoretic property of border-assignment in connected-components computation, not a bug. The metadata in the predicate direct-status rows confirms the current policy: `border_assignment_policy: "lowest_predicate_true_point_id_within_radius"` and `border_candidate_updates: ~25,000–26,000`.

The corollary — that a raw component-size signature is too strict as a sole correctness gate — follows directly and is stated clearly. The two-contract design in Goal4166 is the correct response to this finding.

**One clarification the report does not make explicit** (worth noting for readers): the cases where canonical mismatches appear (`road_sparse_many_noise`) involve large two-cluster configurations where one cluster has ~21,000–22,000 points. The size difference per border point is small in percentage terms but changes the canonical multiset definitively. The cases without canonical mismatches (`road_mid_sparse_mixed_clusters`, `clustered_half_radius_high_threshold`, `ngsim_sparse_many_noise`) either have more homogeneous border neighborhoods or a smaller number of active border candidates. The probe design correctly includes both types, making the diagnostic complete.

---

## Question 3: Does Goal4166 keep this policy-aware semantic signature in the app/reference layer rather than adding app-specific native engine logic?

**Yes, definitively.**

The `policy_aware_rt_dbscan_semantic_signature(...)` and `same_policy_aware_rt_dbscan_semantic_signature(...)` functions are in `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`, lines 1186–1246. Both are pure Python functions operating on a `signature` dict (a plain Python dict from the app layer). They call the pre-existing `canonical_component_size_signature(...)` helper (also in the same file) and return a plain dict. No native engine file was touched.

The report states "Native engine remains unchanged." The test `test_report_records_scope` checks that this phrase appears in the report. The report also states "It does not change native code, add a DBSCAN ABI, authorize release, or authorize public speedup wording."

The implementation correctly fails closed on invalid contract names:
```python
if component_size_contract not in {
    "policy_bound_component_sizes",
    "core_noise_assigned_counts_only",
}:
    raise ValueError(...)
```
The test `test_invalid_contract_fails_closed` verifies this.

**Design note worth recording**: The `border_assignment_policy` parameter is a string label in the output dict — it does not change which computation the helper performs. The `component_size_contract` parameter is what actually controls the output shape. This means the helper is an attestation/labeling mechanism (the caller declares which contract they intend to use) rather than a dispatch mechanism. This is the correct design: the helper does not impose a policy on the data; it records the caller's stated policy for comparison purposes. The test `test_helper_fields_are_stable_and_explanatory` confirms the field contents are stable.

---

## Question 4: Does Goal4167 update the advisor honestly — policy-aware counts-only semantics can pass, but mixed predicate direct-status is still not broadly faster and is not promoted?

**Yes.**

Reading `explain_rt_dbscan_explicit_route_choice(...)` in the benchmark app (lines 327–369):

- `"policy_aware_semantic_signature_helper": "policy_aware_rt_dbscan_semantic_signature"` ✓
- `"mixed_predicate_comparison_contracts": ("policy_bound_component_sizes", "core_noise_assigned_counts_only")` ✓
- `"mixed_predicate_policy_probe": "Goal4165"` ✓
- `"mixed_predicate_policy_aware_contract": "Goal4166"` ✓
- `"mixed_predicate_performance_status"`: explicitly says the predicate route "is not promoted for mixed rows because Goal4165 does not show broad performance advantage" ✓
- `"mixed_predicate_route_promotion_blocked_by": ("Goal4159", "Goal4160")` — correctly carries forward the prior blocking evidence ✓
- `"automatic_dispatch_authorized": False`, `"public_speedup_claim_authorized": False`, `"release_authorized": False` ✓

The direct-status option entry in `options` (lines 251–292) explicitly says: "they are not broadly faster in Goal4165" as part of `predicate_scope`, and `"mixed_predicate_performance_status": "Goal4165 shows the candidate is not broadly faster on sparse mixed rows"`.

**Performance verification from the Goal4165 artifact**:

| Case | Grouped elapsed (approx.) | Predicate elapsed (approx.) | Direction |
| --- | ---: | ---: | --- |
| `road_sparse_many_noise` (3 seeds) | 6–7ms | 19–20ms | predicate ~3× slower |
| `road_mid_sparse_mixed_clusters` (3 seeds) | 7–8ms | 23ms | predicate ~3× slower |
| `ngsim_sparse_many_noise` (3 seeds) | 7–8ms | 26ms | predicate ~3× slower |
| `clustered_half_radius_high_threshold` (3 seeds) | 52–63ms | 41–42ms | predicate ~1.3–1.5× faster |

The clustered-high-threshold case is the one shape where predicate is faster. This shape has only 76–78 noise points out of 65,536 — it is nearly all-predicate-true, which is why the predicate fast path nearly fires. Goal4164 already handles this regime via the explicit `all_true` mode that fails closed on mixed rows. The `clustered_half_radius_high_threshold` result here is consistent with that finding and does not establish a broad mixed-predicate performance advantage.

The advisor's "not broadly faster" wording is accurate and appropriately conservative.

---

## Question 5: Do the reports avoid release, public speedup, whole-app, and route-promotion overclaims?

**Yes, throughout.**

The JSON artifact carries:
```json
"claim_boundary": {
    "public_speedup_claim_authorized": false,
    "release_authorized": false,
    "route_promotion_authorized": false,
    "whole_app_claim_authorized": false
}
```

The three reports contain explicit denial sentences:

- **Goal4165**: "This diagnostic does not promote predicate direct-status for mixed predicate rows. It does not authorize release, public speedup wording, whole-app claims, or route-promotion wording."
- **Goal4166**: "This does not promote predicate direct-status for mixed predicate rows. It does not change native code, add a DBSCAN ABI, authorize release, or authorize public speedup wording."
- **Goal4167**: "No hidden dispatch or public speedup claim is authorized." and "Goal4167 does not promote mixed predicate direct-status."

The advisor function in the benchmark app preserves all six False claim flags from the prior chain and adds no new True claims.

The tests enforce this at the report-text level:
- Goal4165 test: `"does not promote predicate direct-status for mixed predicate rows"` in report ✓
- Goal4166 test: `"does not promote predicate direct-status"` and `"Native engine remains unchanged"` ✓
- Goal4167 test: `"does not promote mixed predicate direct-status"` and `"No hidden dispatch or public speedup claim is authorized"` ✓

---

## Cross-Checks Between Reports and Artifacts

| Claim | Source | Verified |
| --- | --- | --- |
| 7/12 exact matches per variant | Report and test | Confirmed by JSON `candidate_matches` field across 12 rows |
| 11/12 canonical matches per variant | Report and test | Confirmed by JSON `candidate_canonical_matches` field |
| Only `road_sparse_many_noise` rows show canonical mismatch | Report and test | Confirmed: all 9 non-road-sparse rows have canonical_matches all-true |
| Seed 17: direct_side_effect canonical mismatch | Report and test | JSON row 1 shows direct_side_effect canonical = false |
| Seed 123: same_root variants canonical mismatch | Report and test | JSON row 2 shows same_root_true and same_root_false canonical = false |
| `border_assignment_policy` in predicate rows | Report | JSON metadata: `"border_assignment_policy": "lowest_predicate_true_point_id_within_radius"` ✓ |
| `direct_status_convergence_proven: true` in predicate rows | Claim integrity | JSON metadata confirms this on all 12 predicate direct-status rows ✓ |
| Artifact commit matches `d25eff1` | Report | `"commit": "d25eff118d8590068c5aa0ead9c557240ae3a06c"` ✓ |
| GPU: RTX 4000 Ada | Report | `"gpu": "NVIDIA RTX 4000 Ada Generation, 550.127.05"` ✓ |

No inconsistencies found between reports and artifacts.

---

## Continuity with Prior Reviews

This chain follows naturally from Goal4160's prior review (`accept-with-boundary`). Goal4160 recommended "an explicit generic border-assignment policy parameter" and stated that "canonical component-size signature comparison should be the formal same-contract metric going forward." Goal4165 confirms the gap is policy-driven. Goal4166 implements the two-contract comparison without reaching into the engine. Goal4167 wires it into the advisor. The chain is methodologically consistent.

The remaining open item from Goal4160's engineering recommendation — implementing a `reference_grouped_stream_compatible` policy — is still not done. The advisor correctly names it as the `target_predicate_border_assignment_policy` and keeps it distinct from the current `lowest_predicate_true_point_id_within_radius` policy. This gap is accurately preserved, not obscured.

---

## Minor Observations

1. **`border_assignment_policy` as attestation label**: The `policy_aware_rt_dbscan_semantic_signature` helper records the caller's stated policy in the output dict but does not enforce that policy during computation. A caller could pass `border_assignment_policy="x"` with `component_size_contract="core_noise_assigned_counts_only"` and the same dict would result regardless of the policy string. This is a deliberate design choice (the helper is a labeling/contract mechanism, not a dispatch mechanism) and is correct for the intended use. It is worth documenting in the helper's docstring if this is to be used outside the research benchmark context.

2. **`clustered_half_radius_high_threshold` performance**: Predicate is 1.3–1.5× faster on this shape, but this shape is effectively near-all-predicate (76–78 noise/65,536 points). Goal4164 already covers this regime via the explicit all-true mode. The advisor does not present this as a mixed-predicate win, which is correct.

3. **Three seeds per shape is a reasonable diagnostic**: The probe uses seeds 17, 123, and 20260519. For two of three seeds of `road_sparse_many_noise` a canonical mismatch appears, which is sufficient to establish that the gap is real and not a rare seed-specific artifact. The probe's scope is correctly bounded as diagnostic, not as a full promotion evidence set.

---

## Verdict

`accept-with-boundary`

Goals 4165–4167 are methodologically sound and internally consistent. Goal4165 correctly establishes that no grouped-stream configuration switch explains the mixed-predicate signature gap. Goal4166 correctly adds the policy-aware semantic helper as a pure app-layer facility without touching native code. Goal4167 correctly updates the advisor to name the new contracts and probe, while keeping all False claim flags intact and explicitly recording that mixed-predicate direct-status is not broadly faster and is not promoted. The three reports and tests are internally consistent with the JSON artifact data.

The boundary from Goal4159/4160 is preserved: mixed-predicate direct-status route promotion remains blocked by the performance evidence (`road_sparse_many_noise` is ~3× slower under predicate) and by the unresolved `reference_grouped_stream_compatible` border policy requirement. No release, public speedup, whole-app, or route-promotion claim is authorized.
