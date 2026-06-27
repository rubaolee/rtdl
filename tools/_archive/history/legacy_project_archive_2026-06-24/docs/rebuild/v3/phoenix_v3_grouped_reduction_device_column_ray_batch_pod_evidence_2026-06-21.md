# Phoenix V3 Grouped-Reduction Device-Column Ray-Batch Pod Evidence

Status: pending 2-AI review, not M7 promotion and not release authorization.

```text
status: grouped_reduction_device_column_ray_batch_pod_evidence_pending_2ai_not_m7
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
m7_promoted: false
m7_reopen_candidate_pending_2ai_review: true
failed_checks: none
```

## What This Tests

This packet tests a generic V3 engine route, not a RayDB-specific native
engine: OptiX prepared grouped_sum can prepare its ray batch from
`cupy_device_columns` instead of materializing host-packed ray records first.
The same generated rows, logical ray count, warmup, repeat, and CPU-reference
checks are used for the host-packed OptiX baseline.

## Summary

- Minimum OptiX host-packed / device-column cold-prepare speedup:
  `6.022x`
- Minimum OptiX host-packed / device-column cold-plus-loop speedup:
  `3.599x`
- Maximum OptiX host-packed / device-column cold-plus-loop speedup:
  `73.586x`
- Minimum Embree / OptiX-device-columns hot-query speedup:
  `173.013x`
- Minimum Embree / OptiX-device-columns cold-plus-loop speedup:
  `100.019x`
- All CPU references match: `true`
- Host-packed rays eliminated on device route:
  `true`

## Candidate Exact Rows

These rows are candidates for M7 reopening only. They do not replace the
already approved host-packed/scalar-broadcast row.

| Candidate row id | Rows | Groups | Logical rays | Layout | Warmup | Repeat | Replaces existing M7 row |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups | 262,144 | 1,024 | 38,043,648 | cupy_device_columns | 3 | 100 | false |
| grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups | 524,288 | 2,048 | 76,087,296 | cupy_device_columns | 3 | 100 | false |

## Route Integrity

| Rows | OptiX route layout | Created from | Native device-column path | Host-packed rays on device route | Logical rays | Eliminated |
| ---: | --- | --- | --- | ---: | ---: | --- |
| 262,144 | cupy_device_columns | partner_device_columns | true | 0 | 38,043,648 | true |
| 524,288 | cupy_device_columns | partner_device_columns | true | 0 | 76,087,296 | true |

## Performance Table

| Rows | Logical rays | Host/device cold prepare | Host/device ray-batch prepare | Host/device cold+loop | Embree/device hot query | Embree/device cold+loop | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 262,144 | 38,043,648 | 6.022x | 5.538x | 3.599x | 203.492x | 100.019x | pending_2ai_review_not_m7 |
| 524,288 | 76,087,296 | 218.248x | 8.243x | 73.586x | 173.013x | 174.645x | pending_2ai_review_not_m7 |

## Phase Table

The cold-prepare speedup includes workload-build/input-path collapse,
ray-batch preparation, native prepare, and other measured cold setup. It must
not be described as only ray-batch preparation.

| Rows | Device workload build | Host workload build | Host/device build | Device ray-batch prepare | Host ray-batch prepare | Host/device ray-batch | Device cold prepare | Host cold prepare |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 262,144 | 0.050s | 1.625s | 32.466x | 0.234s | 1.298s | 5.538x | 0.527s | 3.176s |
| 524,288 | 0.105s | 142.852s | 1362.274x | 0.305s | 2.510s | 8.243x | 0.667s | 145.626s |

## Pre-Dedup Hit Events

Embree and OptiX pre-dedup hit-event counts can differ. The semantic gate is
the grouped reduction result, and all rows match the CPU reference.

| Rows | Embree pre-dedup hits | OptiX device-column pre-dedup hits | OptiX host-packed pre-dedup hits | CPU reference match |
| ---: | ---: | ---: | ---: | --- |
| 262,144 | 1,853 | 3,693 | 3,693 | true |
| 524,288 | 3,683 | 7,386 | 7,386 | true |

