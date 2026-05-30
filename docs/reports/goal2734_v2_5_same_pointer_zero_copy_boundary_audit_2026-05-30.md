# Goal2734: v2.5 Same-Pointer / Zero-Copy Boundary Audit

Date: 2026-05-30
Status: accepted as claim-boundary audit

## Purpose

Goal2729 and Goal2732 both accepted the v2.5 primitive-first correction with a remaining boundary: same-pointer hardware evidence is useful, but it must not be promoted into public true-zero-copy wording.

Goal2734 makes that boundary explicit and testable.

## Evidence Reviewed

The audit covers the current v2.5 hit-stream pod artifacts that record Torch/Triton carrier same-pointer evidence:

- `docs/reports/goal2715_pod_artifacts/goal2715_raydb_native_device_hit_stream_pointer_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2716_pod_artifacts/goal2716_hit_stream_carrier_execution_flag_smoke_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2719_pod_artifacts/goal2719_native_output_proven_materialization_removed_smoke_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2720_pod_artifacts/goal2720_raydb_prepared_device_hit_stream_smoke_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2722_pod_artifacts/goal2722_raydb_prepared_device_hit_stream_large_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2726_pod_artifacts/goal2726_raydb_v24_native_vs_v25_prepared_probe_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2727_pod_artifacts/goal2727_raydb_prepared_grouped_vs_hit_stream_large_pod_69_30_85_171_2026-05-30.json`
- `docs/reports/goal2731_pod_artifacts/goal2731_raydb_primitive_first_minmaxavg_gap_pod_69_30_85_171_2026-05-30.json`

Across those artifacts, the current same-pointer evidence set contains 47 cases.

## Finding

All same-pointer cases preserve the correct boundary:

- `torch_carrier_same_pointer_evidence_observed` or `torch_carrier_execution.same_pointer_evidence_observed` is true.
- `true_zero_copy_authorized` remains false at the case level.
- `torch_carrier_execution.true_zero_copy_authorized` remains false when execution metadata is present.
- `no_public_speedup_claim` remains true at the artifact level when that field is present.

This means the v2.5 path has evidence that the Torch carrier can preserve device pointers for the hit-stream/payload columns in these measured cases. It does not prove a complete public true-zero-copy contract because ownership, lifetime, stream synchronization, cleanup, cross-partner transfer semantics, and public wording review remain separate gates.

## Zero-Copy Candidate vs Authorization

Some artifacts contain `zero_copy_candidate = true` inside adapter planning metadata. That is acceptable only as a candidate label. It is not authorization. The guard test ensures candidate labels do not coincide with `true_zero_copy_authorized = true` in the v2.5 hit-stream evidence set.

## Public Documentation Boundary

Learner-facing docs may explain that v2.5 has internal same-pointer evidence and device-resident column experiments. They must not say that true zero-copy is authorized unless a future release gate explicitly approves that exact public claim.

## Verdict

Same-pointer evidence is accepted as internal v2.5 engineering evidence.

Public true-zero-copy wording remains blocked.
