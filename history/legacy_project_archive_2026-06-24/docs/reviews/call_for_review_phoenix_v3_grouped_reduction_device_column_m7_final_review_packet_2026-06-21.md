# Call For Review: Phoenix V3 Grouped-Reduction Device-Column M7 Final Review Packet

Reviewer: Gemini or Claude.

Project: RTDL Phoenix V3 rebuild.

## Review Target

Please critically review this V3-only final M7 public-row review packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json
```

Primary evidence and prior review context:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.json
docs/reviews/codex_subagent_phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2ai_consensus_2026-06-21.md
```

Raw POD evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_device_columns_262144_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_host_packed_optix_262144_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_device_columns_524288_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_host_packed_optix_524288_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/source_manifest.sha256
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/nvidia-smi.txt
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/gpu_env_gate.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/optix_hardware_gate.json
```

Implementation and tests:

```text
src/rtdsl/optix_runtime.py
examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
scripts/v3_0_m28_raydb_prepared_grouped_refresh.py
scripts/v3_phoenix_grouped_reduction_device_column_pod_evidence.py
scripts/v3_phoenix_grouped_reduction_device_column_m7_final_review_packet.py
tests/v3_phoenix_grouped_reduction_device_column_pod_evidence_test.py
tests/v3_phoenix_grouped_reduction_device_column_m7_final_review_packet_test.py
```

## Proposed Decision

Decide whether either or both of these exact rows can become supplemental
M7-qualified Phoenix V3 row-scoped claims:

```text
grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups
grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups
```

The current packet intentionally says:

```text
m7_promotion_authorized: false
row_scoped_public_speedup_claim_authorized: false
release_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
```

## Key Facts To Check

- generic capability: `grouped_reduction`;
- operation: `prepared_grouped_sum_i64`;
- candidate route: OptiX `cupy_device_columns`;
- host-packed route retained as comparison, not silently replaced;
- existing M7 row retained:
  `grouped_reduction_sum_scalar_broadcast_repeat100_262144`;
- hardware: NVIDIA RTX 4000 Ada Generation POD;
- warmup/repeat: warmup=3, actual repeat=100;
- CPU reference parity: true for both rows;
- device route `host_packed_ray_count: 0` for both rows;
- raw POD JSONs have no git HEAD because the remote directory was not a git
  checkout; `source_manifest.sha256` is the source traceability record.

Measured candidate facts:

```text
262,144 rows / 1,024 groups / 38,043,648 logical rays
host-packed OptiX/device-column OptiX cold+loop: 3.599x
Embree/device-column OptiX cold+loop: 100.019x

524,288 rows / 2,048 groups / 76,087,296 logical rays
host-packed OptiX/device-column OptiX cold+loop: 73.586x
Embree/device-column OptiX cold+loop: 174.645x
```

Important phase attribution:

```text
The 218.248x host-packed/device-column cold-prepare ratio at 524,288 rows is
not only ray-batch preparation. It includes workload-build/input-path collapse,
ray-batch preparation, native prepare, and other measured cold setup.
```

## Questions For The Reviewer

1. Is this genuinely a V3 generic-engine optimization rather than app-specific
   benchmark tuning?
2. Can both exact candidate rows be promoted to supplemental M7-qualified
   row-scoped claims, or only one, or neither?
3. Are the host-packed/device-column OptiX comparisons honest and sufficiently
   phase-attributed?
4. Are the Embree/device-column OptiX comparisons safe only as same-contract
   context, not pure backend-only ratios?
5. Does the missing git HEAD plus `source_manifest.sha256` traceability record
   satisfy review requirements, or is this a P0 blocker?
6. Are the forbidden public wordings strong enough, especially against claiming
   "V3 is 218x faster", true zero-copy, whole-RayDB acceleration, or broad
   V3-over-V2 speedup?
7. What exact P0/P1 changes are required before Codex writes a final 2-AI
   consensus?

## Required Output

Please write the review to:

```text
docs/reviews/gemini_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-21.md
```

Use one verdict:

```text
approve
approve-with-required-fixes
reject
```

Then state exactly one row decision:

```text
promote_both_rows
promote_262144_only
promote_524288_only
promote_neither
```

Be strict. Reject or require fixes if the packet makes the speedups too easy to
misread as whole-app, whole-database, true_zero_copy_authorized, pure backend-only, or
broad V3-over-V2 claims.
