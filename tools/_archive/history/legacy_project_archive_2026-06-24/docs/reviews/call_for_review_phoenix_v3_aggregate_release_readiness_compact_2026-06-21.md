# Compact Call For Review: Phoenix V3 Aggregate Release Readiness

Date: 2026-06-21

The full packet timed out. Please perform a focused release-readiness review
from this smaller source set.

Read only these files unless absolutely necessary:

```text
docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
docs/reviews/codex_phoenix_v3_secondary_rt_hardware_scope_waiver_2ai_consensus_2026-06-21.md
docs/reviews/codex_phoenix_v3_source_tree_pod_gated_scoped_release_wording_2ai_consensus_2026-06-21.md
```

Current gate state:

```text
status: blocked_not_release
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
m7_qualified_release_rows: 11
secondary_rt_hardware_scope_waiver_reviewed: true
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row
package_install_claim_authorized: false
multi_gpu_performance_portability_claim_authorized: false
secondary_rt_performance_confirmation_authorized: false
```

Current gate blockers:

```text
release_authorization_false
eleven_row_surface_still_too_narrow_for_major_release
broad_v3_faster_than_v2_claim_not_authorized
current_eleven_row_release_readiness_consensus_blocks_release
```

Validation just run locally:

```text
py -3 scripts/v3_release_wording_gate.py --pretty --json-out docs/rebuild/v3/phoenix_v3_release_wording_gate_2026-06-21.json
py -3 scripts/v3_phoenix_release_readiness_gate.py --pretty --json-out docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json
py -3 scripts/run_test_matrix.py --group v3_rebuild
```

The full matrix reported 91 modules / 438 tests OK.

Question:

After scoped installer closure and scoped hardware waiver closure, is Phoenix
V3 now responsible to release under exactly:

```text
release_scope: source_tree_pod_gated_eleven_row
hardware_performance_scope: single_rtx_4000_ada_driver_550_127_05_pod
```

Use one verdict:

- `release-ready-source-tree-eleven-row-scoped`
- `not-release-ready-fix-p0`
- `reject-overclaim`

If not release-ready, list only the real P0 blockers that remain. If
release-ready, list exact allowed claims and exact forbidden claims.

Write the review to:

```text
docs/reviews/claude_phoenix_v3_aggregate_release_readiness_review_2026-06-21.md
```

Keep the review concise and decisive.
