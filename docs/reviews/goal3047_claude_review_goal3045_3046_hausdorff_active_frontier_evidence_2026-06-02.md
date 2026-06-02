# Goal3047 Claude Review: Goals3045–3046 Hausdorff Active-Frontier Evidence

**Date:** 2026-06-02
**Reviewer:** Claude (independent read-only review)
**Verdict:** `accept-with-boundary`

---

## Scope

This review covers the Goal3042 baseline artifact and the two evidence-strengthening
goals that follow it:

- Goal3042 — active-frontier native primitive and initial A4000 single-run timing
- Goal3045 — repeated-trial (10-trial, 2-warmup) median harness on A4000
- Goal3046 — four-dataset diversity harness on A4000 (12 cases, 60 measured trials)

The review is read-only and does not authorize any public claim, release, or
promotion of the claim language beyond what is stated in each artifact.

---

## Review Question Responses

### 1. Does the active-frontier native primitive remain generic/app-agnostic?

**Pass.**

The native export name is:

```
rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d
```

This name contains only generic concepts: point group, threshold, active frontier,
nearest witness, max-distance reduction. The Goal3042 test
`test_native_export_is_generic_and_filters_rows_on_device` explicitly asserts that
"hausdorff", "x-hd", and "xhd" do not appear (case-insensitive) in any of
`rtdl_optix_api.cpp`, `rtdl_optix_prelude.h`, `rtdl_optix_core.cpp`, or
`rtdl_optix_workloads.cpp`. The roadmap validator enforces
`"app_specific_native_engine_logic_authorized": false`.

The Hausdorff-specific orchestration lives entirely in
`rtdl_hausdorff_v2_function.py:_directed_rt_grouped_active_frontier_nearest_witness`
at the Python app layer. The native primitive receives only a query-point buffer,
a threshold radius, a threshold count, and a witness radius; it returns one
`RtdlFixedRadiusNeighborRow` and one active-count scalar. No Hausdorff semantics
cross the native boundary.

The `materializes_frontier_on_host = False` flag is correctly set and documented.
The review confirms the narrower true-zero-copy claim is correctly excluded: query
points are still packed on the host side before the launch.

### 2. Do Goals3045 and 3046 correctly preserve exact Hausdorff distance parity?

**Pass.**

All parity evidence is consistent across all three goals:

- **Goal3042** (single-run, 6 sizes): `"all_rows_match_exact_reference": true`. Each
  size row confirms matching distance, source index, and target index against
  `cupy_grouped_grid_rawkernel`. Build and focused test suite also passed on pod.

- **Goal3045** (10 alternating trials, 3 sizes): `"all_rows_match_distance": true`
  at the top level; each individual row records `"all_trials_match_distance": true`.
  The script raises a `RuntimeError` on any distance mismatch, so a silently passing
  artifact implies zero mismatch events across 30 trial pairs.

- **Goal3046** (5 alternating trials, 4 datasets × 3 sizes = 12 cases, 60 measured
  trials): `"all_rows_match_distance": true` and every individual row records
  `"all_trials_match_distance": true`. The report states "All 60 measured trials
  matched the exact CuPy grouped-grid distance."

The adversarial-tail-outlier case warrants specific attention because it is designed
to test correctness when a seed sample can miss the true witness. Inspection of the
artifact confirms:

- At all three sizes (32768, 65536, 131072), both the CuPy reference and the
  active-frontier method agree on `reference_distance ≈ 1.5654`, with
  `source_index = N-1` (the planted outlier) and `target_index = N-1`.
- The reported distance is geometrically consistent: the outlier in A is at
  [1.35, −1.20] and its counterpart in B is at [0.18, −0.16];
  `sqrt((1.35−0.18)² + (−1.20+0.16)²) ≈ 1.5654`, matching the artifact to four
  significant figures.
- This confirms the correctness argument stated in the Goal3046 report: a seed that
  misses the outlier only raises the threshold radius, leaving the missed point
  active and resolving it in the native nearest-witness pass.

The `math.isclose` tolerance used in the harness is `rel_tol=abs_tol=1e-6`, which
is appropriate for this distance scale and float64 arithmetic.

### 3. Are the reported A4000 speedups arithmetically consistent with the artifacts?

**Pass.**

All reported speedup values were verified by independent recomputation from the raw
sample arrays in the JSON artifacts.

