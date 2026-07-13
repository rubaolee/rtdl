# Call For Review: RT-DBSCAN Goals5097-5103 Representative Partition Packet

Please strictly review the RT-DBSCAN Goals5097-5103 packet.

## Context

This is the next RT-DBSCAN paper-reproduction-app step after the bounded same-input gates. Earlier Goal5095 was amended and externally approved after moving from signature-only comparison to canonical component-partition comparison. Goals5097-5103 now extend that line to representative synthetic fixtures, fair timing regimes, and one generic RTDL system extraction.

## Files To Review

Goal reports:

- `history/internal_docs/goal5097_rt_dbscan_performance_boundary_and_runner_contract_2026-07-07.md`
- `history/internal_docs/goal5098_rt_dbscan_representative_fixtures_2026-07-07.md`
- `history/internal_docs/goal5099_rt_dbscan_representative_correctness_gate_2026-07-07.md`
- `history/internal_docs/goal5100_rt_dbscan_fair_performance_matrix_2026-07-07.md`
- `history/internal_docs/goal5101_component_partition_helper_system_extraction_2026-07-07.md`
- `history/internal_docs/goal5102_rt_dbscan_bottleneck_analysis_2026-07-07.md`
- `history/internal_docs/goal5103_rt_dbscan_goals5097_5102_consolidated_packet_2026-07-07.md`

Call-for-review files:

- `history/internal_docs/call_for_review_goal5097_rt_dbscan_performance_boundary_and_runner_contract_2026-07-07.md`
- `history/internal_docs/call_for_review_goal5098_rt_dbscan_representative_fixtures_2026-07-07.md`
- `history/internal_docs/call_for_review_goal5099_rt_dbscan_representative_correctness_gate_2026-07-07.md`
- `history/internal_docs/call_for_review_goal5100_rt_dbscan_fair_performance_matrix_2026-07-07.md`
- `history/internal_docs/call_for_review_goal5101_component_partition_helper_system_extraction_2026-07-07.md`
- `history/internal_docs/call_for_review_goal5102_rt_dbscan_bottleneck_analysis_2026-07-07.md`
- `history/internal_docs/call_for_review_goal5103_rt_dbscan_goals5097_5102_consolidated_packet_2026-07-07.md`

App and evidence files:

- `Paper-reproduction-apps/rt-dbscan-paper/README.md`
- `Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json`
- `Paper-reproduction-apps/rt-dbscan-paper/results/README.md`
- `Paper-reproduction-apps/rt-dbscan-paper/data/fixtures/representative_fixtures_manifest.json`
- `Paper-reproduction-apps/rt-dbscan-paper/results/representative_partition_matrix_local_cpu_summary.json`
- `Paper-reproduction-apps/rt-dbscan-paper/results/representative_partition_matrix_pod_optix_summary.json`
- `Paper-reproduction-apps/rt-dbscan-paper/results/representative_partition_matrix_representative_medium_two_clusters3d_cold_pod_optix_summary.json`
- `Paper-reproduction-apps/rt-dbscan-paper/results/representative_partition_matrix_representative_border_shell3d_cold_pod_optix_summary.json`
- `Paper-reproduction-apps/rt-dbscan-paper/results/representative_partition_matrix_representative_three_components_noise3d_cold_pod_optix_summary.json`

System extraction:

- `src/rtdsl/component_partition.py`
- `src/rtdsl/__init__.py`
- `tests/goal5101_component_partition_helpers_test.py`
- `Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_component_signature_gate.py`
- `Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_partition_matrix.py`
- `Paper-reproduction-apps/rt-dbscan-paper/scripts/generate_representative_fixtures.py`

## Main Claims To Verify

### A. Correctness

- Three representative synthetic fixtures were generated:
  - `representative_medium_two_clusters3d`
  - `representative_border_shell3d`
  - `representative_three_components_noise3d`
- All three matched patched AuthorOfficial on POD under:
  - canonical component partition
  - core flags
  - normalized component signature
- The comparison is stronger than signature-only and should not be blind to border assignment swaps.

### B. Performance Boundary

- The packet must not claim public RT-DBSCAN paper speedup.
- Cold one-shot RTDL is unfavorable:
  - roughly `1.61s-1.72s`
  - `34x-72x` slower than author reported phase total on these synthetic fixtures
- Warm long-lived-process RTDL is small:
  - roughly `0.0041s-0.0057s` median
  - but this is diagnostic only, not a paper-performance claim
- Please check that cold/warm regimes are not mixed and that warm numbers are not used as a headline.

### C. Generic System Extraction

- `src/rtdsl/component_partition.py` adds generic helpers:
  - `canonical_partition_labels`
  - `component_signature_from_partition`
  - `partition_equivalent`
- These should be generic component-partition helpers, not DBSCAN-specific primitives.
- Verify that RT-DBSCAN app uses them and that tests cover label-renaming invariance, noise preservation, and fail-closed behavior.

### D. System/App Boundary

- RTDL should remain a general system.
- RT-DBSCAN app should own epsilon/minPts, DBSCAN interpretation, AuthorOfficial comparison, and performance-regime policy.
- Please verify that no DBSCAN-native RTDL core primitive or hidden app-specific shortcut was introduced.

### E. Claim Boundaries

Please check that the packet still explicitly excludes:

- full RT-DBSCAN paper reproduction
- exact paper dataset reproduction
- exact author label-ID parity
- full DBSCAN output-format parity
- public performance/speedup claim
- author-performance parity
- DBSCAN-native RTDL engine ABI
- automatic route selection

## Known Local Validation

Command:

```text
py -m unittest tests.goal5092_rt_dbscan_authorofficial_gate_packet_test tests.goal5094_rt_dbscan_authorofficial_component_signature_gate_test tests.goal5101_component_partition_helpers_test
```

Result:

```text
Ran 11 tests OK
```

JSON sanity checks passed for all representative matrix summaries.

All representative result JSONs have:

```text
paper_reproduction_claim_authorized=false
performance_claim_authorized=false
whole_program_speedup_claim_authorized=false
```

## Requested Verdict Shape

1. Overall verdict:
   - approve / approve_with_required_amendments / revise / block
2. Blocking findings:
   - list any correctness, denominator, genericity, or claim-boundary issue
3. Required amendments:
   - especially if warm numbers are overclaimed or genericity is overstated
4. Non-blocking notes
5. Answer these questions:
   - Are the representative fixtures valid bounded synthetic cases?
   - Does POD evidence support representative same-input correctness?
   - Is the component-partition comparison strong enough?
   - Is the cold/warm performance boundary honest?
   - Is the generic component-partition helper truly generic?
   - Did the app/core boundary remain intact?
   - Are full paper/performance claims correctly excluded?
   - Can Goals5097-5103 be closed as a bounded representative RT-DBSCAN packet?

## Requested Verdict Label If Approved

```text
approve_goals5097_5103_rt_dbscan_representative_partition_and_performance_boundary_packet
```
