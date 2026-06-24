# Claude Recorded Review: Phoenix V3 M60 Step-2 Set-A Selection

Date: 2026-06-23

Recorded sources:

- `docs/reviews/claude_phoenix_v3_m60_step2_set_a_selection_review_2026-06-23.raw.md`
- `docs/reviews/claude_phoenix_v3_m60_debt_followup_2026-06-23.raw.md`

Verdict:

```text
accept_m60_select_spatial_topology_stream_for_local_set_a_step2
```

Debt follow-up verdict:

```text
p1b_superseded_by_m53_no_m60_verdict_change
```

## Review Read

Claude accepts M60's selection of Spatial/RayJoin point-location topology stream
as the next local Step-2 Set-A runtime-family target. The accepted scope is
generic topology-stream prepared-handle, internal residency, and full-M3
phase-accounting work. Claude also confirms that M60 correctly avoids RayJoin
app-specific route tuning and preserves the no-POD/no-release boundary.

## Carry-Forward Findings

P1 carry-forward into M61:

- The `2.282x` device-resident internal delta must be labeled
  `internal_routing_delta_not_public_row`. It must not appear as a public
  speedup row or imply RTDL beats RayJoin author timing.

P2 carry-forward into M61/release work:

- The M59 OptiX cold single-shot Set-B row remains yellow/open and still needs
  accepted user-language explanation or a separately reviewed overhead fix
  before any V3 release decision.
- M61 must map or supplement the existing `PreparedExecutionReport` phase
  vocabulary so the full topology-stream M3 table can be emitted:
  `static_scene_prepare_sec`, `query_stream_prepare_sec`,
  `device_transfer_or_residency_sec`, `rt_traversal_sec`,
  `topology_continuation_sec`, and
  `host_return_or_scalar_materialization_sec`.

Claude's original P1-B about M43 review debt is superseded by M53. M61 may cite
M43/M44 only through the completed M53 debt-backfill trail, not through the
stale M44 sentence that originally recorded Claude debt as open.

## Non-Authorization

This review does not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure
