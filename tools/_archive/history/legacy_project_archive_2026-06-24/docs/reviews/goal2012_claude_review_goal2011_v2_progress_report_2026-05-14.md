# Goal2012 Claude Review — Goal2011 v2.0 Progress Report

Date: 2026-05-14

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **accept-with-boundary**

---

## Scope

Independent read-only review of
`docs/reports/goal2011_v2_0_progress_report_for_external_review_2026-05-14.md`
against six verification criteria. Cross-referenced against:

- `docs/reviews/goal2007_claude_review_goal2006_prepared_cupy_exact_filter_2026-05-14.md`
- `docs/reviews/goal2010_claude_review_goal2009_prepared_cupy_triangle_lookup_cache_2026-05-14.md`
- `docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_2048.json`
- `docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_4096.json`
- `docs/reports/goal2006_pod_smoke/road_hazard_cupy_exact_filter_smoke_64.json`
- `scratch/HANDOFF_GOAL2006_EXTERNAL_REVIEW.md`
- `scratch/HANDOFF_GOAL2009_CLAUDE_REVIEW.md`

No source files were modified.

---

## Check 1 — v2.0 Purpose and v1.8/v2.0 Distinction

**Pass.**

The report cleanly separates the two milestones. "Current High-Level State" opens
with:

> "v1.8 established the app-agnostic native engine boundary. v2.0 is now building
> the partner-runtime layer on top of that boundary."

The purpose statement names the v2.0 goal precisely:

> "Python + RTDL + partner tensors … v2.0 is not trying to put app logic back inside
> the RTDL native engine."

These sentences correctly characterize v1.8 as boundary-setting and v2.0 as
partner-layer construction. No blurring of the two milestones is present.

---

## Check 2 — Native Engine App-Agnostic Rule

**Pass.**

The "Architectural Boundary Being Protected" section explicitly states:

> "RTDL native engine = generic primitive producer  
> Python + partner layer = app semantics, exact filters, reductions, summaries"

The report correctly notes that v1.0/v1.6 had app-shaped native paths and that
v1.8 removed them; it names the risk that v2.0 could reintroduce them. The
Goal2000–2009 goal descriptions are each told through the lens of preserving this
boundary: native OptiX emits `generic_ray_primitive_candidate_witness_pairs`, and
all segment/polygon/road-hazard semantics are attributed to the partner layer.

The "Design Lessons" section reinforces the rule in four of five items. The rule
is never violated in the narrative.

---

## Check 3 — Goal Descriptions: Purpose and Effect

### Goal2000

**Pass.**

The report correctly identifies both issues Goal2000 addressed:

1. Float32 ray-column ABI enforcement for the all-witness device path.
2. Over-strong interpretation of all-witness output as exact app rows, corrected
   to `generic_ray_primitive_candidate_witness_pairs`.

The stated effect (correctness repaired; host exact filtering introduced as a
temporary measure; performance debt exposed) is accurate and matches the public
record from prior reviews. The "review interpretation" correctly frames Goal2000
as a correctness and claim-boundary goal rather than a performance advance.

### Goal2003

**Pass.**

The report correctly states that Goal2003 moved the exact segment/triangle filter
from host Python to a CuPy RawKernel on the partner GPU, while native OptiX
continued to emit only generic candidate witnesses. The performance table is
directionally consistent with the expected GPU/CPU crossover pattern: at count 256
the kernel launch overhead dominates (2.263x slower), while at count 2048 and 8192
the GPU filter wins substantially (0.145x, 0.0129x). Direct cross-check of the
Goal2003 pod artifact was not available in the reviewed materials; the table is
accepted on the basis of physical plausibility and the broader review chain.