## Interpretation

This is a material V3 engine optimization candidate because it attacks the
prepared grouped-reduction input path itself. The 524,288-row baseline shows
why earlier V3 wording was not enough: host-packed ray materialization can
dominate the story even when the hot RT query is fast. The device-column route
keeps the hot query essentially comparable while removing host-packed ray
records from the OptiX candidate path.

The Embree/device-column ratios are same-contract backend context, not pure
backend-only ratios, because the Embree route remains host-packed while the
OptiX candidate uses `cupy_device_columns`.

This is still not release wording. It needs external review before it can
supersede or expand the existing grouped_reduction M7 row.

## Public Copy Rules

- Say this is a grouped_sum prepared-query route candidate, not whole RayDB.
- Say cupy_device_columns avoids host-packed ray-record materialization on the OptiX route.
- Report host-packed OptiX versus device-column OptiX before quoting Embree/OptiX ratios.
- Report cold prepare and cold-plus-loop next to hot prepared-query timing.
- Say the cold-prepare win includes workload-build/input-path collapse, not only ray-batch preparation.
- State that Embree and OptiX pre-dedup hit-event counts can differ while CPU-reference reduction still matches.
- Name the RTX 4000 Ada pod, generated row count, logical ray count, warmup, and repeat.
- Keep public release wording blocked until 2-AI review closes.

## Forbidden Public Wording

- Do not claim: release wording for V3
- Do not claim: broad V3-over-V2 win
- Do not claim: RayDB is universally accelerated
- Do not claim: This proves true zero-copy
- Do not claim: This is an M7-qualified row before 2-AI review
- Do not claim: All grouped_reduction rows are now public claims

## Next Actions

- Send this packet to Claude/Gemini for critical review.
- If review approves, treat this as a new exact row candidate keyed by cupy_device_columns, not an implicit replacement of the current grouped_reduction M7 row.
- Update the public grouped_sum tutorial only after the review-bound wording is closed.
- Continue the next generic-engine queue item if review rejects or scopes this as internal only.

## Source Evidence

Source candidate packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_candidate_2026-06-21.md
```

POD artifact directory:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621
```

Source traceability record:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/source_manifest.sha256
```

Source manifest entries:

```text
c1cc6ce99096d1d12968d44a890518b8dc8a8cb212b7bf31cf578c9a0b221e20  VERSION
218d58519fd0e13ba0dad4049d3e06f11f863e03772f157e2ebfac88e93fa93c  src/rtdsl/optix_runtime.py
df703fa260488258ee4db68ab1fcf795ae6edf2ed50f5c89f0b18a7071f18c80  examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
3eed5a1bf688a2cc7da6c66cbe4ce23ea3884949275a44fc5e3a8942993f36c7  scripts/v3_0_m28_raydb_prepared_grouped_refresh.py
```

Raw evidence git-head values:

```text
fatal: not a git repository (or any of the parent directories): .git
```

Interpretation:

The remote POD run directory was not a git checkout, so raw evidence JSONs record git_head as unavailable. The SHA256 source manifest is therefore the source traceability record for this packet.

## Goal-Level Decision Audit

Decision: convert the POD device-column grouped_reduction results into a pending-2AI M7 reopen candidate instead of promoting it immediately

1. Was I foolish?
   No. The measured gains are material, but public promotion still needs review.
2. If yes, what actions made the decision foolish?
   It would be foolish to advertise the 173x/203x hot query ratios alone, or to call the device-column route true zero-copy, or to skip the host-packed OptiX baseline that explains why V3 changed technically.
3. Was there another path that would have avoided getting stuck on that idea?
   Promote the existing 262,144-row M7 result and keep polishing docs. That would avoid risk but would not answer the user's performance-first concern.
4. Can I now try a different path that actually solves the problem?
   Treat this as a generic engine improvement: prove host packing is removed, show cold-plus-loop speedups, then ask external review whether the row can enter the V3 release surface.
