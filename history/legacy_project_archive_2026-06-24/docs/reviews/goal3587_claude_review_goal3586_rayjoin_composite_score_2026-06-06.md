# Claude Review: Goal3586 RayJoin Composite Score From Hot Promoted Routes

Date: 2026-06-06
Reviewer: Claude (Sonnet 4.6)
Verdict: **accept**

---

## Scope

This is an independent review of Goal3586 as requested by
`docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3586_RAYJOIN_COMPOSITE_SCORE_2026-06-06.md`.
All artifacts were read directly and all arithmetic was independently verified from the
JSON source data. The Goal3583 artifacts and the prior Goal3583 reviews (goal3584,
goal3585) were consulted for context.

Artifacts reviewed:

- `docs/reports/goal3586_rayjoin_composite_score_from_hot_promoted_routes_2026-06-06.md`
- `tests/goal3586_rayjoin_composite_score_from_hot_promoted_routes_test.py`
- `docs/reports/goal3583_rayjoin_hot_promoted_routes_a5000/summary.json` (ratios section)
- `docs/reports/goal3583_rayjoin_hot_promoted_routes_stress_a5000/summary.json` (ratios section)
- `docs/reviews/goal3584_claude_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md`
- `docs/reviews/goal3585_gemini_review_goal3583_rayjoin_hot_promoted_routes_2026-06-06.md`

---

## Arithmetic Verification

All six composite values were independently recomputed from the `ratios` arrays in the
two JSON artifacts before reading the report's claimed numbers.

### Standard packet

Source: `goal3583_rayjoin_hot_promoted_routes_a5000/summary.json` (git commit
`3b845c1085add4ae304123fcd78985359c61acf0`, NVIDIA RTX A5000, driver 580.126.09)

| Contract | Embree sec (JSON) | OptiX sec (JSON) | Speedup (JSON) |
|---|---:|---:|---:|
| LSI | 0.012941647320985794 | 0.00010210834443569183 | 126.74426749849505 |
| Overlay | 0.34969502314925194 | 0.00035725533962249756 | 978.837778936392 |
| PIP | 0.010831083171069622 | 0.002115868963301182 | 5.11897634443815 |

Embree total: 0.012941647320985794 + 0.34969502314925194 + 0.010831083171069622
= **0.37346775364130735** (report: 0.373467754 ✓)

OptiX total: 0.00010210834443569183 + 0.00035725533962249756 + 0.002115868963301182
= **0.002575232647359371** (report: 0.002575233 ✓)

Summed speedup: 0.37346775364130735 / 0.002575232647359371
= **145.02292x** (report: 145.023x ✓)

Geometric mean: (5.11897634443815 × 126.74426749849505 × 978.837778936392)^(1/3)
= **85.9556x** (report: 85.956x ✓)

### Stress packet

Source: `goal3583_rayjoin_hot_promoted_routes_stress_a5000/summary.json` (same commit and
environment)

| Contract | Embree sec (JSON) | OptiX sec (JSON) | Speedup (JSON) |
|---|---:|---:|---:|
| LSI | 0.019551154226064682 | 0.0001312941312789917 | 148.91110543638632 |
| Overlay | 5.392689579166472 | 0.0011661453172564507 | 4624.37185088876 |
| PIP | 0.03496394120156765 | 0.005896885879337788 | 5.92922127322804 |

Embree total: 0.019551154226064682 + 5.392689579166472 + 0.03496394120156765
= **5.447204674594104** (report: 5.447204675 ✓)

OptiX total: 0.0001312941312789917 + 0.0011661453172564507 + 0.005896885879337788
= **0.00719432532787323** (report: 0.007194325 ✓)

Summed speedup: 5.447204674594104 / 0.00719432532787323
= **757.1530x** (report: 757.153x ✓)

Geometric mean: (5.92922127322804 × 148.91110543638632 × 4624.37185088876)^(1/3)
= **159.830x** (report: 159.830x ✓)

All eight numbers match the report to the precision displayed. No transpositions, rounding
errors, or inconsistencies detected.

---

## Reviewer Question Responses

### Q1: Is summed wall-time ratio a reasonable primary single app-packet score for this fixed RayJoin-style benchmark packet?

**Yes, it is the correct choice for this packet structure.**

For a fixed sequential packet where the app runs PIP, LSI, and overlay active-count once
each, the summed wall-time ratio directly answers "what is the end-to-end speedup for this
packet?" It weights each route by its actual wall-clock contribution, which is appropriate
when the goal is a single trackable app-level number rather than a per-route narrative.

The choice amplifies overlay dominance in proportion to actual wall-time: overlay represents
93.7% of the standard Embree total (0.350 s out of 0.373 s) and 99.0% of the stress Embree
total (5.393 s out of 5.447 s). This is a feature of the metric, not a bug: if overlay is
the bottleneck in the real app packet, the primary score should reflect that. The report
acknowledges this explicitly in the Interpretation section.

One constraint to note: the summed ratio assumes the contracts execute sequentially within
the packet. If future packet designs run contracts in parallel, the metric definition would
need to change. At the current scope this constraint holds.

### Q2: Is geometric mean a reasonable secondary route-balanced score, and does it properly reduce overlay dominance?

**Yes on both counts.**

The geometric mean of the three per-contract speedups gives each route equal narrative
weight, independent of its absolute wall-clock magnitude. This is the standard technique
for multi-workload averaging where the routes span very different absolute time scales (here:
microseconds for LSI, milliseconds for PIP, hundreds of milliseconds to seconds for overlay).

