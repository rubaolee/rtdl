# Call For Review: Phoenix V3 Twelve-Row Release Readiness

Date: 2026-06-21

Please critically review the current Phoenix V3 release-readiness state. This is
not a request to approve release by default. Treat the prior V3 failure mode as
the main risk: internal technical progress was previously mistaken for a
responsible user-facing major release.

## Current Local Result

The current local gates report:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
96 modules / 462 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
final_public_surface_gate: true
missing_expected_m7_row_ids: []
release_authorized: false
public_speedup_claim_authorized: false

py -3 scripts/v3_phoenix_release_readiness_gate.py --pretty
status: blocked_not_release
failed_checks: []
m7_qualified_release_rows: 12
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
- release_authorization_false
- twelve_row_surface_still_too_narrow_for_major_release
- missing_point_location_topology_stream_m7_capability_family
- twelve_row_release_readiness_consensus_missing
```

## Files To Read

- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `scripts/v3_release_wording_gate.py`
- `scripts/v3_phoenix_release_readiness_gate.py`
- `scripts/v3_phoenix_m7_row_classification_packet.py`

## Specific Context

The current surface has twelve exact row-scoped M7 rows. The latest added row is:

```text
aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped
```

It is approved only as a generic aggregate-tree fused weighted-vector sum via a
Numba CUDA partner, with 4.082x over CPU/Numba fused baseline. It is not RT-core
evidence, not whole Barnes-Hut, and the 13.591x comparison against the current
prepared RTDL/OptiX frontier-emission route is supporting no-go metadata only.

The current breadth gate records 8/9 planned capability families covered. The
remaining missing family is:

```text
point_location_topology_stream
```

Spatial RayJoin/topology-stream remains future research, not an M7 row.

## Review Questions

1. Is the current twelve-row state a responsible V3 major release? If yes, state
   the exact release scope and required wording. If no, state the exact P0
   blockers.
2. Is the current `blocked_not_release` readiness gate honest and sufficient, or
   does it still hide a release-blocking issue?
3. Is the public wording gate correctly updated for twelve rows, including the
   Barnes-Hut fused-partner row and the no-release/no-broad-speedup boundaries?
4. Does the next-engine queue correctly close active generic-engine work while
   keeping Spatial topology-stream as future research, or is that closure too
   aggressive?
5. What concrete improvements should be made before asking for another release
   decision?

Please return a verdict using one of:

- `release-ready`
- `approve-blocked-not-release`
- `not-release-ready-fix-p0`
- `reject`

Include P0/P1 findings, required fixes, and any exact wording that must be
forbidden or allowed. This review should be saved as:

```text
docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_review_2026-06-21.md
```
