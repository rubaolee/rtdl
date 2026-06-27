# Call For Review: Phoenix V3 Grouped-Reduction Device-Column Ray-Batch Pod Evidence

Date: 2026-06-21

Requested reviewer: Claude

## Scope

Review the new Phoenix V3 grouped_reduction device-column ray-batch POD
evidence. This is a candidate generic-engine optimization for the prepared
grouped_sum route, not V3 release authorization and not an M7 promotion.

Primary files:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.json
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_candidate_2026-06-21.md
docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_device_columns_262144_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_host_packed_optix_262144_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_device_columns_524288_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_host_packed_optix_524288_repeat100.json
tests/v3_phoenix_grouped_reduction_device_column_pod_evidence_test.py
scripts/v3_phoenix_grouped_reduction_device_column_pod_evidence.py
```

Context:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.md
docs/reviews/codex_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2ai_consensus_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_public_surface_closure_2026-06-21.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
```

Verification already run by Codex:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test
6 tests OK

py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test
17 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []

py -3 scripts/v3_phoenix_release_readiness_gate.py --pretty
status: blocked_not_release
failed_checks: []
```

Key observed numbers from the packet:

```text
262,144 rows / 38,043,648 logical rays:
- OptiX host-packed over OptiX device-columns cold prepare: 6.022x
- OptiX host-packed over OptiX device-columns cold+loop: 3.599x
- Embree over OptiX device-columns hot query: 203.492x
- Embree over OptiX device-columns cold+loop: 100.019x
- device route host_packed_ray_count: 0

524,288 rows / 76,087,296 logical rays:
- OptiX host-packed over OptiX device-columns cold prepare: 218.248x
- OptiX host-packed over OptiX device-columns cold+loop: 73.586x
- Embree over OptiX device-columns hot query: 173.013x
- Embree over OptiX device-columns cold+loop: 174.645x
- device route host_packed_ray_count: 0
```

## Review Questions

1. Is this correctly classified as a reusable V3 generic-engine optimization,
   rather than RayDB app-specific tuning?
2. Does the packet honestly compare device-column OptiX against host-packed
   OptiX before using Embree/OptiX ratios?
3. Are the cold prepare, cold-plus-loop, logical-ray-count, and CPU-reference
   facts sufficient to reopen M7 review for grouped_reduction?
4. Should this candidate supersede the current exact M7 row
   `grouped_reduction_sum_scalar_broadcast_repeat100_262144`, become a new
   exact row, or remain internal only?
5. What P0/P1 fixes are required before Codex can write 2-AI consensus?

## Required Output

Please save your review to:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_review_2026-06-21.md
```

Use verdict:

```text
approve
approve-with-required-fixes
reject
```

List P0 and P1 issues separately.
