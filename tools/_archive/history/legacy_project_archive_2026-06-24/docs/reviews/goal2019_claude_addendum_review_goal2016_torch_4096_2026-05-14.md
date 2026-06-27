# Goal2019 Claude Addendum Review: Goal2016 Torch Exact Filter — Count-4096 Pod Evidence

Date: 2026-05-14

Reviewer: Claude (claude-sonnet-4-6)

Prior review: `docs/reviews/goal2017_claude_review_goal2016_torch_exact_filter_2026-05-14.md`
(verdict: `accept-with-boundary`)

Verdict: **accept-with-boundary**

---

## Scope

This is a narrow addendum to Goal2017. The only change since that review is the
addition of the count-4096 pod artifact
`docs/reports/goal2016_pod_smoke/road_hazard_prepared_torch_exact_filter_4096.json`
and corresponding table rows in the Goal2016 report. The implementation in
`src/rtdsl/partner_adapters.py` is unchanged relative to Goal2017.

---

## Artifact Verification

### Count-4096 artifact (`road_hazard_prepared_torch_exact_filter_4096.json`)

- `status: "pass"`, `parity.strict_priority_flags_match: true` — strict parity holds.
- All expected metadata keys confirmed present in both unprepared and prepared
  `partners.torch` sections:
  - `app_exact_filter: torch_vectorized_segment_triangle_filter_from_generic_witness_candidates`
  - `app_exact_filter_device_materialization: true`
  - `app_count_materialization: partner_gpu_unique_pair_counts_from_prepared_torch_exact_filter`
  - `whole_app_true_zero_copy_authorized: true`
- Claim boundary flags all intact: `v2_0_release_authorized: false`,
  `broad_rt_core_speedup_claim_authorized: false`,
  `package_install_claim_authorized: false`.
- Timing confirmed against artifact:
  - Prepared Torch median: `0.004532679915428162s` (report: `0.004532680s` ✓)
  - v1.8 prepared baseline median: `0.007986754179000854s` (report: `0.007986754s` ✓)
  - Ratio `0.5675246556787354` → report `0.568x` ✓
  - Reciprocal `1/0.5675 ≈ 1.762x` → report "about `1.76x` faster" ✓
- GPU and source label match the 2048 artifact: `NVIDIA RTX A5000, 570.211.01`,
  `5e89ceaf-plus-goal2016-torch-exact-filter`.

One note: the 4096 artifact uses 3 iterations rather than the 5 used at 2048.
This is a thinner sample. The first sample in both the unprepared Torch row
(`0.2483s`) and the v1.8 unprepared baseline (`90.5s`) show GPU warmup spikes
consistent with first-run initialization; the median of 3 is taken from the
remaining samples after that spike. This is the same warmup pattern as 2048.
The thin sample is not a blocker but should be understood as a limitation of
the single-run evidence.

### Count-2048 artifact consistency check

Numbers in the report for the 2048 row are unchanged from Goal2017 and remain
correct against the artifact file. No regression introduced.

---

## Report Narrative Check

### 1. Distinguishes 2048 negative from 4096 positive evidence

The report table and prose correctly frame the two counts as opposite-sign
evidence of scale sensitivity:

- Count 2048: prepared Torch is `1.880x slower` than v1.8 prepared native —
  negative performance evidence, closeness-of-parity framing.
- Count 4096: prepared Torch is `0.568x` (about `1.76x` faster) — positive
  performance evidence, explicitly qualified as scale-sensitive.

The report does not merge or elide these two results; the table presents them
as separate rows with separate baselines, and the prose labels the crossover
explicitly. This is correct.

### 2. Avoids broad claims

The report boundary section explicitly states: "it is not a v2.0 release claim
and not a broad speedup claim." The artifact claim boundary flags corroborate
this. No release, package-install, or broad RT-core speedup claim appears
anywhere in the updated report text. This check passes.

### 3. Goal2017 implementation risks still apply; no new blockers

The implementation in `partner_adapters.py` is unchanged. All risks identified
in Goal2017 carry forward:

- Torch vectorized tensor expressions vs CuPy RawKernel: precision and launch
  behavior may differ even when parity passes on the collected artifacts. The
  4096 artifact does not change this risk profile — it exercises the same code
  path with a larger candidate set.
- Invalid candidate clamping and masking: `safe_ray_indices` and
  `safe_triangle_indices` are clamped (lines 2396–2397), then the `valid` mask
  (line 2395) is ANDed into `exact_mask` (line 2446), ensuring clamped-but-invalid
  positions are filtered out. This pattern is identical to what Goal2017 reviewed.
- The artifact `goal` field still reads `Goal1869`; provenance depends on path
  and source label as noted in the report boundary. This is a pre-existing
  known limitation.

No new implementation risk is introduced by citing the 4096 artifact. The
larger count produces a larger candidate tensor, but the filter logic path is
identical.

---

## Summary

The updated Goal2016 report correctly adds count-4096 as positive
scale-sensitive evidence alongside the count-2048 boundary case. Numbers
cross-check against the artifact JSON. Claim boundaries remain intact. No new
blockers. The thin 3-iteration sample at 4096 is a minor limitation consistent
with the existing boundary framing.

Verdict: **accept-with-boundary** (same boundary as Goal2017; 3-iteration 4096
sample noted as a minor limitation).