The claim "CuPy hit-count metadata can honestly record `whole_app_true_zero_copy_authorized:
true`" is consistent with the smoke artifact inspected for Goal2006, which confirmed
that flag is set to `true` in the partner metadata when the CuPy exact filter is
active.

### Goal2006

**Pass with provenance note (non-blocking).**

The narrative is correct: Goal2006 fixed the prepared-scene path by wrapping the
native prepared OptiX scene in a Python object that retains caller-owned triangle
columns, enabling CuPy exact filtering before partner-side unique-pair counting.
The Goal2007 review (accepted-with-boundary) and Goal2008 review (accepted) are
correctly attributed.

**Provenance discrepancy in the Goal2006 timing table.**

The report shows:

| Row | Median (s) | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| Goal2006 prepared CuPy exact-filter priority columns | 0.003149398 | 0.907x |

The Goal2007 review verified from the Goal2006 pod artifact
(`road_hazard_prepared_cupy_exact_filter_2048.json`) that
`query_median_ratio_vs_v1_8_prepared_native` was `0.9225`, implying a median of
approximately 0.003205 s. The progress report's numbers (0.003149398 s, 0.907x)
are internally consistent with the v1.8 prepared baseline shown (0.003474137 s),
but they do not match the Goal2006 pod artifact that was officially reviewed.

The v1.8 one-shot baseline also differs between the two tables (16.327098407 s for
the Goal2006 table vs 16.492227267 s for the Goal2009 table), confirming they come
from different pod runs. The most likely explanation is that the Goal2006 row in the
progress report was re-measured during the Goal2009 pod run and reflects different
pod timing, rather than numbers from the original Goal2006 artifact.

The direction is unaffected (prepared CuPy is faster than v1.8 prepared in both
runs), and the claim "modestly faster" holds under either measurement. However, the
report does not explain the source of the Goal2006 table numbers or acknowledge that
they differ from the previously reviewed pod artifact. This is a non-blocking
provenance gap that a final v2.0 release report should resolve.

### Goal2009

**Pass.**

All reported numbers cross-check precisely against pod artifacts.

Count 2048 cross-check:

| Field | Artifact | Report |
| --- | ---: | ---: |
| v1.8 one-shot median (s) | 16.492227267473936 | 16.492227267 |
| v1.8 prepared median (s) | 0.0034781303256750107 | 0.003478130 |
| Unprepared CuPy median (s) | 0.0031884759664535522 | 0.003188476 |
| Unprepared CuPy ratio | 0.9167212461582375 | 0.917x |
| Cached CuPy median (s) | 0.0025192387402057648 | 0.002519239 |
| Cached CuPy ratio | 0.724308322091654 | 0.724x |

Count 4096 cross-check:

| Field | Artifact | Report |
| --- | ---: | ---: |
| v1.8 one-shot median (s) | 104.25956045277417 | 104.259560453 |
| v1.8 prepared median (s) | 0.009691450744867325 | 0.009691451 |
| Unprepared CuPy median (s) | 0.005996620282530785 | 0.005996620 |
| Unprepared CuPy ratio | 0.6187536252719074 | 0.619x |
| Cached CuPy median (s) | 0.00393231026828289 | 0.003932310 |
| Cached CuPy ratio | 0.4057504259994795 | 0.406x |

All artifact `claim_boundary` flags verified:

| Flag | Artifact | Expected |
| --- | --- | --- |
| `v2_0_release_authorized` | `false` | false |
| `broad_rt_core_speedup_claim_authorized` | `false` | false |
| `package_install_claim_authorized` | `false` | false |
| `whole_app_speedup_claim_authorized` | `false` | false |
| `same_contract_timing_row` | `true` | true |
| `partner_output_columns_true_zero_copy_authorized` | `true` | true |

The derived figures ("about 2.46x faster than v1.8 prepared" at count 4096,
"about 1.52x faster than unprepared CuPy") are arithmetically correct:
1/0.4057504 ≈ 2.465x and 1/0.6558 ≈ 1.525x. Goal2010 verdict (accept) is
correctly attributed.

---

## Check 4 — Performance Claims Narrow Enough for the Artifacts

**Pass.**

Every performance table in the report is labeled with a specific count, a specific
GPU (NVIDIA RTX A5000), and a specific contract (road-hazard prepared CuPy priority
columns or segment/polygon CuPy hit-count columns). No table is presented as a
"general" speedup.

The "Current Performance Picture" section correctly notes that fixed-radius and
compact-output rows remain the strongest evidence, and that the segment/polygon and
road-hazard rows demonstrate the intended pattern rather than universal acceleration.
The caveat that database, graph, polygon area, and Jaccard rows "should not be
marketed as arbitrary SQL, graph, or GIS overlay acceleration" is appropriately
strict.

---

## Check 5 — No Overclaims of Release Readiness or Broad Speedup

**Pass.**

The "Current High-Level State" section lists what the evidence does not support:

- final v2.0 release authorization
- broad RT-core speedup wording
- arbitrary Python acceleration wording
- arbitrary PyTorch/CuPy acceleration wording
- package-install readiness
- claiming every public app has a broad, fair, full-app v2 speedup

The "Current Claim Boundary" section repeats the "Not allowed yet" list with the
same items. These align with the artifact `claim_boundary` flags, all of which
correctly show `false` for release and broad-speedup gates.

The report's title explicitly states "external-review-requested" rather than
"release-authorized," and no language in the body asserts release readiness.

---

## Check 6 — Stated Next Work Is Reasonable

**Pass.**

The "Open Risks And Debt" section lists six items that are appropriate and
internally consistent with the current state of the evidence:

1. Refreshed all-app table incorporating Goal2006/Goal2009 numbers — warranted
   given that some rows still reference Goal1946-era data.
2. Torch equivalent of the CuPy device-side exact filter — correctly identified
   as missing.
3. Pod artifact provenance gap (`git_commit: unknown`) — a pre-existing issue
   acknowledged in prior reviews, correctly flagged here.
4. JIT warmup reporting — a non-blocking consistency improvement; both the
   Goal2009 artifacts show a large first-sample outlier that the median correctly
   ignores, but separating it explicitly would improve reproducibility claims.
5. All-app table wording for database, graph, polygon — appropriate given the
   review chain's repeated caution on these rows.

No next-work item implies an imminent release gate that has already been met.

---

## Non-Blocking Observations

1. **Goal2006 table provenance** (described under Check 3): The report uses
   Goal2006 timing numbers (0.907x) that differ from the Goal2007-verified pod
   artifact (0.9225x) without identifying which pod run the table reflects. For a
   progress report this is acceptable; for any formal release report it should be
   resolved by citing the specific pod artifact or re-running and citing the
   new artifact.

2. **"4741.70x slower" and "10757.88x slower" ratios**: These are derived by
   dividing the v1.8 one-shot median by the v1.8 prepared median. At count 2048:
   16.492227267 / 0.003478130 ≈ 4741.4x (report: 4741.70x), and at count 4096:
   104.259560453 / 0.009691451 ≈ 10759.7x (report: 10757.88x). Both are within
   sub-0.03% of each other due to rounding of the displayed prepared-baseline
   median. Not a substantive error.

3. **Goal1975–1985 and Goal1987–1997 summaries** are not verifiable against
   artifacts in the reviewed set, but are presented as background context rather
   than performance claims. Their "review interpretation" paragraphs correctly
   bound what those goal chains authorize.

4. **The report does not attempt to aggregate all rows into a single speedup
   figure**, which is correct given the heterogeneous app contracts. This restraint
   should be maintained in any follow-on summary.

---

## Summary

The progress report accurately describes the v1.8/v2.0 architectural division,
consistently enforces the native-engine app-agnostic rule, and correctly narrates
the purpose and effect of Goals 2000, 2003, 2006, and 2009. Goal2009 timing
numbers verify precisely against pod artifacts. Performance claims are correctly
scoped to narrow same-contract rows on the A5000 pod. All overreach gates (release
readiness, broad RT-core speedup, package-install, arbitrary PyTorch/CuPy
acceleration) are maintained in both the narrative and the artifact
`claim_boundary` fields.

The single boundary item is the Goal2006 table's provenance: numbers that differ
from the Goal2007-reviewed artifact without explanation of which run produced them.
The claim direction (prepared CuPy faster than v1.8 prepared) is correct under
either measurement, so this does not affect the accuracy of the architectural
narrative.

**Verdict: accept-with-boundary**

Boundary: Clarify the source of the Goal2006 timing table (0.907x / 0.003149398 s)
before promoting these numbers in any release-facing document. All other claims
and boundary language are correct as written.