The reduction of overlay dominance is large and correct:
- Standard: 978.838x overlay speedup → 85.956x geometric mean (vs 145.023x primary)
- Stress: 4624.372x overlay speedup → 159.830x geometric mean (vs 757.153x primary)

The geometric mean pulls the PIP row (5-6x) into the average on equal terms with the
overlay row (979-4624x), which is the intended behavior. The resulting geometric mean still
reflects a strong positive result because even the weakest route (PIP at ~5x) is positive,
and geometric mean of positive values is always positive.

Unlike arithmetic mean, geometric mean is dimensionless under rescaling of individual route
speedups, making it stable if individual contract times shift proportionally with fixture
size. This is a good property for the secondary score.

### Q3: Are all scores recomputed correctly from the Goal3583 artifacts?

**Yes, all eight values verified to full floating-point precision.** See the Arithmetic
Verification section above. The test's expected values in
`goal3586_rayjoin_composite_score_from_hot_promoted_routes_test.py` are consistent with
independent recomputation from the JSON source.

The test implementation is also correct:
- It reads `ratios` from the JSON and sums `embree_sec` / `optix_sec` values directly.
- It computes the geometric mean using `optix_speedup_vs_embree` from the JSON (which is
  the per-row ratio precomputed in the Goal3583 artifact) rather than recomputing from
  individual sec values. This is equivalent and correct.
- `assertAlmostEqual` without a `places` argument defaults to 7 decimal places, which is
  appropriate for 64-bit float precision.

### Q4: Are the caveats strong enough that no one reads the composite score as full RayJoin paper reproduction, paper-scale performance, full polygon overlay materialization, a true zero-copy claim, or release authorization?

**Yes, the caveats are complete and machine-enforced.**

The report's Boundaries section explicitly lists all six required exclusions:
- not a full RayJoin paper reproduction ✓
- not a paper-scale RayJoin claim ✓
- not a claim that RTDL beats the original RayJoin implementation ✓
- not a full polygon overlay materialization result ✓
- not a true zero-copy claim ✓
- not a release authorization ✓

The test (`test_report_documents_score_definitions_and_boundaries`) asserts the presence of
three key phrases in the report text: "full RayJoin paper reproduction", "full polygon
overlay materialization", and "true zero-copy claim". These are the three most likely to be
misread as positive claims, so the test selection is appropriate.

One mild gap: the test does not assert the presence of "paper-scale", "release
authorization", or "RTDL beats" text. These are present in the report but not validated by
the test suite. This is a coverage weakness rather than a correctness problem; the six
boundaries are all present in the report as-written.

The Interpretation section is also correctly worded: "The stress app-packet score is larger
because overlay active-count scales into a multi-second Embree workload while the prepared
OptiX active-count continuation stays near millisecond scale. This is a real benefit for
this active-count contract, but it is not full polygon overlay materialization." This
phrasing is strong and accurate.

Context from Goal3583 reviews: both goal3584 (Claude) and goal3585 (Gemini) accepted the
Goal3583 measurements and confirmed the claim boundaries are complete. Goal3586 inherits
those boundaries and adds composite-level boundary language. The inheritance is clean.

### Q5: What should the next RayJoin work be after composite scoring: external same-contract CUDA/OptiX baseline, full-overlay continuation, or another target?

**Recommended: external same-contract CUDA/OptiX baseline.**

Goal3584 recommended "composite app scoring first, then external baseline" — Goal3586 has
now delivered the composite score. The natural follow-on is the external baseline.

Rationale: the composite score (Goal3586) establishes a fixed, reproducible internal number
for tracking RayJoin-style performance as a single app metric. The next question a
stakeholder or reviewer will ask is "how does this compare to vanilla RT-core usage without
RTDL?" An external same-contract CUDA/OptiX baseline directly answers that question, using
the same measurement protocol (hot prepared-query median, same fixture tiling, same three
contracts). This converts the internal Embree-vs-OptiX benchmark into an externally
comparable number.

Full-overlay continuation (replacing the active-count contract with full polygon
materialization including row-transfer overhead) is valuable but will likely reduce the
overlay speedup ratio, and its impact on the composite score should be measured against the
now-fixed composite baseline. Attempting it before the external baseline risks measuring two
changes at once.

Another-target work (new routes, new primitives) can proceed independently but should not
be prioritized over the external baseline if the goal is publication-path evidence.

---

## Code and Test Quality

The `_composite` helper in the test is clean and reusable. It reads the JSON directly and
is not coupled to any implementation details beyond the `ratios` array structure, which is
the stable summary format from Goal3583.

The test correctly uses `assertAlmostEqual` for floating-point comparisons. The third test
case (`test_report_documents_score_definitions_and_boundaries`) checks both the score
definitions and the boundary language in a single assertion pass, which is appropriate for
a report-level validation test.

The report's tables are internally consistent with the JSON source and with each other. The
Interpretation section correctly explains the stress/standard ratio difference for the
overlay contract (active-count scales closer to O(n²) for Embree, while the prepared
OptiX continuation amortizes the setup cost). No prohibited claim wording is present in the
report body.

---

## Summary

Goal3586 cleanly converts three per-contract Goal3583 hot prepared-query measurements into
two principled composite scores. The summed wall-time ratio (primary) and geometric mean
(secondary) are the correct choices for their stated purposes. All eight reported numbers
are independently verified from the JSON source artifacts. The boundary language is complete
and machine-checked for the three highest-risk phrases. The caveats are strong enough to
prevent misreading as any of the prohibited claim types.

**Verdict: accept**

Suggested next step: external same-contract CUDA/OptiX baseline (see Q5).
