# External Review: RT-DBSCAN Goals5097-5103 Representative Partition & Performance Boundary Packet

Date: 2026-07-07
Reviewer: external review (Claude)

## Overall verdict

```text
approve_goals5097_5103_rt_dbscan_representative_partition_and_performance_boundary_packet
```

Evidence is real and recomputes. Correctness uses the strong canonical component-
partition comparison (not a regression to signature-only), the generic extraction
is real, the app/core boundary holds, cold/warm regimes are separated, the cold
headline uses the harsher denominator, and all claim flags are false. No blocking
findings; a few non-blocking hardening notes.

## Verification performed (against real files / evidence)

### A. Correctness

Three representative fixtures matched patched AuthorOfficial on POD with
`all_cases_matched=true` and, per case, `component_partition_matched=true`,
`core_flags_matched=true`, `signature_matched=true`:

- representative_medium_two_clusters3d (100 pts)
- representative_border_shell3d (60 pts; sizes [29,29], core 54, noise 2)
- representative_three_components_noise3d (64 pts)

The comparison uses the label-producing generic route
(`radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns`,
`component_label_policy=positive_root_index_labels_noise_minus_one`) and canonical
partition equivalence from Goal5095, so it is not blind to a border-assignment swap.

### B. Performance boundary

Cold one-shot (`*_cold_pod_optix_summary.json`): rtdl_wall 1.606-1.717 s;
`rtdl_vs_author_reported_total_ratio` 34.1 / 71.8 / 60.7x (recomputed and consistent).
The headline uses the denominator that is least favorable to RTDL (author reported
phase total 0.024-0.047 s), not the favorable process-wall ratio (~4.1-4.6x). Warm
(aggregate `representative_partition_matrix_pod_optix_summary.json`) is 0.0041-0.0057 s
median and is explicitly labeled diagnostic-only in Goal5100, which also lists
"using warm medians as a cold one-shot headline" as forbidden. Cold and warm are not
mixed: cold in separate `_cold_` files, warm in the aggregate matrix file.

### C. Generic extraction

`src/rtdsl/component_partition.py` provides three helpers
(`canonical_partition_labels`, `component_signature_from_partition`,
`partition_equivalent`), parameterized by `noise_label=-1`, operating on abstract
integer label sequences with no dbscan/epsilon/min_points terms. All three are
exported in `__all__` and used by the RT-DBSCAN app. `tests/goal5101` covers label-
renaming invariance and discrimination
(`[10,10,20,-1,20] == [5,5,9,-1,9]`, `!= [5,9,9,-1,9]`), noise preservation, and
fail-closed (`assertRaises(ValueError)`).

### D. App/core boundary

DBSCAN appears in core only in support/benchmark catalogs (`app_support_matrix.py`,
`current_benchmark_front_doors.py`, `current_benchmark_route_decisions.py`,
`backend_comparison_campaign_closeout.py`) as app-tracking metadata. No DBSCAN
algorithmic primitive or engine ABI in core; clustering runs through the generic
radius-graph component route plus the generic partition helpers. Epsilon/minPts,
DBSCAN interpretation, AuthorOfficial comparison, and performance-regime policy
remain app-owned.

### E. Claim boundaries

All representative result JSONs carry `paper_reproduction_claim_authorized=false`,
`performance_claim_authorized=false`, `whole_program_speedup_claim_authorized=false`.
The Goal5103 consolidated packet excludes full RT-DBSCAN paper reproduction, exact
paper dataset provenance, exact author output-format parity, public performance
claim, DBSCAN-native RTDL core primitive, and automatic route selection.

## Blocking findings

None.

## Required amendments

None (the items below are non-blocking).

## Non-blocking notes

1. The warm aggregate JSON lacks an explicit in-file regime tag, and its filename
   does not say "warm" (unlike the `_cold_` files). Add an explicit
   `regime="warm_in_process_diagnostic"` field or filename so the ~0.004 s medians
   cannot be lifted out of context.
2. The warm "favorable 0.119-0.188x" is amortized in-process RTDL vs author per-call
   reported phase; the author binary has no warm-equivalent regime. Even as a
   diagnostic, label it as not regime-matched so it cannot be read as a fair
   regime-to-regime result.
3. The Goal5103 consolidated Boundaries block should add, verbatim, "exact author
   label-ID parity" and "author-performance parity" (present in per-goal reports and
   result JSONs, but not in the consolidated list).
4. Due to an unstable review sandbox (shell timeouts and a truncated JSON tail on one
   summary), the `Ran 11 tests OK` suite was not re-executed; conclusions rest on
   direct reads/greps of the fixtures, result JSONs, `component_partition.py`, the
   tests, and the reports.

## Answers to the review questions

- Representative fixtures valid bounded synthetic cases? Yes. 60/64/100-point
  synthetic structures (two clusters, border shell, three components + noise);
  bounded, with names matching structure.
- POD evidence supports representative same-input correctness? Yes. All three pass
  partition + core-flags + signature on POD; `all_cases_matched=true`.
- Component-partition comparison strong enough? Yes. Canonical per-point partition
  plus core flags (not signature-only); not blind to border swaps.
- Cold/warm performance boundary honest? Yes. Cold 34-72x slower is the headline
  (with the harsher denominator); warm is explicitly diagnostic, non-speedup, and
  forbidden as a headline; regimes are not mixed.
- Generic component-partition helper truly generic? Yes. Pure label utilities,
  `noise_label`-parameterized, no dbscan terms, exported, independently tested.
- App/core boundary intact? Yes. No DBSCAN core primitive; dbscan only in
  catalog/benchmark metadata; interpretation and comparison in the app.
- Full paper/performance claims correctly excluded? Yes (add the two wordings in
  non-blocking note 3 for completeness).
- Can Goals5097-5103 close as a bounded representative RT-DBSCAN packet? Yes, under
  bounded representative correctness plus a cold-unfavorable / warm-diagnostic
  performance boundary; adopting notes 1-2 makes it more robust.

## Conclusion

An honest, verifiable bounded packet: correctness via the strong partition
comparison with POD validation, a genuinely generic extraction, an intact app/core
boundary, a cold headline reported against the least-favorable denominator, and warm
timing strictly scoped as diagnostic. Approved. The non-blocking notes mainly make
the warm regime harder to misuse at the JSON level.
