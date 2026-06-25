# Goal4646 Pre-Tag Mandatory Wording Fixes (Blocking)

Date: 2026-06-25
Source: `docs/reviews/claude_v4_0_0_release_review_2026-06-25.md`
Status: **completed locally — external review requested before public tag.**

The V4.0.0 bounded operator release is accepted on substance (real POD
measurement, tight scope, honest exclusion of barnes_hut/rayjoin). These are the
wording/measurement-presentation fixes required before any public tag, so the
release does not become a v3.0-style over-claim by label.

## Fix 1 — Qualify the "high-performance" label (state the baseline)

Problem: the label "high-performance generic RT-core operator release" reads as
"near hand-written OptiX," but the Goal4639 ratios are vs a Torch/partner (or
CPU brute-force) baseline. Hand-written OptiX was never measured.

Required:

- [x] Public label changed to, in substance: **"faster than brute-force partner
      baselines on 8 generic RT-core operators."**
- [x] Every public surface mentions the comparison is **vs brute-force
      partner/CPU baselines**, not vs hand-written OptiX.
- [x] No unqualified "high-performance" or "near-OptiX" wording in README,
      release notes, `docs/current_v4_status.md`, or `docs/learn/performance_wording.md`.

## Fix 2 — Report the honest ratio distribution, not the inflated geomean

Problem: the `5.18x` "strong geomean" is dominated by two algorithmic-complexity
outliers (point_nearest 389.7x, aabb_index 164.7x = O(n^2) brute force vs
O(n log n) BVH). The honest core is ~1.2-1.7x.

Required:

- [x] Release wording reports the **distribution**: most operators 1.2-1.7x vs
      partner baseline; two large wins where the alternative is O(n^2).
- [x] The two O(n^2)-vs-BVH outliers are labeled as **algorithmic-complexity
      wins** (scale-dependent), not kernel-quality wins.
- [x] If a single headline number is used, it is the median/core-cluster figure
      (~1.4-1.7x), with the outliers shown separately — not the 5.18x geomean.

## Fix 3 — State the denominator for every "representative ratio"

Problem: the scorecard reports ratios without naming the baseline or data scale.

Required:

- [x] Each of the 8 surfaces annotated with `baseline = {torch|embree|cpu}` and
      the data scale used.
- [x] The scorecard summary states the baseline convention explicitly; no bare
      ratio appears without its denominator.

## Exit gate for Goal4646

- [x] Fix 1, Fix 2, Fix 3 all complete.
- [x] Scope boundaries from Goal4642/4643 preserved verbatim (no scope expansion).
- [x] Tag/release packet ready for owner approval, pending external wording-fix review.

## Deferred to V4.1 (not blocking the tag)

- A4: add a hand-written OptiX baseline for at least one low-ratio operator
  (e.g. component_union 1.20x / argmin 1.26x) to determine whether the fusion is
  good or mediocre. Until then, the release claims only "beats brute-force
  partner baselines," never "approaches the OptiX ceiling."

## Non-authorization

Completing this checklist authorizes only the bounded operator tag with the
corrected wording. It does not authorize broad/whole-app/all-benchmark speedup,
near-OptiX wording, zero-copy, Tier-3, embedding, C-ABI, or app-identity kernels.
