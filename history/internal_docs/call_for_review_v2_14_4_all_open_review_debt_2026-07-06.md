# Call For Review - v2.14.4 All Open Review Debt

Date: 2026-07-06

This is the consolidated review request for all currently open v2.14.4 review
debt.

## Current Gate State

The current release preflight says:

```text
overall_status: blocked_by_release_gates
```

Gate summary:

```text
required_goal_reports_present: pass
strict_pod_smoke: pass
public_surface_internal_leak_scan: pass
legacy_rayjoin_public_exports_disclosed: pass
external_review_debt: blocked
```

Open review debt:

```text
Goal5048
Goal5049
Goal5050
Goal5051
Goal5052
Goal5053
Goal5055
Goal5056
Goal5057
Goal5058
Goal5059
Goal5060
Goal5061
Goal5062
```

## Scope To Review

v2.14.4 is **not** a RayJoin performance release.

v2.14.4 is an RTDL API consolidation milestone.  It turns the reusable system
pieces proven during the v2.14.3 RayJoin work into public, generic, claim-bounded
RTDL API surfaces:

```text
DeviceColumnBuffer
PreparedGeometrySession
device_order_by
NumbaPartnerContinuation
```

The intended system shape is:

```text
RTDL primitive output
-> typed device columns
-> prepared/session metadata
-> generic device ordering
-> approved Numba partner continuation
```

RayJoin is an app and a regression workload on top of RTDL.  It is not the
system identity.

## Not Authorized

Please reject any wording or implication that v2.14.4 authorizes:

```text
v2_14_4_speedup_claim
author_parity_claim
true_zero_copy_claim
device_group_by_public_ready
all_public_exports_rayjoin_free
all_internal_symbols_rayjoin_free
public_release_ready_without_review
public_release_ready_without_pod_smoke
```

The locked performance boundary remains the v2.14.3 / Goal5040 result:

```text
RTDL prepared binary route, top4 six-batch sum: 0.328842s
AuthorOfficial core phases, top4:                0.187042s
Ratio:                                           1.76x slower
```

v2.14.4 preserves and packages API structure.  It does not claim a new
performance win.

## Important Known Boundary

Goal5059 amends a real overclaim found during review: several RayJoin-named
Python helpers remain in `rtdsl.__all__`.

They must be classified as:

```text
legacy public exports / compatibility debt; not new v2.14.4 public generic API
```

The legacy public exports are:

```text
PreparedEmbreeRayjoinCdbPointLocation2D
PreparedOptixRayjoinCdbPointLocation2D
PreparedOptixRayjoinCdbPointLocationPoints2D
RAYJOIN_PAPER_TARGETS
RayJoinBoundedPlan
RayJoinFeatureServiceLayer
RayJoinPlan
RayJoinPublicAsset
chains_to_rayjoin_cdb_segments
download_rayjoin_sample
lower_to_rayjoin
pack_rayjoin_cdb_segments
prepare_rayjoin_cdb_point_location_2d_embree
prepare_rayjoin_cdb_point_location_2d_optix
rayjoin_bounded_plans
rayjoin_feature_service_layers
rayjoin_public_assets
```

Do not approve any wording that says these exports are absent, private, or not
public API names.  The correct claim is narrower: the **new v2.14.4 public
generic API surface** is generic, while these historical exports remain
compatibility debt.

## Documents To Review

Please review the following goal reports and their call-for-review files.

