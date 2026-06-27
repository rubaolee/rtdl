# Call For Review: Phoenix V3 M5 Topology Pod Evidence

Date: 2026-06-20

Reviewer: Claude

## Request

Critically review the final Phoenix V3 M5 topology pod evidence and decide
whether Codex's classification is honest:

- internal M5 topology evidence: passed;
- M5 author-code comparison: blocked because `query_exec` is missing;
- release/public speedup authorization: false;
- Phoenix M7-qualified release rows: 0.

Please answer with:

1. verdict: approve, approve with amendments, or reject;
2. P0/P1 issues;
3. whether the filtered-safe PIP stream repair is acceptable;
4. whether the failed attempts are documented honestly;
5. whether the M5 status should be `partial-plus internal` or something
   stricter.

## Files Under Review

- `docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_topology_intake_summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_pip_point_location_safe100k/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_overlay_active_count_same_contract.json`
- `tests/v3_phoenix_m5_topology_evidence_test.py`

## Evidence Summary

Intake:

```text
status: pass
overall_status: partial_internal_evidence_author_code_blocked
m5_author_code_comparison_status: blocked_query_exec_missing
release_authorized: false
public_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
failures: []
```

PIP point-location:

```text
point_count: 100000
query_generation: backend_parity_filtered_random_bbox
parity_filter_requested: true
parity_filter.accepted_count: 100000
parity_filter.rejected_count: 1
correctness_sample: 100000
exact mismatches after filtering: 0
positive_face_count: 43738
optix_repeats: 1000
embree_repeats: 1000
row_materialization_in_timed_path: false
internal RTDL OptiX speedup vs RTDL Embree: 1.870x
internal native traversal ratio: 2.764x
```

Overlay active count:

```text
output_contract: overlay_active_pair_dependency_count
active_count: 174
same_output_contract: true
active_counts_match: true
all_row_materialization_avoided: true
internal Embree/OptiX timed median ratio: 499.112x
public_speedup_claim_authorized: false
rt_core_speedup_claim_authorized: false
```

Hardware:

```text
NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
compute capability: 8.9
gpu_env_gate: pass
optix_hardware_gate: pass
```

Failed attempts preserved on pod:

- `phoenix_v3_m5_topology_20260620_failed_markdown_none_20260620T173923Z`
- `phoenix_v3_m5_topology_20260620_stopped_unbounded_query_exec_find_20260620T174322Z`
- `phoenix_v3_m5_topology_20260620_failed_pip_tie_mismatch_20260620T175119Z`

Fixes made after failures:

- missing-author Markdown bug fixed and tested;
- `query_exec` search changed from unbounded `/workspace /root` find to
  bounded candidate-path plus `timeout 20s -maxdepth` search;
- PIP query stream changed from random bbox labelled "safe" to
  backend-parity-filtered random bbox that rejects exact-row tie candidates
  before timing;
- evidence tests added and `v3_rebuild` matrix passed.

Verification:

```text
py -3 scripts\run_test_matrix.py --group v3_rebuild
17 modules, 59 tests OK

py -3 scripts\v3_release_wording_gate.py --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.md --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.json --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md --pretty
status: pass
missing_required_scanned_files: []
violations: []
```

## Goal-Level Decision Audit

Decision under review: accept M5 as internal partial-plus evidence and keep
M5 author-code completion blocked.

1. Was Codex foolish?

   Yes, earlier. The unbounded `query_exec` search and the random stream
   labelled "safe100k" were foolish.

2. What actions made it foolish?

   Using a broad find without timeout wasted pod time. Calling a random bbox
   stream "safe" before exact OptiX/Embree row parity filtering nearly converted
   a tie-sensitive result into false evidence.

3. Was there another path?

   Yes: bounded search and backend-parity filtering before timing. That path is
   now implemented.

4. Can Codex now try a different path that solves the problem?

   Yes. The next solving path is to locate or rebuild author `query_exec` and
   rerun the author-code arm, while keeping the current M5 evidence internal.
