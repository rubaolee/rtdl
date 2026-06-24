# External Claude Review: Phoenix V3 Grouped-Reduction Device-Column M7 Final Review Packet

Reviewer: Claude (`claude-sonnet-4-6`), acting as external AI reviewer, not a
Codex subagent.

Date: 2026-06-22

Target packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json
```

Prior substitute review audited:

```text
docs/reviews/codex_subagent_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2ai_consensus_2026-06-21.md
docs/reviews/external_ai_blocked_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
```

## Verdict

```text
verdict: approve-with-required-fixes
row_decision: promote_both_rows
release_authorized: false
public_global_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
```

Both rows are supported by internally consistent, verifiable raw JSON evidence.
The required fixes are administrative and traceability documentation updates,
not evidence reruns.

Rows reviewed:

```text
grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups
grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups
```

## Arithmetic Verification

Claude independently checked the four raw POD JSON files:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_device_columns_262144_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_host_packed_optix_262144_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_device_columns_524288_repeat100.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/grouped_sum_host_packed_optix_524288_repeat100.json
```

Verified values:

```text
262,144 rows:
  device-column cold+loop: 1.0274 sec
  host-packed cold+loop: 3.6971 sec
  host-packed/device-column cold+loop: 3.5985x
  Embree/device-column cold+loop: 100.019x
  host_packed_ray_count on device route: 0
  CPU reference parity: true
  warmup=3, repeat=100

524,288 rows:
  device-column cold+loop: 1.9970 sec
  host-packed cold+loop: 146.9567 sec
  host-packed/device-column cold+loop: 73.586x
  Embree/device-column cold+loop: 174.645x
  cold-prepare phase ratio: 218.248x
  host_packed_ray_count on device route: 0
  CPU reference parity: true
  warmup=3, repeat=100
```

Claude also confirmed all four JSON files report the same RTX 4000 Ada pod:

```text
NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
```

## P0 Findings

None.

There was no evidence of fabrication, arithmetic inconsistency, suppressed
routes, or misrepresented hardware.

## P1 Findings

### P1-A: Procedural status fields must be superseded

The packet still says:

```text
current_packet_2ai_consensus_status: subagent_codex_consensus_complete
current_packet_external_review_status: subagent_approved_with_p1_fixes_applied
```

That reflected the old substitute path. Under the current refresh protocol,
Codex subagents do not satisfy the external-AI side of 2-AI consensus.

Required fix:

```text
current_packet_external_review_status: claude_external_approved_with_p1_fixes_2026-06-22
current_packet_2ai_consensus_status: claude_external_review_supersedes_codex_subagent_gap_2026-06-22
```

The row `local_gate_reading` values and human-readable status text must also
record the real Claude external review.

### P1-B: Source-manifest scope must be acknowledged

The source manifest covers:

```text
VERSION
src/rtdsl/optix_runtime.py
examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
scripts/v3_0_m28_raydb_prepared_grouped_refresh.py
```

It does not hash the evidence orchestration scripts listed in the review
request. Claude judged this a traceability gap, not an integrity failure,
because the raw benchmark JSON version identifies the manifested M28 script as
the benchmark execution entry point.

Required fix: the packet must explicitly say that the manifest does not cover
the orchestration wrappers, that the manifested M28 script is the measured
benchmark entry point, and that future reruns should expand manifest coverage.

## P2 Findings

- Hot-query performance is essentially route-independent; the material wins are
  cold-prepare/cold+repeat100 wins. Existing wording is acceptable, but future
  prose can make that even clearer.
- Pre-dedup hit-event counts differ between Embree and OptiX, but CPU reference
  parity is the correctness gate. Host-packed OptiX and device-column OptiX
  pre-dedup counts match for each size.
- The `218.248x` value is acceptable as a labeled cold-prepare phase field, not
  as a headline or public end-to-end speedup.

## Supersession Of Subagent-Only Gap

Claude's conclusion:

```text
this real Claude external review supersedes the prior procedural gap
```

The old Codex subagent review was documented honestly, but it did not satisfy
the current external-AI requirement. This review independently verified the raw
JSON arithmetic, hardware, warmup/repeat, CPU parity, and claim boundaries.

The supersession is valid only after P1-A and P1-B are applied.

## Safe Wording Boundary

Approved row-scoped wording after P1 fixes:

```text
For a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada Generation pod, 262,144 rows / 1,024 groups, 38,043,648 logical rays, warmup=3 and actual repeat=100, RTDL's OptiX route prepared the ray batch from cupy_device_columns with host_packed_ray_count=0. Compared with the host-packed OptiX route, cold prepare plus the measured repeat100 loop was 3.599x faster. Embree remains the host-packed route while the OptiX candidate uses cupy_device_columns; under that same grouped_sum contract, the OptiX device-column route was 100.019x faster than Embree for cold prepare plus repeat100 loop. That Embree/device-column ratio is same-contract context, not a pure backend-only ratio. This is a row-scoped prepared grouped_reduction result, not a whole-app, whole-database, true_zero_copy_authorized, or broad V3-over-V2 speedup claim.

For a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada Generation pod, 524,288 rows / 2,048 groups, 76,087,296 logical rays, warmup=3 and actual repeat=100, RTDL's OptiX route prepared the ray batch from cupy_device_columns with host_packed_ray_count=0. Compared with the host-packed OptiX route, cold prepare plus the measured repeat100 loop was 73.586x faster. Embree remains the host-packed route while the OptiX candidate uses cupy_device_columns; under that same grouped_sum contract, the OptiX device-column route was 174.645x faster than Embree for cold prepare plus repeat100 loop. That Embree/device-column ratio is same-contract context, not a pure backend-only ratio. This is a row-scoped prepared grouped_reduction result, not a whole-app, whole-database, true_zero_copy_authorized, or broad V3-over-V2 speedup claim.
```

Additional constraint: do not lead with the `218.248x` cold-prepare phase
ratio. It may appear only as a labeled phase-attribution data point adjacent to
the workload-build/input-path-collapse explanation.

## Explicit Non-Authorization

This review authorizes nothing beyond the two exact row-scoped row IDs listed
above, and only after the P1 documentation fixes are applied.

This review does not authorize:

- Phoenix V3 release;
- broad V3-over-V2 speedup claims;
- whole-RayDB or whole-database acceleration;
- true-zero-copy wording;
- public global speedup claims;
- `218.248x` as a headline or public end-to-end speedup;
- replacement of the existing scalar-broadcast M7 row.

## Final Summary

The evidence is arithmetically sound, internally consistent, and conservatively
bounded. Once the two P1 documentation fixes are applied, both device-column
grouped-sum rows stand as valid supplemental M7-qualified row-scoped evidence
under the exact approved wording above.
