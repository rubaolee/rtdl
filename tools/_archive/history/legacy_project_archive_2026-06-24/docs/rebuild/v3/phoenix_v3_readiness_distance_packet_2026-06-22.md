# Phoenix V3 Readiness Distance Packet

Date: 2026-06-22
Status: `redo_required`

## Bottom Line

Phoenix V3 has a current 13-row / 9-capability scoped evidence surface, a
reviewed source-tree/pod-gated thirteen-row installer scope, and a green full V3
rebuild matrix. That is useful internal evidence, but it is not enough for V3.

It is not release-authorized. The remaining blocker is now the major RTRDL
language/runtime performance mandate: V3 must prove broad V2.x performance
superiority across serious benchmark-app stress tests.

External review is now bounded by
[Phoenix V3 Bounded External Review Protocol](phoenix_v3_bounded_external_review_protocol_2026-06-22.md):
missing Claude/Gemini output must be recorded as a blocker, not retried
indefinitely, and non-release V3 work must continue.

The scoped Claude verdict is recorded as evidence for the 13-row packet, but it
cannot override the major-version performance mandate.

Historical bounded Claude attempt:

```text
external_review_not_obtained_claude_no_output_timeout_after_dossier
stdout bytes: 0
stderr bytes: 0
```

The current continuation handoff is
[Phoenix V3 Current Handoff](../../handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md).

The requirement-by-requirement completion audit is
[Phoenix V3 Release Completion Audit](phoenix_v3_release_completion_audit_2026-06-22.md).

## Current Evidence

Machine gate:

```text
docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json
status: redo_required
m7_qualified_release_rows: 13
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
```

Current release surface:

```text
release-surface rows: 13
planned capability families: 9/9
missing capability families: none
surface row integrity rows: 13
surface row paths all exist: true
surface row unsupported-claim flags blocked: true
surface rows are generic capability rows: true
```

Installer/reproducibility scope:

```text
release_scope: source_tree_pod_gated_thirteen_row
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row
source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true
aggregate_13_row_installer_scope_review_required: false
general_release_installer_ready: false
package_install_claim_authorized: false
```

Secondary hardware scope:

```text
hardware_performance_scope: single_rtx_4000_ada_driver_550_127_05_pod
secondary_platform_closes_release_blocker: true
secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver
secondary_rt_performance_confirmation_authorized: false
multi_gpu_performance_portability_claim_authorized: false
```

Verification:

```text
focused current-surface suite: 27 tests OK
full v3_rebuild matrix: 106 modules / 509 tests OK
```

Latest full matrix:

`docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_serious_paired_conclusion_sync_20260622.json`

## What Is Done

- The old missing-Spatial / surface-width blocker is removed.
- The current surface covers all planned capability families.
- The current surface has a machine-checked 13-row integrity manifest tying
  every row to existing evidence/review/consensus paths and blocked unsupported
  claim flags.
- The scoped installer blocker is closed for source-tree/pod-gated thirteen-row
  use.
- The secondary RT hardware blocker is closed only by a reviewed single-RTX
  hardware-scope waiver.
- Public docs and wording gates keep release, public speedup, broad V3-over-V2,
  package-install, hardware portability, and whole-app claims unauthorized.
- The current full V3 rebuild matrix is green.
- The current public documentation map and tutorial README expose a short,
  safe learner path into V3, recorded in
  `docs/reports/phoenix_v3_short_user_path_guard_update_2026-06-22.md`.
- The completion audit maps the active Phoenix V3 objective to current
  evidence and records the exact non-completion reason:
  broad V2.x runtime performance superiority is not proven.

## What Is Not Done

- The scoped external verdict does not prove V3 as a major language/runtime release.
- The current same-row V3-vs-V2.14 geomean is only `1.012x`.
- All benchmark apps need serious same-RT-hardware reruns as runtime stress tests.
- The staged pod installer is not a general package installer.
- There is no broad hardware portability claim.
- There is no broad V3 faster-than-V2.x claim.
- There is no public Spatial speedup or RTDL-beats-RayJoin claim.
- There is no whole-app acceleration claim.
- There is no true-zero-copy product claim.

## Distance To V3 Release

Technically, the current scoped evidence surface is close: no current machine
gate reports a missing capability family, stale installer scope, or failing V3
rebuild matrix.

Release-wise, it is not one review step away. It needs a real performance redo:

1. Rerun serious same-RT-hardware V3-vs-V2.x benchmarks across all benchmark
   apps as RTRDL language/runtime stress tests.
2. Convert successful work into reusable runtime capabilities, not app patches.
3. Explain every negative or surprising row.
4. Only then request external review for the major-version performance case.

Until that happens, Phoenix V3 remains `redo_required`.

## External Review Process Guard

The current no-output Claude attempt is a recorded blocker, not an active
engineering loop. Future external-review attempts for this packet must follow
the bounded protocol:

```text
one complete packet
one bounded automated attempt in the active work loop
no substantive verdict before timeout -> record external_review_not_obtained
no release promotion without a real external verdict
continue non-release V3 cleanup
```

## Current External Review State

Current review request:

`docs/reviews/call_for_review_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md`

Current external-review attempt record:

`docs/reviews/external_ai_blocked_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_2026-06-22.md`

Recorded scoped-review state:

```text
aggregate_13_row_scoped_dossier_external_review_status:
  external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release
aggregate_13_row_scoped_dossier_external_authorization_obtained: true
major_version_release_authorized: false
```

## Goal-Level Decision Audit

Decision: keep Phoenix V3 in `redo_required` while recording that the scoped
technical surface is useful evidence but broad V2.x runtime performance
superiority is not proven.

1. Was I foolish? Yes.
2. If yes, what actions made the decision foolish? The foolish action would be
   to claim release readiness from 13 rows, 503 tests, or a scoped external
   verdict while the broad V2.x performance case remains weak.
3. Was there another path? Yes. Treat benchmark apps as runtime stress tests,
   not product surfaces, and require broad performance evidence first.
4. Can I now try a different path? Yes. Preserve the current packet as internal
   evidence and redo V3 around reusable runtime improvements that beat V2.x
   materially across serious benchmark-app stress tests.