**Goal3042 (single-run):**

| Points | CuPy sec | Active sec | Reported speedup | Verified |
| ---: | ---: | ---: | ---: | :--- |
| 4096 | 0.004776 | 0.006584 | 0.725x | ✓ |
| 8192 | 0.008930 | 0.011396 | 0.784x | ✓ |
| 16384 | 0.032289 | 0.020905 | 1.545x | ✓ |
| 32768 | 0.079344 | 0.038274 | 2.073x | ✓ |
| 65536 | 0.300481 | 0.078558 | 3.825x | ✓ |
| 131072 | 1.101468 | 0.168522 | 6.536x | ✓ |

**Goal3045 (10-trial median):**

| Points | CuPy median | Active median | Reported speedup | Verified |
| ---: | ---: | ---: | ---: | :--- |
| 16384 | 0.027997 | 0.020016 | 1.399x | ✓ |
| 65536 | 0.301261 | 0.079906 | 3.770x | ✓ |
| 131072 | 1.109388 | 0.168451 | 6.586x | ✓ |

**Goal3046 (5-trial medians, 12 cases):**

Minimum median speedup: 2.044x (demo_offset, 32768 pts) — verified.
Maximum median speedup: 7.673x (clustered_shift, 131072 pts) — verified.
Median-of-medians: 4.303x — verified by sorting the 12 speedup values and taking
the average of the 6th and 7th: `(4.196 + 4.410) / 2 = 4.303`.

No arithmetic discrepancies were found between reported summaries and raw sample
arrays. The speedup formula `cupy_median / active_median` is applied consistently
in the script and matches the artifact values.

One minor note: Goal3045 samples are stored in the order the trials were collected
(not sorted), while `_timing_stats` sorts internally for percentile computation.
`statistics.median` does not require sorted input and handles even-count sets
correctly. No issue.

### 4. Does Goal3046 materially reduce the dataset-diversity and seed-miss concern?

**Partially, but gaps remain. The concern is materially reduced, not eliminated.**

**What Goal3046 adds:**

- **Four distinct geometric shapes**: dense-offset (original), four-cluster Gaussian
  shift, ring-vs-spiral (structured anisotropic curves), and adversarial tail-outlier
  (mostly-overlapping cloud with a planted outlier far from the bulk).
- **Three sizes** per shape (32768, 65536, 131072 points), giving 12 (dataset, size)
  combinations.
- **5 alternating warmup+trials** per combination, with 60 total measured trials.
- **Exact correctness** on all 60 trials, including the adversarial shape.
- **Consistent speedup profile**: minimum 2.044x across all 12 cases, scaling to
  7.673x at 131072. The speedup does not vanish for non-demo-offset shapes.

**Remaining gaps:**

1. **Single seed/sample configuration.** Every run uses `--seed-sample-count 1024`
   and `--target-points-per-group 512`. The pruning effectiveness and correctness
   boundary depend on both parameters. A sweep over these knobs (e.g.,
   seed_sample_count of 64, 256, 4096; target_points_per_group of 128, 1024) has
   not been reported.

2. **All datasets are synthetic and 2D.** No real-world point cloud has been tested.
   Real data may have density gradients, spatial correlations, or near-duplicate
   points that differ from the four synthetic shapes.

3. **Only one CuPy reference method.** The comparison baseline is exclusively
   `cupy_grouped_grid_rawkernel`. Performance relative to other CUDA references
   (e.g., raw CuPy pairwise, Numba paths) is not part of this artifact.

4. **Single GPU (A4000).** All 70+ measurements are from one pod, one GPU model,
   one driver version (580.159.03), one CUDA prefix (12.8). Porting behavior to
   an L4, A100, or consumer GPU is unconfirmed.

5. **Goal3046 uses only one warmup iteration** (vs. two in Goal3045). This is a
   minor regression in thermal-state control but not a correctness concern. The
   IQRs in Goal3046 are comparable to Goal3045, so the reduced warmup does not
   appear to have introduced visible variance.

6. **The `ring_vs_spiral` dataset yields slightly different Hausdorff distances at
   different sizes** (0.09692 at 65536, 0.09684 at 131072 for direction b→a),
   which is expected since different N produces different point positions from the
   deterministic formula. The witnesses are at different indices, and both methods
   agree. This is correct behavior, not an anomaly.