| Goal | Topic | Primary Report | Call For Review | Main Review Question |
|---|---|---|---|---|
| Goal5048 | Non-RayJoin proof for public Numba partner API | `history/internal_docs/goal5048_non_rayjoin_numba_partner_public_api_genericity_2026-07-06.md` | `history/internal_docs/call_for_review_goal5048_non_rayjoin_numba_partner_public_api_genericity_2026-07-06.md` | Is the public Numba partner API proven on a non-RayJoin shape, with POD smoke debt stated honestly? |
| Goal5049 | RayJoin app migration to public v2.14.4 surface | `history/internal_docs/goal5049_rayjoin_public_v2144_surface_migration_2026-07-06.md` | `history/internal_docs/call_for_review_goal5049_rayjoin_public_v2144_surface_migration_2026-07-06.md` | Does RayJoin use public `device_order_by` as an app without creating a hidden RayJoin system identity? |
| Goal5050 | Public/private boundary audit | `history/internal_docs/goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md` | `history/internal_docs/call_for_review_goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md` | Are public surfaces, legacy exports, grouped-reduce debt, and native naming debt classified honestly after the Goal5059 amendment? |
| Goal5051 | API consolidation closeout packet | `history/internal_docs/goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md` | `history/internal_docs/call_for_review_goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md` | Does the closeout correctly present v2.14.4 as API consolidation rather than a speedup or RayJoin release? |
| Goal5052 | Public API POD smoke runner | `history/internal_docs/goal5052_v2_14_4_public_api_pod_smoke_runner_2026-07-06.md` | `history/internal_docs/call_for_review_goal5052_v2_14_4_public_api_pod_smoke_runner_2026-07-06.md` | Is the strict POD smoke runner adequate and honest about what it proves? |
| Goal5053 | Release preflight gate | `history/internal_docs/goal5053_v2_14_4_release_preflight_gate_2026-07-06.md` | `history/internal_docs/call_for_review_goal5053_v2_14_4_release_preflight_gate_2026-07-06.md` | Does the release preflight correctly block public release until external review and strict POD smoke requirements are satisfied? |
| Goal5055 | Remote POD smoke launcher | `history/internal_docs/goal5055_v2_14_4_pod_smoke_remote_launcher_2026-07-06.md` | `history/internal_docs/call_for_review_goal5055_v2_14_4_pod_smoke_remote_launcher_2026-07-06.md` | Is the launcher mechanics acceptable, noting that earlier auth status is superseded by Goal5056/5057? |
| Goal5056 | Strict POD smoke result | `history/internal_docs/goal5056_v2_14_4_strict_pod_smoke_result_2026-07-06.md` | `history/internal_docs/call_for_review_goal5056_v2_14_4_strict_pod_smoke_result_2026-07-06.md` | Does strict POD smoke pass, and are its limits narrow enough? |
| Goal5057 | POD environment bootstrap | `history/internal_docs/goal5057_v2_14_4_pod_env_bootstrap_2026-07-06.md` | `history/internal_docs/call_for_review_goal5057_v2_14_4_pod_env_bootstrap_2026-07-06.md` | Is the CUDA/Numba POD environment fix repeatable and not dependent on user-side manual repair? |
| Goal5058 | Review debt content gate | `history/internal_docs/goal5058_v2_14_4_review_debt_content_gate_2026-07-06.md` | `history/internal_docs/call_for_review_goal5058_v2_14_4_review_debt_content_gate_2026-07-06.md` | Does preflight require real review content rather than accepting filenames or call-for-review stubs? |
| Goal5059 | Legacy RayJoin public export boundary amendment | `history/internal_docs/goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md` | `history/internal_docs/call_for_review_goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md` | Does the amendment correctly classify RayJoin-named Python exports as legacy public exports / compatibility debt? |
| Goal5060 | Substantive review gate hardening | `history/internal_docs/goal5060_v2_14_4_substantive_review_gate_hardening_2026-07-06.md` | `history/internal_docs/call_for_review_goal5060_v2_14_4_substantive_review_gate_hardening_2026-07-06.md` | Does the gate reject shallow template approvals while still accepting one substantive consolidated review? |
| Goal5061 | Consolidated review quality gate | `history/internal_docs/goal5061_v2_14_4_consolidated_review_quality_gate_2026-07-06.md` | `history/internal_docs/call_for_review_goal5061_v2_14_4_consolidated_review_quality_gate_2026-07-06.md` | Does the gate reject global padding / keyword-stuffing consolidated reviews while preserving the single-file review workflow? |
| Goal5062 | Dynamic RayJoin export disclosure gate | `history/internal_docs/goal5062_v2_14_4_dynamic_rayjoin_export_disclosure_gate_2026-07-06.md` | `history/internal_docs/call_for_review_goal5062_v2_14_4_dynamic_rayjoin_export_disclosure_gate_2026-07-06.md` | Does the gate dynamically enumerate and require disclosure of all RayJoin-named public exports? |

## Verification Evidence To Check

Local adjacent gate:

```text
Ran 68 tests in 4.375s
OK (skipped=1)
```

Strict POD smoke:

```text
history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json
overall_status: pass
strict: true
```

Current preflight JSON:

```text
history/internal_docs/goal5053_v2144_release_preflight_result.json
overall_status: blocked_by_release_gates
```

Important pass checks:

```text
required_goal_reports_present: pass
strict_pod_smoke: pass
public_surface_internal_leak_scan: pass
legacy_rayjoin_public_exports_disclosed: pass
external_review_debt: blocked
```

## Cross-Cutting Review Questions

Please answer these for the whole packet:

1. Does v2.14.4 correctly present itself as RTDL API consolidation, not a new
   RayJoin speedup release?
2. Are the new public API names generic and claim-bounded:
   `DeviceColumnBuffer`, `PreparedGeometrySession`, `device_order_by`,
   `NumbaPartnerContinuation`?
3. Is `device_group_by` correctly held back from the public v2.14.4 surface?
4. Is the public Numba partner API sufficiently proven for v2.14.4 with one
   non-RayJoin proof, while acknowledging that broader non-RayJoin proof remains
   future work?
5. Does RayJoin use the new public `device_order_by` surface as an app rather
   than bypassing into a private helper?
6. Are legacy RayJoin-named native symbols and Python exports disclosed honestly
   as compatibility/naming debt rather than hidden?
7. Does the packet avoid claiming true zero-copy, author parity, broad speedup,
   or RT traversal replacement?
8. Does the preflight gate correctly remain blocked until real external review
   files exist for all required goals?
8a. Does the preflight gate correctly reject shallow template approvals and
    expose `malformed_reasons`?
8b. Does the preflight gate correctly reject consolidated reviews whose goal
    sections are too short or whose only coverage comes from padding/keyword
    stuffing?
8c. Does the preflight gate dynamically detect all RayJoin-named public exports
    rather than trusting a static undercount?
9. Are Goal5055's earlier POD-auth status and Goal5053's earlier missing-POD
   status properly superseded by Goal5056/Goal5057 rather than treated as current
   blockers?
10. Is v2.14.4 safe to proceed to release-staging review after external review
    debt is retired, or are there blocking amendments still needed?

## Requested Output Format

For each goal, please provide:

```text
GoalXXXX:
verdict_label:
pass/fail/required_amendments:
blocking_findings:
non_blocking_notes:
```

For the whole packet, please provide one final verdict:

```text
approve_v2_14_4_all_review_debt_retirement
```

or:

```text
revise_v2_14_4_before_release_staging
```

## Expected Consequence

If the whole-packet verdict is approval, we should add the actual review files
under `history/internal_docs/` and rerun:

```text
scripts/goal5053_v2144_release_preflight.py
```

Only after that preflight stops blocking on `external_review_debt` can v2.14.4
move from internal staging toward user-facing release wording.
