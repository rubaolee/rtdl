# Goal3151: v2.8 Benchmark-App Front-Door Adoption Audit

Date: 2026-06-03

Status: `audit_complete_with_two_safe_migrations`

## Purpose

Goal3151 audits the ten promoted benchmark apps against the v2.8 rule: benchmark apps should use explicit, user-selected generic RTDL front doors when the generic contract already exists, while app/domain interpretation remains in the app layer. This is an internal adoption audit. It does not authorize a v2.8 release, public speedup wording, broad RT-core wording, whole-app speedup wording, paper reproduction wording, or true-zero-copy wording.

## Current Result

Two safe bespoke app continuations were migrated to the generic v2.8 segmented typed-stream front door:

- `spatial_rayjoin`: the legacy `run_rayjoin_v2_6_numba_compact_mask_preview(...)` helper is preserved, but now builds a schema-only typed stream and calls `execute_segmented_typed_stream_partner_continuation(..., operation="compact_mask_i64", partner="numba")`.
- `triangle_counting`: the legacy `run_triangle_counting_v2_6_numba_compact_mask_preview(...)` helper is preserved, but now uses the same v2.8 compact-mask front door.

Both wrappers still validate the input columns with the v2.6 neutral partner handoff before execution. The v2.8 adapter is used as a typed-stream schema/front-door contract over caller-supplied device columns; it does not claim that RTDL materializes a device-resident stream, and it does not claim true zero-copy.

The v2.8 front door also now accepts a generic optional `block_size` parameter for `compact_mask_i64`, so the legacy benchmark helper signatures keep their previous tuning knob without directly calling the lower Numba primitive from app code.

## Ten-App Adoption Matrix

| Benchmark app | Current v2.8 front-door status | Goal3151 operation | Legacy alias preserved | Remaining boundary |
| --- | --- | --- | --- | --- |
| `hausdorff_xhd` | Now uses the generic `directed_max_of_nearest_distance_2d_partner_columns` front-door alias for the exact directed max-nearest-distance continuation. | Migrated the recommended `partner_exact` app route away from the app-shaped adapter name. | `directed_hausdorff_2d_partner_columns` and legacy Hausdorff modes remain available. | Hausdorff interpretation stays in the benchmark app; the primitive contract is generic. |
| `spatial_rayjoin` | Row-stream compaction now routes through `build_segmented_typed_stream_adapter` and `execute_segmented_typed_stream_partner_continuation`. | Migrated safe Numba compact-mask path. | `run_rayjoin_v2_6_numba_compact_mask_preview` and `v2_6_numba_compact_mask_plan` remain. | RayJoin semantics, positive-hit interpretation, and paper policy stay in app code. No RayJoin performance claim. |
| `rt_dbscan` | Uses fixed-radius/core-summary primitives plus app-owned component continuation. | No safe migration in this goal. | Existing DBSCAN app modes remain. | Needs a generic typed adjacency/component continuation before app-owned CuPy component logic can be replaced. |
| `robot_collision` | Uses generic any-hit/collision flag primitives over prepared static scenes. | No migration needed. | Existing app wrappers remain. | Needs bounded flag/witness page evidence before richer partner continuation claims. |
| `contact_manifold` | Uses bounded witness collection with fail-closed overflow handling. | No migration needed. | Existing app wrappers remain. | Partner filtering requires new same-contract evidence before migration. |
| `raydb_style` | Already primitive-first for fused grouped reductions when the primitive exactly matches. | No migration needed. | Existing RayDB benchmark modes remain. | Unfused continuations still require explicit user partner choice; no hidden dispatch. |
| `barnes_hut` | Uses aggregate-frontier collect primitives and app-owned force-law continuation. | No safe migration in this goal. | Existing Barnes-Hut modes remain. | Needs typed aggregate-frontier streams plus grouped vector continuation before app-owned CuPy force logic can be replaced. |
| `librts_spatial_index` | Uses generic point/range query rows and no-regression evidence. | No migration needed. | Existing benchmark harness remains. | Prepared spatial-index residency remains a future validation target. |
| `rtnn` | Uses prepared fixed-radius ranked-summary primitives with batched request hardening. | No migration needed. | Existing RTNN modes remain. | Typed ranked-summary streams and prepared packed-column residency remain future hardening work. |
| `triangle_counting` | Row-stream compaction now routes through `build_segmented_typed_stream_adapter` and `execute_segmented_typed_stream_partner_continuation`. | Migrated safe Numba compact-mask path. | `run_triangle_counting_v2_6_numba_compact_mask_preview` and `v2_6_numba_compact_mask_plan` remain. | Scalar triangle count remains primitive-first; compact-mask is only for explicit witness/candidate-row interpretation. |

## Claim Boundary

- `release_authorized: False`
- `v2_8_release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `paper_reproduction_claim_authorized: False`
- `automatic_partner_selection_allowed: False`
- `app_specific_engine_logic_allowed: False`

## Validation

Local focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test tests.goal3147_compact_mask_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
Ran 33 tests in 1.110s
OK
```

Final local Goal3151 validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test tests.goal3147_compact_mask_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
Ran 39 tests in 1.111s
OK
```

External-review handoff:

- `docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3151_V2_8_BENCHMARK_FRONT_DOOR_ADOPTION_2026-06-03.md`

External-review result:

- Claude review: `docs/reviews/goal3152_claude_review_goal3151_v2_8_benchmark_front_door_adoption_2026-06-03.md`
- Verdict: `accept`
- Boundary: the review does not authorize v2.8 release, public speedup, RT-core speedup, true-zero-copy, or paper reproduction claims.

Pod validation:

```text
Pod SSH: ssh root@69.30.85.131 -p 22063 -i id_ed25519_rtdl_codex
GPU: NVIDIA A40
Driver: 570.211.01
Python: 3.12.3
Checkout: /root/rtdl_goal3151
Commit: fd419b940fa948178fa9afa0eb17b59654a986af
Command: PYTHONPATH=src:. python3 -m unittest tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test tests.goal3147_compact_mask_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
Ran 39 tests in 0.478s
OK
```
