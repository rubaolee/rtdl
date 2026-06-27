# V4 Goals4753-4754 Review Debt: Full RT-Core Matrix And Analysis

Status: `open_external_review_debt__engineering_continues_to_goal4755`

Goals4753-4754 produced the first complete NVIDIA RT-core same-hardware matrix
for all 10 promoted benchmark apps across V2.14, V3.0.2, and V4.0.

## Evidence

- Raw serious POD matrix:
  `future/v4/evidence/v4_goal4753_serious_all30_clean_2026-06-26/`
- Analysis JSON:
  `future/v4/evidence/v4_goal4754_final_rt_core_matrix_analysis_2026-06-26.json`
- Analysis report:
  `future/v4/v4_goal4754_final_rt_core_matrix_analysis_2026-06-26.md`

## Result

- 30/30 serious rows executed on the RTX A5000 POD with `rc=0` and parseable JSON.
- Embree is not used as a primary denominator.
- All 10 apps now have V2.14/V3.0.2/V4.0 rows.
- Current analysis finds one material V4-over-V2 candidate: `barnes_hut`.
- Current analysis finds three regression rows requiring Goal4755 work:
  `triangle_counting`, `hausdorff_xhd`, and `spatial_rayjoin`.

## Required External Review Questions

1. Is the matrix fair under the user's NVIDIA RT-core primary-denominator rule?
2. Are the per-app hot metrics extracted from the correct payload fields?
3. Is the Barnes-Hut V2.14 denominator with generic helper fallback acceptable as
   same-semantics V2.14 evidence, or must it be split into a denominator caveat?
4. Are Triangle/Hausdorff/Spatial correctly classified as release blockers?
5. Does the analysis correctly block broad high-performance V4 release wording?

## Non-Authorization

This review debt does not authorize release, public V4-over-V2.14 speedup claims,
whole-app high-performance wording, true-zero-copy wording, or final tag.