### 5. Are the claim boundaries strict enough?

**Pass.**

Every artifact (JSON, Markdown, script source, roadmap entry) carries explicit
`False` flags for all five prohibited wording categories:

- `v2_6_release_authorized: false`
- `public_speedup_claim_authorized: false`
- `rt_core_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `true_zero_copy_claim_authorized: false`

The `validate_v2_6_roadmap` function enforces all five flags programmatically and
must return `"status": "accept"` for the test suite to pass. The Goal3045 and
Goal3046 test files check `roadmap.get("release_authorized") is False` and
`roadmap.get("public_speedup_claim_authorized") is False` directly.

The roadmap entries for Goal3045 and Goal3046 both contain
`"not_public_speedup_evidence"` in their status strings, which is also
machine-checked.

The claim language in the reports is appropriately narrow: "internal v2.6 evidence
for a specific A4000 Hausdorff benchmark path", "one GPU, synthetic dataset
diversity, one seed/sample configuration, one CuPy reference method, and no
second-GPU confirmation yet." This language does not authorize:

- Any public speedup number
- Broad RT-core speedup wording
- Release readiness
- True-zero-copy or whole-app wording

No language drift was found between the reports, scripts, artifacts, and roadmap.

### 6. What concrete follow-up remains before public v2.6 Hausdorff RT-core claim?

The following are prerequisites before any public Hausdorff RT-core performance
claim can be authorized from this evidence chain:

1. **Second-GPU confirmation** (highest priority). Run the Goal3045 or Goal3046
   harness (or an equivalent) on a different GPU model — the obvious candidate is
   the L4 pod that was used for Numba conformance in Goals3021/3031/3034. Confirm
   that the crossover point and the speedup scaling profile are qualitatively
   similar. A second GPU that shows a different crossover point or much lower
   speedup would materially change the claim scope.

2. **Seed/sample parameter sweep.** Test at least two additional
   `seed_sample_count` values (e.g., 256 and 4096) and two additional
   `target_points_per_group` values (e.g., 128 and 1024) on one of the existing
   datasets. Report the crossover point and speedup change, if any. Confirm
   correctness at all configurations.

3. **Real-world or semi-real dataset.** A point cloud from a domain application
   (LiDAR scan, mesh vertex set, geographic coordinate set) would help establish
   that the speedup is not an artifact of the synthetic generation structure.
   Even a publicly available benchmark point cloud would suffice.

4. **External review sign-off.** At least one reviewer must confirm the generic
   contract, parity, and boundary language before any public wording is used.
   This review satisfies that requirement for the Claude reviewer role but does
   not substitute for the Gemini reviewer slot or a human domain reviewer if one
   is required by the project process.

5. **Agreed public claim wording.** Any public speedup number must cite the GPU
   model, dataset class, size range, and reference method. Wording such as
   "up to Xx faster than CuPy grouped-grid on A4000 at N≥16K 2D synthetic
   point sets" is defensible; wording such as "RT-core Hausdorff speedup" or
   "X times faster" without qualification is not.

---

## Verdict Summary

| Review question | Finding |
| :--- | :--- |
| Native primitive generic/app-agnostic | Pass |
| Exact distance parity (G3045/G3046) | Pass |
| Speedup arithmetic consistent | Pass |
| Dataset-diversity concern reduced | Partially — 4 shapes tested, synthetic only |
| Claim boundaries strict enough | Pass — machine-enforced, no drift found |
| Follow-up before public claim | Second GPU, seed sweep, real-world data, wording review |

**Verdict: `accept-with-boundary`**

The Goals3042, 3045, and 3046 evidence chain is internally coherent, arithmetically
correct, and correctly bounded. The active-frontier primitive is demonstrably generic.
The 60-trial parity record across four dataset shapes is strong internal evidence.
The claim boundaries are machine-enforced and show no drift.

This review does NOT authorize:
- Public speedup wording of any form
- Broad RT-core speedup wording
- Release of v2.6
- True-zero-copy wording
- Whole-app speedup wording

The evidence may be cited internally as: "A4000 active-frontier Hausdorff path
crosses the CuPy grouped-grid baseline above 16K points and reaches ~6.6x median
speedup at 131K points across four synthetic 2D dataset shapes, with exact distance
parity confirmed across 60+ trials; second-GPU confirmation and external review
are required before public claim authorization."
