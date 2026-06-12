# Gemini Review: Goal4314 And Goal4312 Follow-Up Fixes

Date: 2026-06-11

## Verdict

`accept`

## Summary

This review covers the canonicalization of learner-doc claim boundaries (Goal4314) and the follow-up fixes for Claude Goal4312 findings (F-N1, F-N2, F-N3) implemented in Goal4311 and Goal4308.

The changes successfully reduce documentation drift by establishing a single source of truth for claim boundaries and refine the internal evidence artifacts to prevent misleading interpretations of performance data.

## Question-by-Question Analysis

### 1. Does Goal4314 reduce learner-doc claim-boundary drift without changing or expanding the actual boundary?

**Yes.** Goal4314 introduces `docs/learn/current_claim_boundaries.md` as the canonical page for capability and performance claims. This page is linked from all major entry points (READMEs, tutorials, etc.). The content rigorously adheres to the existing v2.10 source-tree boundary and explicitly labels v2.11 work as internal evidence. The structure work simplifies maintenance without expanding the authorized claim surface.

### 2. Is `docs/learn/current_claim_boundaries.md` clear for a new learner and correctly conservative about v2.10 public docs versus active v2.11 internal work?

**Yes.** The document clearly distinguishes between the current public milestone (v2.10) and active development (v2.11). It uses clear "What RTDL Claims" and "What RTDL Does Not Claim" sections that are easy to parse. The conservation of the v2.10 milestone as the "learner-facing" surface is maintained consistently.

### 3. Does the public-doc claim scan still cover the canonical page and preserve zero hard blockers?

**Yes.** The public-doc scan in `docs/reports/goal4248_current_public_docs_claim_boundary_scan.json` correctly includes the new canonical page and reports `hard_blocker_count: 0`. The scan test `tests/goal4248_current_public_docs_claim_boundary_scan_test.py` verifies this with a total of 34 public markdown files.

### 4. Do the Goal4311 follow-up changes properly address F-N1, F-N2, and F-N3?

**Yes.**
- **F-N1 (Metric Resolution):** The scale-profile runner (`scripts/goal3828_current_benchmark_scale_profile_runner.py`) now implements `metric_resolution_status`. It correctly distinguishes between numeric values, non-numeric values, missing paths in JSON, and missing/unparseable stdout files. This is verified by `tests/goal4311_current_scale_timing_floor_guard_test.py`.
- **F-N2 (Dry-Run Status):** The runner now uses `dry_run_policy_only_no_runtime_evaluation` as the summary status for dry runs, as seen in `_summarize_hot_path_floor`. This prevents dry-run artifacts from being mistaken for successful runtime timing evidence.
- **F-N3 (RTNN Embree Metadata):** In `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`, the `ann_embree_quality_payload` correctly removes the inherited `optix_performance` key and provides a relevant `rt_path_note`. This ensures the Embree front door does not carry misleading OptiX-specific metadata.

### 5. Are claim boundaries still blocked for release, public speedup wording, broad RT-core wording, package-install wording, automatic partner selection, true-zero-copy wording, paper reproduction, and app-specific native-engine logic?

**Yes.** These blocks are explicitly listed in `docs/learn/current_claim_boundaries.md` and are enforced across all updated reports and artifacts (`docs/reports/goal4314_...`, `docs/reports/goal4311_...`, `docs/reports/goal4308_...`). The `claim_boundary` dictionaries in JSON artifacts consistently show these authorizations as `false`.

## Final Notes

The implementation of Goal4314 and the Goal4312 follow-ups shows high technical maturity and adherence to the project's conservative claim policy. The documentation structure is now more robust against drift, and the internal evidence collection is more precise in its labeling. No regressions or boundary expansions were observed.
