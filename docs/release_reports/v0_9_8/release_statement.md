# RTDL v0.9.8 Release Statement

Status: released as `v0.9.8`.

RTDL `v0.9.8` is the bounded RTX app evidence and public-claim cleanup release.

The correct release statement is:

> RTDL `v0.9.8` packages reviewed public RTX app evidence and claim-boundary
> cleanup after v0.9.6. It preserves the existing v0.9.6 backend/visibility
> release baseline, adds one newly reviewed public RTX speedup wording row for
> the prepared native road-hazard compact-summary sub-path, and keeps
> database/Jaccard public speedup wording blocked.

## What This Release May Claim

- The current reviewed public RTX wording matrix has `11` reviewed sub-path
  rows.
- `road_hazard_screening / prepared_native_compact_summary_40k` has reviewed
  public wording for the prepared native compact-summary traversal/count
  sub-path only.
- The reviewed road-hazard wording is bounded to 40k copies and excludes
  default app behavior, GIS/routing, row output, Python orchestration, and
  whole-app speedup.
- Goal1214 full local discovery passed: `2366` tests OK with `196` skips.
- Goal1215 release-surface documentation audit passed: `64` tests OK.
- Goal1216 confirmed local release-candidate readiness with 2-AI consensus.
- Goal1218 confirmed no additional pod run is required before release package
  and authorization paperwork for the currently bounded public claims.

## What This Release Must Not Claim

- broad speedup across all RTDL apps;
- whole-app speedup for road hazard;
- public speedup wording for `database_analytics`;
- public speedup wording for `polygon_set_jaccard`;
- that every `--backend optix` run proves NVIDIA RT-core speedup;
- new HIPRT AMD GPU validation;
- new Vulkan parity with OptiX;
- release scope beyond the audited `v0.9.8` support matrix.

## Evidence

- `/Users/rl2025/rtdl_python_only/docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1214_full_local_discovery_after_goal1213_2026-05-01.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1215_release_surface_doc_audit_2026-05-01.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1216_two_ai_consensus_2026-05-01.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1217_two_ai_consensus_2026-05-01.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal1218_two_ai_consensus_2026-05-01.md`
